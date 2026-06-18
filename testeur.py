import tkinter as tk
import random
import copy

# ---------- Dimensions ----------
GRID_SIZE = 25
CELL_SIZE = 20
R_MATURATION = 3        # cycles avant qu'un reboisement devienne fertile

# Probabilités réalistes
P_CROP_DIE_DRY = 0.6
P_CROP_DIE_WET = 0.2
P_DEGRADE_SURPATURAGE = 0.3
P_REGENERATION_WET = 0.2
P_DESERT_SPREAD = 0.8
P_REBOISEMENT_WET = 0.2    # <-- ajoutée
P_REBOISEMENT_DRY = 0.05

COLORS = {
    0: "#2ecc71",   # vert
    1: "#f1c40f",   # jaune
    2: "#e67e22",   # orange
    3: "#e74c3c",   # rouge
    4: "#3498db",   # bleu
    5: "#f5deb3",   # beige
}
STATES = ["Fertile (V)", "Culture (C)", "Dégradé (D)", "Désertifié (S)", "Reboisé (R)", "Vierge (X)"]

class RealisticDesertificationSim:
    def __init__(self, master):
        self.master = master
        master.title("Désertification réaliste – Nord-Cameroun")
        self.canvas_size = GRID_SIZE * CELL_SIZE

        # Grille initiale : toute vierge
        self.grid = [[5 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.age_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Contrôles
        self.running = False
        self.step_count = 0
        self.overgrazing = tk.BooleanVar(value=False)
        self.reforestation = tk.BooleanVar(value=True)
        self.brush_state = 3
        self.season_mode = tk.IntVar(value=0)

        self.build_interface()
        self.draw_grid()

    def build_interface(self):
        control = tk.Frame(self.master)
        control.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Button(control, text="Étape", command=self.step).pack(side=tk.LEFT, padx=2)
        self.btn_run = tk.Button(control, text="Lancer", command=self.toggle_run)
        self.btn_run.pack(side=tk.LEFT, padx=2)
        tk.Button(control, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=2)

        # Configurations prédéfinies
        tk.Button(control, text="Zone témoin (N désert)", command=self.preset_normal).pack(side=tk.LEFT, padx=5)
        tk.Button(control, text="Crise sévère", command=self.preset_crisis).pack(side=tk.LEFT, padx=5)
        tk.Button(control, text="Espoir (reboisement)", command=self.preset_reforestation).pack(side=tk.LEFT, padx=5)

        # Options
        tk.Checkbutton(control, text="Surpâturage", variable=self.overgrazing).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(control, text="Reboisement actif", variable=self.reforestation).pack(side=tk.LEFT)

        # Saisons
        season_frame = tk.Frame(control)
        season_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(season_frame, text="Saison:").pack(side=tk.LEFT)
        tk.Radiobutton(season_frame, text="Auto", variable=self.season_mode, value=0).pack(side=tk.LEFT)
        tk.Radiobutton(season_frame, text="Sèche forcée", variable=self.season_mode, value=1).pack(side=tk.LEFT)
        tk.Radiobutton(season_frame, text="Pluies forcées", variable=self.season_mode, value=2).pack(side=tk.LEFT)

        self.season_label = tk.Label(control, text="  Saison : --", width=25)
        self.season_label.pack(side=tk.LEFT, padx=10)

        # Palette de peinture
        palette = tk.Frame(self.master)
        palette.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        tk.Label(palette, text="Peindre :").pack(side=tk.LEFT)
        for idx, name in enumerate(STATES):
            color = COLORS[idx]
            fg = "white" if idx in (2,3,4) else "black"
            tk.Button(palette, text=name, bg=color, fg=fg,
                      command=lambda i=idx: self.set_brush(i)).pack(side=tk.LEFT, padx=2)

        self.canvas = tk.Canvas(self.master, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_click)

    def set_brush(self, idx):
        self.brush_state = idx

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.grid[row][col] = self.brush_state
            if self.brush_state == 4:
                self.age_grid[row][col] = R_MATURATION
            else:
                self.age_grid[row][col] = 0
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1, y1 = j * CELL_SIZE, i * CELL_SIZE
                state = self.grid[i][j]
                color = COLORS[state]
                self.canvas.create_rectangle(x1, y1, x1+CELL_SIZE, y1+CELL_SIZE,
                                             fill=color, outline="#dddddd")
                if state == 4 and self.age_grid[i][j] > 0:
                    self.canvas.create_text(x1+CELL_SIZE//2, y1+CELL_SIZE//2,
                                            text=str(self.age_grid[i][j]),
                                            fill="white", font=("Arial", 7))

    # ---------- Configurations prédéfinies ----------
    def preset_normal(self):
        self.grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for i in range(GRID_SIZE):
            if i < GRID_SIZE//4:
                state = 3
            elif i < GRID_SIZE//2:
                state = 2
            elif i < 3*GRID_SIZE//4:
                state = 1 if random.random() < 0.7 else 0
            else:
                state = 0
            for j in range(GRID_SIZE):
                self.grid[i][j] = state
        self.age_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.draw_grid()

    def preset_crisis(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i < 3*GRID_SIZE//4:
                    self.grid[i][j] = 3
                else:
                    self.grid[i][j] = 2 if random.random() < 0.5 else 0
        self.age_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.draw_grid()

    def preset_reforestation(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i < GRID_SIZE//2:
                    self.grid[i][j] = 3
                else:
                    self.grid[i][j] = 0
        for i in range(GRID_SIZE//4, GRID_SIZE//2, 2):
            for j in range(GRID_SIZE):
                self.grid[i][j] = 4
                self.age_grid[i][j] = R_MATURATION
        self.draw_grid()

    # ---------- Contrôle de la simulation ----------
    def toggle_run(self):
        self.running = not self.running
        self.btn_run.config(text="Pause" if self.running else "Lancer")
        if self.running:
            self.run()

    def run(self):
        if not self.running:
            return
        self.step()
        self.master.after(400, self.run)

    def reset(self):
        self.running = False
        self.btn_run.config(text="Lancer")
        self.step_count = 0
        self.grid = [[5]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.age_grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.draw_grid()
        self.season_label.config(text="Saison : --")

    # ---------- Règles de transition réalistes ----------
    def step(self):
        self.step_count += 1

        mode = self.season_mode.get()
        if mode == 1:
            dry = True
            season_name = "Sèche (forcée)"
        elif mode == 2:
            dry = False
            season_name = "Pluies (forcées)"
        else:
            dry = (self.step_count // 6) % 2 == 0
            season_name = "Sèche" if dry else "Pluies"
        self.season_label.config(text=f"Saison : {season_name} | pas {self.step_count}")

        new_grid = copy.deepcopy(self.grid)
        new_age = copy.deepcopy(self.age_grid)

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell = self.grid[i][j]
                nb_desert = self.count_neighbors(i, j, 3)
                nb_fertile = self.count_neighbors(i, j, 0)
                nb_reboise = self.count_neighbors(i, j, 4)
                age = self.age_grid[i][j] if cell == 4 else 0

                next_state = cell
                next_age_val = 0

                if cell == 5:  # Vierge
                    if nb_desert >= 4 and random.random() < 0.1:
                        next_state = 2
                    elif random.random() < 0.01:
                        next_state = 1

                elif cell == 0:  # Fertile
                    if nb_desert >= 3 and random.random() < (0.7 if dry else 0.3):
                        next_state = 2
                    elif random.random() < 0.05:
                        next_state = 1

                elif cell == 1:  # Culture
                    degrade = False
                    if dry:
                        if random.random() < P_CROP_DIE_DRY:
                            degrade = True
                    else:
                        if nb_desert >= 2 and random.random() < P_CROP_DIE_WET:
                            degrade = True
                    if self.overgrazing.get() and random.random() < P_DEGRADE_SURPATURAGE:
                        degrade = True
                    if degrade:
                        next_state = 2

                elif cell == 2:  # Dégradé
                    if not dry and nb_fertile >= 3 and random.random() < P_REGENERATION_WET:
                        next_state = 0
                    elif nb_desert >= 2 and random.random() < P_DESERT_SPREAD:
                        next_state = 3
                    elif dry and nb_desert >= 1 and random.random() < 0.5:
                        next_state = 3

                elif cell == 3:  # Désertifié
                    if self.reforestation.get():
                        prob = P_REBOISEMENT_WET if not dry else P_REBOISEMENT_DRY
                        if random.random() < prob:
                            next_state = 4
                            next_age_val = R_MATURATION

                elif cell == 4:  # Reboisé
                    if age > 1:
                        next_state = 4
                        next_age_val = age - 1
                    else:
                        if nb_reboise + nb_fertile >= 3:
                            next_state = 0
                        else:
                            next_state = 4
                            next_age_val = age  # stagne

                new_grid[i][j] = next_state
                new_age[i][j] = next_age_val

        self.grid = new_grid
        self.age_grid = new_age
        self.draw_grid()

    def count_neighbors(self, row, col, target_state):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = (row + dr) % GRID_SIZE
                nc = (col + dc) % GRID_SIZE
                if self.grid[nr][nc] == target_state:
                    count += 1
        return count

if __name__ == "__main__":
    root = tk.Tk()
    app = RealisticDesertificationSim(root)
    root.mainloop()