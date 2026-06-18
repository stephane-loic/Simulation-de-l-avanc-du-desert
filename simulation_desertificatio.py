"""
=============================================================
  SIMULATION DE LA DÉSERTIFICATION — ZONE AGRICOLE CAMEROUNAISE
  Inspiré de la réalité du Sahel camerounais :
  Adamaoua, Nord, Extrême-Nord

  Automate cellulaire · Voisinage de Moore (8 voisins)
  Grille vierge au départ — l'utilisateur peint ses zones.

  États inspirés du terrain camerounais :
    0  Forêt / Savane dense     — végétation naturelle protectrice
    1  Sol Fertile               — bon sol, humidité suffisante
    2  Champ de Maïs             — culture active (maïs, mil, sorgho)
    3  Champ de Coton            — culture de rente exigeante
    4  Sol Dégradé               — perte de fertilité, fissures
    5  Sol Désertifié            — sable, latérite, rien ne pousse
    6  Zone Reboisée             — eucalyptus, neem, reforestation
    7  Pâturage / Élevage        — zone de transhumance, troupeaux
    8  Vierge / Non défini       — pas encore attribué par l'utilisateur

  Règles inspirées de la réalité camerounaise :
  - Maïs sur sol dégradé en saison sèche → récolte perdue (→ Dégradé encore plus)
  - Coton épuise le sol rapidement
  - Surpâturage détruit la végétation et accélère l'érosion
  - La forêt protège les terres voisines
  - Saison des pluies : régénération possible si entourage favorable
  - Saison sèche + harmattan : propagation rapide du désert
=============================================================
"""

import tkinter as tk
import random
import copy

# ─────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────
GRID_SIZE     = 22
CELL_SIZE     = 24
SEASON_LENGTH = 6    # itérations par saison en mode auto
R_MATURATION  = 5    # cycles pour qu'une Zone Reboisée devienne Fertile

# États
FORET    = 0
FERTILE  = 1
MAÏS     = 2
COTON    = 3
DEGRADE  = 4
DESERT   = 5
REBOISE  = 6
PATURAGE = 7
VIERGE   = 8

COLORS = {
    FORET:    "#1B5E20",   # vert très foncé   — Forêt/Savane
    FERTILE:  "#4CAF50",   # vert moyen         — Sol Fertile
    MAÏS:     "#FFD600",   # jaune vif          — Maïs/Mil/Sorgho
    COTON:    "#FFFFFF",   # blanc              — Coton
    DEGRADE:  "#FF8C00",   # orange             — Sol Dégradé
    DESERT:   "#B22222",   # rouge brique       — Désertifié
    REBOISE:  "#1565C0",   # bleu               — Reboisé
    PATURAGE: "#A5D6A7",   # vert clair         — Pâturage
    VIERGE:   "#F5DEB3",   # beige sable        — Vierge
}

NOMS = {
    FORET:    "Forêt/Savane",
    FERTILE:  "Sol Fertile",
    MAÏS:     "Champ Maïs/Mil",
    COTON:    "Champ Coton",
    DEGRADE:  "Sol Dégradé",
    DESERT:   "Désertifié",
    REBOISE:  "Zone Reboisée",
    PATURAGE: "Pâturage/Élevage",
    VIERGE:   "Vierge",
}

# ─────────────────────────────────────────────
#  CONFIGURATIONS PRÉDÉFINIES
#  Chaque scénario remplit la grille avec un
#  paysage réaliste camerounais.
# ─────────────────────────────────────────────

def scenario_village_nord():
    """Village typique du Nord-Cameroun :
    centre fertile avec champs, entouré de dégradation."""
    g = [[VIERGE]*GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            di = abs(i - GRID_SIZE//2)
            dj = abs(j - GRID_SIZE//2)
            dist = max(di, dj)
            if dist <= 3:
                g[i][j] = FERTILE
            elif dist <= 5:
                g[i][j] = MAÏS if random.random() < 0.6 else COTON
            elif dist <= 8:
                g[i][j] = DEGRADE if random.random() < 0.5 else PATURAGE
            elif dist <= 10:
                g[i][j] = DEGRADE
            else:
                g[i][j] = DESERT if random.random() < 0.4 else DEGRADE
    # Quelques arbres isolés
    for _ in range(6):
        ri, rj = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        g[ri][rj] = FORET
    return g

def scenario_front_desertique():
    """Front désertique venant du nord (haut de la grille)
    comme dans l'Extrême-Nord Cameroun."""
    g = [[VIERGE]*GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if i < 5:
                g[i][j] = DESERT
            elif i < 8:
                g[i][j] = DESERT if random.random() < 0.7 else DEGRADE
            elif i < 11:
                g[i][j] = DEGRADE if random.random() < 0.8 else PATURAGE
            elif i < 15:
                g[i][j] = MAÏS if random.random() < 0.5 else FERTILE
            else:
                g[i][j] = FERTILE if random.random() < 0.6 else FORET
    return g

def scenario_surpaturage():
    """Zone de transhumance de l'Adamaoua :
    pâturages dégradés par les troupeaux de zébus."""
    g = [[PATURAGE]*GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            r = random.random()
            if r < 0.25:
                g[i][j] = DEGRADE
            elif r < 0.40:
                g[i][j] = FERTILE
            elif r < 0.50:
                g[i][j] = FORET
            elif r < 0.55:
                g[i][j] = DESERT
    # Axe de transhumance central très dégradé
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE//2 - 1, GRID_SIZE//2 + 2):
            if random.random() < 0.7:
                g[i][j] = DEGRADE
    return g

def scenario_reboisement():
    """Programme de reboisement (neem, eucalyptus) :
    zones désertifiées avec intervention humaine."""
    g = [[DESERT]*GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            r = random.random()
            if r < 0.15:
                g[i][j] = REBOISE
            elif r < 0.25:
                g[i][j] = DEGRADE
            elif r < 0.30:
                g[i][j] = FERTILE
    # Bande fertile au sud (fleuve Bénoué)
    for i in range(GRID_SIZE-4, GRID_SIZE):
        for j in range(GRID_SIZE):
            g[i][j] = FERTILE if random.random() < 0.7 else MAÏS
    return g

def scenario_mais_sec():
    """Le scénario du maïs en saison sèche :
    champs de maïs plantés sur sol dégradé sans eau — voués à l'échec."""
    g = [[DEGRADE]*GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            r = random.random()
            if r < 0.45:
                g[i][j] = MAÏS    # maïs semé sur sol pauvre
            elif r < 0.55:
                g[i][j] = FERTILE
            elif r < 0.60:
                g[i][j] = DESERT
    return g

SCENARIOS = {
    "Village Nord-Cameroun":      scenario_village_nord,
    "Front désertique (Extrême-Nord)": scenario_front_desertique,
    "Surpâturage Adamaoua":       scenario_surpaturage,
    "Programme reboisement":      scenario_reboisement,
    "Maïs en saison sèche":       scenario_mais_sec,
}


# ─────────────────────────────────────────────
#  RÈGLES DE TRANSITION
#  Inspirées de la réalité camerounaise
# ─────────────────────────────────────────────

def compter_voisins(grid, r, c, etat):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = (r + dr) % GRID_SIZE
            nc = (c + dc) % GRID_SIZE
            if grid[nr][nc] == etat:
                count += 1
    return count

def compter_voisins_multi(grid, r, c, etats):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = (r + dr) % GRID_SIZE
            nc = (c + dc) % GRID_SIZE
            if grid[nr][nc] in etats:
                count += 1
    return count

def transition(grid, age_grid, dry, surpaturage):
    new_g   = copy.deepcopy(grid)
    new_age = copy.deepcopy(age_grid)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cur = grid[i][j]
            age = age_grid[i][j]
            rnd = random.random()

            # Compter les voisins utiles
            nb_desert   = compter_voisins(grid, i, j, DESERT)
            nb_degrade  = compter_voisins(grid, i, j, DEGRADE)
            nb_foret    = compter_voisins(grid, i, j, FORET)
            nb_fertile  = compter_voisins(grid, i, j, FERTILE)
            nb_reboise  = compter_voisins(grid, i, j, REBOISE)
            nb_paturage = compter_voisins(grid, i, j, PATURAGE)
            nb_protege  = nb_foret + nb_reboise  # protection naturelle

            ns  = cur   # next state
            na  = age   # next age

            # ══ VIERGE ══════════════════════════════════════════════
            # La terre vierge se dégrade si le désert approche
            if cur == VIERGE:
                if nb_desert >= 1:
                    p = 0.80 if dry else 0.30
                    if rnd < p:
                        ns = DEGRADE
                elif nb_degrade >= 3:
                    p = 0.40 if dry else 0.10
                    if rnd < p:
                        ns = DEGRADE

            # ══ FORÊT / SAVANE ══════════════════════════════════════
            # La forêt résiste bien, mais cède sous déforestation + sécheresse
            elif cur == FORET:
                if dry and nb_desert >= 3 and nb_protege == 0:
                    if rnd < 0.20:
                        ns = DEGRADE   # feux de brousse, sécheresse extrême
                elif nb_desert >= 5:
                    if rnd < 0.35:
                        ns = DEGRADE
                # La forêt se régénère spontanément si entourage favorable
                elif not dry and nb_fertile >= 3 and rnd < 0.05:
                    pass  # reste forêt, se renforce

            # ══ SOL FERTILE ═════════════════════════════════════════
            # Un sol fertile peut être mis en culture ou se dégrader
            elif cur == FERTILE:
                if dry and nb_desert >= 1 and nb_protege == 0:
                    # Saison sèche + désert proche + aucune protection → dégradation
                    ns = DEGRADE
                elif dry and nb_degrade >= 4:
                    if rnd < 0.50:
                        ns = DEGRADE
                elif nb_desert >= 3:
                    if rnd < 0.60:
                        ns = DEGRADE
                elif rnd < 0.06:
                    ns = MAÏS     # agriculteur sème du maïs ou mil
                elif rnd < 0.09:
                    ns = COTON    # agriculteur sème du coton

            # ══ CHAMP DE MAÏS (mil, sorgho) ═════════════════════════
            # Règle clé : maïs sur sol dégradé en saison sèche → mort de la récolte
            elif cur == MAÏS:
                sol_sous_jacent_degrade = (nb_degrade >= 5)  # entouré de dégradé
                if dry:
                    if sol_sous_jacent_degrade or nb_desert >= 1:
                        # Maïs semé sur sol pauvre en saison sèche → récolte perdue
                        # Le sol s'épuise encore plus
                        ns = DEGRADE
                    elif nb_protege == 0 and nb_desert == 0:
                        # Maïs sans protection, sans désert proche : risque moyen
                        if rnd < 0.30:
                            ns = DEGRADE
                    else:
                        # Forêt ou reboisé autour : microlimat protecteur
                        if rnd < 0.10:
                            ns = DEGRADE
                else:
                    # Saison des pluies : le maïs peut prospérer
                    if nb_desert >= 2 and nb_protege == 0:
                        if rnd < 0.25:
                            ns = DEGRADE
                    elif rnd < 0.08:
                        ns = FERTILE  # jachère après récolte → sol se repose

            # ══ CHAMP DE COTON ══════════════════════════════════════
            # Le coton épuise rapidement le sol (réalité de l'Adamaoua)
            elif cur == COTON:
                if dry:
                    # Coton en saison sèche → catastrophe certaine
                    if rnd < 0.70:
                        ns = DEGRADE
                else:
                    # Saison des pluies : le coton tient mais épuise le sol
                    if rnd < 0.25:
                        ns = DEGRADE   # épuisement du sol
                    elif nb_desert >= 1:
                        if rnd < 0.40:
                            ns = DEGRADE

            # ══ SOL DÉGRADÉ ═════════════════════════════════════════
            # Cœur de la règle : dégradé entouré de désert en saison sèche → désert
            elif cur == DEGRADE:
                if dry:
                    if nb_desert >= 1:
                        # EN SAISON SÈCHE : 1 seul voisin désertifié suffit
                        # → le dégradé bascule CERTAINEMENT en désert
                        # (comme dans la réalité : l'harmattan finit le travail)
                        ns = DESERT
                    elif nb_degrade >= 6 and nb_protege == 0:
                        # Entouré uniquement de dégradés, aucune protection
                        if rnd < 0.55:
                            ns = DESERT
                    elif surpaturage and nb_paturage >= 2:
                        # Surpâturage accélère la dégradation vers désert
                        if rnd < 0.45:
                            ns = DESERT
                else:
                    # Saison des pluies : chance de régénération
                    if nb_desert >= 3:
                        if rnd < 0.30:
                            ns = DESERT   # trop entouré pour se régénérer
                    elif nb_protege >= 2 and nb_desert == 0:
                        # Forêt/reboisement autour → régénération du sol
                        if rnd < 0.35:
                            ns = FERTILE
                    elif nb_fertile >= 3 and nb_desert == 0:
                        if rnd < 0.20:
                            ns = FERTILE

            # ══ SOL DÉSERTIFIÉ ══════════════════════════════════════
            # Seule intervention humaine (reboisement) peut le sauver
            elif cur == DESERT:
                if not dry and nb_reboise >= 3 and rnd < 0.12:
                    ns  = REBOISE
                    na  = R_MATURATION
                elif not dry and nb_foret >= 3 and rnd < 0.08:
                    ns = DEGRADE   # très lente régénération naturelle
                elif rnd < 0.05:
                    # Intervention humaine rare (programme gouvernemental)
                    ns = REBOISE
                    na = R_MATURATION

            # ══ ZONE REBOISÉE (neem, eucalyptus) ════════════════════
            # Maturation progressive → devient Fertile puis protège ses voisins
            elif cur == REBOISE:
                if age > 1:
                    na = age - 1   # maturation en cours
                else:
                    # Arrivé à maturité → sol fertile
                    ns = FERTILE
                    na = 0
                # Mais peut céder sous harmattan extrême
                if dry and nb_desert >= 5 and rnd < 0.15:
                    ns = DEGRADE
                    na = 0

            # ══ PÂTURAGE / ÉLEVAGE ══════════════════════════════════
            # Réalité Adamaoua : transhumance des zébus dégrade les terres
            elif cur == PATURAGE:
                if surpaturage:
                    # Surpâturage actif : dégradation quasi-certaine en saison sèche
                    p = 0.65 if dry else 0.25
                    if rnd < p:
                        ns = DEGRADE
                else:
                    # Pâturage normal
                    if dry and nb_desert >= 2:
                        if rnd < 0.40:
                            ns = DEGRADE
                    elif not dry and nb_fertile >= 3 and rnd < 0.10:
                        ns = FERTILE   # jachère naturelle
                    elif nb_foret >= 2 and rnd < 0.05:
                        ns = FERTILE

            new_g[i][j]   = ns
            new_age[i][j] = na

    return new_g, new_age


# ─────────────────────────────────────────────
#  INTERFACE GRAPHIQUE
# ─────────────────────────────────────────────

class DesertificationSim:
    def __init__(self, master):
        self.master = master
        master.title("Désertification — Zone Agricole Camerounaise")
        master.configure(bg="#1C1C1C")

        self.grid       = [[VIERGE]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.age_grid   = [[0]*GRID_SIZE      for _ in range(GRID_SIZE)]
        self.running    = False
        self.step_num   = 0
        self.brush      = VIERGE
        self.season_mode = tk.IntVar(value=0)
        self.surpaturage = tk.BooleanVar(value=False)

        self._build()
        self.draw_grid()

    # ══════════════════════════════════════════
    #  INTERFACE
    # ══════════════════════════════════════════

    def _build(self):
        # ── Titre ──
        tk.Label(self.master,
                 text="🌍  Simulation Désertification — Cameroun (Adamaoua · Nord · Extrême-Nord)",
                 bg="#1C1C1C", fg="white", font=("Helvetica", 11, "bold")).pack(pady=(8,2))
        tk.Label(self.master,
                 text="Automate cellulaire · Voisinage de Moore · Règles inspirées du terrain camerounais",
                 bg="#1C1C1C", fg="#555555", font=("Helvetica", 8)).pack(pady=(0,4))

        # ── Palette ──
        pal = tk.Frame(self.master, bg="#242424", padx=6, pady=6)
        pal.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(pal, text="① Peindre :", bg="#242424", fg="#AAAAAA",
                 font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0,6))

        ordre = [FORET, FERTILE, MAÏS, COTON, DEGRADE, DESERT, REBOISE, PATURAGE, VIERGE]
        for idx in ordre:
            fg = "white" if idx in (FORET, DESERT, REBOISE, DEGRADE, COTON) else "black"
            if idx == COTON:
                fg = "#333333"
            tk.Button(pal, text=NOMS[idx], bg=COLORS[idx], fg=fg,
                      font=("Helvetica", 8, "bold"),
                      relief=tk.FLAT, padx=5, pady=3,
                      command=lambda i=idx: self._set_brush(i)
                      ).pack(side=tk.LEFT, padx=2)

        self.lbl_brush = tk.Label(pal, text="Outil : Vierge",
                                   bg="#242424", fg="#F5DEB3",
                                   font=("Helvetica", 9, "bold"))
        self.lbl_brush.pack(side=tk.LEFT, padx=(10,0))

        # ── Scénarios prédéfinis ──
        scen = tk.Frame(self.master, bg="#2A2A2A", padx=6, pady=5)
        scen.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(scen, text="② Scénario :", bg="#2A2A2A", fg="#AAAAAA",
                 font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0,6))
        for nom, fn in SCENARIOS.items():
            tk.Button(scen, text=nom, bg="#37474F", fg="#CCCCCC",
                      font=("Helvetica", 8), relief=tk.FLAT, padx=6, pady=3,
                      command=lambda f=fn: self._load_scenario(f)
                      ).pack(side=tk.LEFT, padx=2)

        # ── Saison + surpâturage ──
        sais = tk.Frame(self.master, bg="#242424", padx=6, pady=5)
        sais.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(sais, text="③ Saison :", bg="#242424", fg="#AAAAAA",
                 font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0,6))
        for txt, val in [("Auto", 0), ("☀  Forcer Sèche", 1), ("🌧  Forcer Pluvieuse", 2)]:
            tk.Radiobutton(sais, text=txt, variable=self.season_mode, value=val,
                           bg="#242424", fg="#CCCCCC", selectcolor="#444",
                           activebackground="#242424", activeforeground="white",
                           font=("Helvetica", 9)).pack(side=tk.LEFT, padx=4)

        tk.Checkbutton(sais, text="🐄 Surpâturage (transhumance)",
                       variable=self.surpaturage,
                       bg="#242424", fg="#F9A825",
                       selectcolor="#444",
                       activebackground="#242424", activeforeground="#F9A825",
                       font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(14,0))

        self.lbl_saison = tk.Label(sais, text="Saison : —",
                                    bg="#242424", fg="#5C9BD6",
                                    font=("Helvetica", 9, "bold"), width=24)
        self.lbl_saison.pack(side=tk.LEFT, padx=(10,0))

        # ── Boutons simulation ──
        btn = tk.Frame(self.master, bg="#1C1C1C", pady=6)
        btn.pack(fill=tk.X, padx=8)
        tk.Label(btn, text="④ Simulation :", bg="#1C1C1C", fg="#AAAAAA",
                 font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0,8))

        self.btn_run = tk.Button(btn, text="▶   DÉMARRER",
                                  command=self._toggle,
                                  bg="#2E7D32", fg="white",
                                  font=("Helvetica", 11, "bold"),
                                  relief=tk.FLAT, padx=18, pady=6, cursor="hand2")
        self.btn_run.pack(side=tk.LEFT, padx=4)

        tk.Button(btn, text="⏭  Étape", command=self.step,
                  bg="#37474F", fg="white", font=("Helvetica", 10),
                  relief=tk.FLAT, padx=12, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=4)

        tk.Button(btn, text="↺  Réinitialiser", command=self._reset,
                  bg="#4A148C", fg="white", font=("Helvetica", 10),
                  relief=tk.FLAT, padx=12, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=4)

        self.lbl_step = tk.Label(btn, text="Itération : 0",
                                  bg="#1C1C1C", fg="white",
                                  font=("Helvetica", 10, "bold"))
        self.lbl_step.pack(side=tk.LEFT, padx=(14,0))

        # ── Canvas ──
        cadre = tk.Frame(self.master, bg="#444", padx=1, pady=1)
        cadre.pack(padx=8, pady=(4,4))
        self.canvas = tk.Canvas(cadre,
                                 width=GRID_SIZE*CELL_SIZE,
                                 height=GRID_SIZE*CELL_SIZE,
                                 highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>",  self._click)
        self.canvas.bind("<B1-Motion>", self._drag)

        # ── Légende compacte ──
        leg = tk.Frame(self.master, bg="#1C1C1C", pady=3)
        leg.pack(fill=tk.X, padx=8, pady=(0,6))
        tk.Label(leg, text="Règles clés :", bg="#1C1C1C", fg="#555",
                 font=("Courier", 8, "bold")).pack(side=tk.LEFT, padx=(0,6))
        regles = [
            "Maïs+sol dégradé+saison sèche → récolte perdue",
            "Coton épuise le sol",
            "Dégradé+désert voisin+saison sèche → Désert (certain)",
            "Forêt/Reboisé = protection des voisins",
            "Surpâturage zébus → Dégradé rapide",
        ]
        for r in regles:
            tk.Label(leg, text=f"  • {r}", bg="#1C1C1C", fg="#444",
                     font=("Courier", 7)).pack(side=tk.LEFT)

    # ══════════════════════════════════════════
    #  DESSIN
    # ══════════════════════════════════════════

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1, y1 = j*CELL_SIZE, i*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                st = self.grid[i][j]
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                              fill=COLORS[st],
                                              outline="#2A2A2A", width=1)
                # Compteur de maturité sur les reboisés
                if st == REBOISE and self.age_grid[i][j] > 0:
                    self.canvas.create_text(x1+CELL_SIZE//2, y1+CELL_SIZE//2,
                                            text=str(self.age_grid[i][j]),
                                            fill="white", font=("Arial", 7, "bold"))

    # ══════════════════════════════════════════
    #  INTERACTIONS
    # ══════════════════════════════════════════

    def _set_brush(self, idx):
        self.brush = idx
        self.lbl_brush.config(text=f"Outil : {NOMS[idx]}", fg=COLORS[idx])

    def _paint(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            self.grid[r][c] = self.brush
            self.age_grid[r][c] = R_MATURATION if self.brush == REBOISE else 0
            self.draw_grid()

    def _click(self, e): self._paint(e)
    def _drag(self, e):  self._paint(e)

    def _load_scenario(self, fn):
        self.running = False
        self.btn_run.config(text="▶   DÉMARRER", bg="#2E7D32")
        self.step_num = 0
        self.lbl_step.config(text="Itération : 0")
        self.lbl_saison.config(text="Saison : —", fg="#5C9BD6")
        self.grid     = fn()
        self.age_grid = [[R_MATURATION if self.grid[i][j]==REBOISE else 0
                          for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        self.draw_grid()

    # ══════════════════════════════════════════
    #  SIMULATION
    # ══════════════════════════════════════════

    def _toggle(self):
        self.running = not self.running
        if self.running:
            self.btn_run.config(text="⏸   PAUSE", bg="#E65100")
            self._loop()
        else:
            self.btn_run.config(text="▶   DÉMARRER", bg="#2E7D32")

    def _loop(self):
        if not self.running:
            return
        self.step()
        self.master.after(300, self._loop)

    def _reset(self):
        self.running = False
        self.btn_run.config(text="▶   DÉMARRER", bg="#2E7D32")
        self.step_num = 0
        self.grid     = [[VIERGE]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.age_grid = [[0]*GRID_SIZE      for _ in range(GRID_SIZE)]
        self.lbl_step.config(text="Itération : 0")
        self.lbl_saison.config(text="Saison : —", fg="#5C9BD6")
        self.draw_grid()

    def step(self):
        self.step_num += 1

        mode = self.season_mode.get()
        if mode == 1:
            dry, txt, fg = True,  "☀  Sèche (forcée)",    "#F9A825"
        elif mode == 2:
            dry, txt, fg = False, "🌧  Pluvieuse (forcée)", "#5C9BD6"
        else:
            dry = (self.step_num // SEASON_LENGTH) % 2 == 0
            txt = "☀  Sèche (auto)" if dry else "🌧  Pluvieuse (auto)"
            fg  = "#F9A825" if dry else "#5C9BD6"

        self.lbl_saison.config(text=f"Saison : {txt}", fg=fg)
        self.lbl_step.config(text=f"Itération : {self.step_num}")

        self.grid, self.age_grid = transition(
            self.grid, self.age_grid, dry, self.surpaturage.get()
        )
        self.draw_grid()


# ─────────────────────────────────────────────
#  LANCEMENT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = DesertificationSim(root)
    root.mainloop()
