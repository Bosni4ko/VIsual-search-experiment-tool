import tkinter as tk
from tkinter import ttk, filedialog
from experiment_session_start import show_experiment_session_start
import os


def show_launch_screen(app):
    app.clear_screen()
    app.root.configure(bg="#f0f0f0")

    # === Persisted user-added experiments ===
    # Initialize on first call
    if not hasattr(app, 'added_experiments'):
        # dict mapping exp_name -> full_path
        app.added_experiments = {}

    # === Top Back Arrow ===
    top_frame = tk.Frame(app.root, bg="#f0f0f0")
    top_frame.pack(fill="x", pady=(10, 0))

    back_button = ttk.Button(top_frame, text="←", command=app.show_main_screen, width=3)
    back_button.pack(side="left", padx=10)

    # === Header ===
    header_frame = tk.Frame(app.root, bg="#f0f0f0")
    header_frame.pack(pady=20)

    title_label = ttk.Label(header_frame, text="Launch Visual Search Experiment", anchor="center", font=("Segoe UI", 24, "bold"))
    title_label.pack(pady=(0, 10))

    # === Folder Entry + Browse + Add ===
    folder_frame = tk.Frame(app.root, bg="#f0f0f0")
    folder_frame.pack(pady=10)

    folder_entry = ttk.Entry(folder_frame, width=50)
    folder_entry.pack(side="left", padx=5)

    # Store {experiment_name: full_path}
    loaded_experiments = {}
    experiment_labels = {}  # Store label widgets to allow highlighting
    selected_experiment = tk.StringVar(value="")  # Selected experiment name

    def browse_folder():
        path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Experiment Folder")
        if path:
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, path)

    def add_experiment():
        # --- If the "No experiments found" label is there, remove it ---
        if hasattr(app, 'no_experiments_label'):
            app.no_experiments_label.destroy()
            delattr(app, 'no_experiments_label')

        path = folder_entry.get().strip()
        if not path or not os.path.isdir(path):
            print("Invalid folder selected.")
            return

        exp_name = os.path.basename(path.rstrip("/\\"))

        if exp_name in loaded_experiments:
            print(f"Experiment '{exp_name}' already listed.")
            return

        loaded_experiments[exp_name] = path
        app.added_experiments[exp_name] = path
        create_experiment_label(exp_name)

    browse_button = ttk.Button(folder_frame, text="Browse", command=browse_folder)
    browse_button.pack(side="left", padx=5)

    add_button = ttk.Button(folder_frame, text="Add", command=add_experiment)
    add_button.pack(side="left", padx=5)

    # === Experiments List with Scroll ===
    experiments_frame = tk.Frame(app.root, bg="#f0f0f0", bd=2, relief="groove")
    experiments_frame.pack(padx=20, pady=10, fill="both", expand=True)

    canvas = tk.Canvas(experiments_frame, bg="#ffffff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(experiments_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#ffffff")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mousewheel scroll
    def _on_mousewheel(event):
        bbox = canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            view_height = canvas.winfo_height()
            if content_height > view_height:
                if event.delta:
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                else:
                    if event.num == 5:
                        canvas.yview_scroll(1, "units")
                    elif event.num == 4:
                        canvas.yview_scroll(-1, "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # --- Function to create experiment label ---
    def create_experiment_label(exp_name):
        lbl = ttk.Label(scrollable_frame, text=exp_name, font=("Segoe UI", 14), cursor="hand2")
        lbl.pack(pady=5, anchor="w", padx=10)

        def on_click(event):
            select_experiment(exp_name)

        lbl.bind("<Button-1>", on_click)
        experiment_labels[exp_name] = lbl

    # --- Handle experiment selection ---
    def select_experiment(exp_name):
        # Deselect previous
        for name, label in experiment_labels.items():
            label.configure(background="#ffffff")

        # Highlight selected
        experiment_labels[exp_name].configure(background="#d0ebff")  # light blue

        selected_experiment.set(exp_name)

        # Update info box
        path = loaded_experiments.get(exp_name, "Unknown path")
        experiment_info_text.config(state="normal")
        experiment_info_text.delete("1.0", tk.END)
        experiment_info_text.insert(tk.END, f"Selected Experiment: {exp_name}\n\nPath:\n{path}\n\n(Additional info coming soon)")
        experiment_info_text.config(state="disabled")

    # --- Load default experiments ---
    experiments_dir = "experiments"
    if not os.path.exists(experiments_dir):
        os.makedirs(experiments_dir)

    experiments = [d for d in os.listdir(experiments_dir) if os.path.isdir(os.path.join(experiments_dir, d))]

    if experiments:
        for exp in experiments:
            exp_path = os.path.join(experiments_dir, exp)
            loaded_experiments[exp] = exp_path
            create_experiment_label(exp)

    if app.added_experiments:
        for exp_name, exp_path in app.added_experiments.items():
            if exp_name not in loaded_experiments:
                loaded_experiments[exp_name] = exp_path
                create_experiment_label(exp_name)

    if not experiments and not app.added_experiments:
            app.no_experiments_label = ttk.Label(
                scrollable_frame,
                text="No experiments found.",
                font=("Segoe UI", 14, "italic"),
                foreground="gray"
            )
            app.no_experiments_label.pack(pady=10)

    # === Selected Experiment Info Field ===
    info_frame = tk.Frame(app.root, bg="#f0f0f0")
    info_frame.pack(padx=20, pady=10, fill="both", expand=False)

    experiment_info_text = tk.Text(info_frame, height=7, font=("Segoe UI", 12), bg="#f8f8f8", wrap="word")
    experiment_info_text.pack(fill="both", expand=True)
    experiment_info_text.insert(tk.END, "Select an experiment to view its details here.")
    experiment_info_text.config(state="disabled")  # Make it read-only

    # === Bottom Buttons (Continue and Launch) ===
    button_frame = tk.Frame(app.root, bg="#f0f0f0")
    button_frame.pack(pady=20)

    continue_button = ttk.Button(button_frame, text="Continue Experiment", width=25)
    continue_button.grid(row=0, column=0, padx=20, pady=10)

    def launch_experiment():
        exp_name = selected_experiment.get()
        if not exp_name:
            print("No experiment selected.")
            return

        exp_path = loaded_experiments.get(exp_name)
        if not exp_path:
            print("Experiment path not found.")
            return

        # Now pass the selected experiment name and path to the session screen!
        show_experiment_session_start(app, exp_name, exp_path)

    launch_button = ttk.Button(button_frame, text="Launch New Experiment", width=25, command=launch_experiment)
    launch_button.grid(row=0, column=1, padx=20, pady=10)