import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
from running_session_screen import show_running_session_screen


def show_experiment_session_start(app, experiment_name, experiment_path, continue_mode=False):
    app.current_screen = "session_start"
    app.root.configure(bg="#f0f0f0")

    if continue_mode:
        continue_data = {}
        continue_path = os.path.join(experiment_path, "continue_experiment.json")
        if os.path.isfile(continue_path):
            try:
                with open(continue_path, "r") as cf:
                    continue_data = json.load(cf)
            except Exception as e:
                print(f"Error loading continue_experiment.json: {e}")
        

    def start_session():
        # 1) Clear previous errors
        for entry, lbl in [
            (participant_name_entry, participant_name_error),
            (save_name_entry,      save_name_error),
            (save_location_entry,  save_location_error),
        ]:
            entry.configure(style="TEntry")
            lbl.config(text="")

        valid = True

        # 2) Validate participant name
        if not participant_name_entry.get().strip():
            participant_name_entry.configure(style="Error.TEntry")
            participant_name_error.config(text="Required")
            valid = False

        # 3) Validate save name
        if not save_name_entry.get().strip():
            save_name_entry.configure(style="Error.TEntry")
            save_name_error.config(text="Required")
            valid = False

        # 4) Validate save location (only emptiness)
        if not save_location_entry.get().strip():
            save_location_entry.configure(style="Error.TEntry")
            save_location_error.config(text="Required")
            valid = False

        if not valid:
            return

        # 5) All good—stash and proceed
        app.participant_name   = participant_name_entry.get().strip()
        app.participant_number = participant_number_var.get()
        app.save_name          = save_name_entry.get().strip()
        app.save_location      = save_location_entry.get().strip()

        # 5a) Write out a continue_experiment.json in the experiment folder
        try:
            cont_data = {
                "participant_number": app.participant_number,
                "participant_name":   app.participant_name,
                "save_name":          app.save_name,
                "save_location":      app.save_location
            }
            cont_path = os.path.join(experiment_path, "continue_experiment.json")
            with open(cont_path, "w") as cf:
                json.dump(cont_data, cf, indent=2)
            print(f"Wrote continue file to {cont_path}")
        except Exception as e:
            print(f"Error writing continue_experiment: {e}")
        show_running_session_screen(app, experiment_path)

    start_button = ttk.Button(app.root, text=app.tr("start_session"), width=30, command=start_session)
    start_button.pack(pady=20)

    def load_create_screen_state(file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            required_keys = {"exp_name", "participant_name", "save_location", "metadata"}
            if not required_keys.issubset(data.keys()):
                print(f"Invalid create_screen_state.json format: missing keys in {file_path}")
                return None

            return data

        except Exception as e:
            print(f"Error loading create_screen_state.json: {e}")
            return None

    app.clear_screen()

    create_state_path = os.path.join(experiment_path, "create_screen_state.json")
    create_state = load_create_screen_state(create_state_path)

    default_participant_name = create_state.get("participant_name", "Participant") if create_state else "Participant"
    if continue_mode and continue_data:
        default_participant_name   = continue_data.get("participant_name", default_participant_name)
        app.participant_number = continue_data.get("participant_number", 1)
        app.participant_number = app.participant_number+1
        app.save_location = continue_data.get("save_location", "")

    metadata_items = create_state.get("metadata", []) if create_state else []
    # === Top Frame ===
    top_frame = tk.Frame(app.root, bg="#f0f0f0")
    top_frame.pack(fill="x", pady=(10, 0))

    def back_to_launch_screen():
        # Remove participant_number if it exists
        if hasattr(app, "participant_number"):
            del app.participant_number

        from launch_screen import show_launch_screen
        show_launch_screen(app)


    back_button = ttk.Button(top_frame, text="←", command=back_to_launch_screen, width=3)
    back_button.pack(side="left", padx=10)
    app.language_var = tk.StringVar(value=app.current_language)
    lang_dropdown = ttk.Combobox(
        top_frame,
        textvariable=app.language_var,
        values=app.languages,
        state="readonly",
        width=12
    )
    lang_dropdown.pack(side="left")
    lang_dropdown.bind("<<ComboboxSelected>>", app.on_language_change)
    title_label = ttk.Label(top_frame, text=app.tr("experiment_colon").format(experiment_name=experiment_name), font=("Segoe UI", 20, "bold"))
    title_label.pack(side="left", padx=20)

    # === Main Session Frame ===
    session_frame = tk.Frame(app.root, bg="#f0f0f0")
    session_frame.pack(expand=True, pady=30)

    # Prepare an “error” style for entries:
    style = ttk.Style(app.root)
    style.configure("Error.TEntry", fieldbackground="#ffe6e6")

    # === Participant Name Row ===
    participant_name_frame = tk.Frame(session_frame, bg="#f0f0f0")
    participant_name_frame.pack(pady=(10, 5), fill="x", padx=20)

    participant_name_label = ttk.Label(participant_name_frame, text=app.tr("participant_name"), font=("Segoe UI", 16))
    participant_name_label.pack(side="left", padx=(0,10))

    participant_name_entry = ttk.Entry(participant_name_frame, font=("Segoe UI", 14), width=30)
    participant_name_entry.insert(0, default_participant_name)
    participant_name_entry.pack(side="left", fill="x", expand=True)

    # <— error label starts hidden
    participant_name_error = ttk.Label(participant_name_frame, text="", foreground="red", font=("Segoe UI",10))
    participant_name_error.pack(anchor="w", padx=(150,0), pady=(2,0))

    # === Participant Number Row ===
    participant_number_frame = tk.Frame(session_frame, bg="#f0f0f0")
    participant_number_frame.pack(pady=(10, 20), fill="x", padx=20)

    participant_number_label = ttk.Label(participant_number_frame, text=app.tr("participant_number"), font=("Segoe UI", 16))
    participant_number_label.pack(side="left", padx=(0,10))

    participant_number_var = tk.IntVar()

    participant_number_spinbox = ttk.Spinbox(
        participant_number_frame,
        from_=1,
        to=9999,
        textvariable=participant_number_var,
        font=("Segoe UI", 14),
        width=10
    )
    participant_number_spinbox.pack(side="left", fill="x", expand=False)

    participant_number_var.set(getattr(app, "participant_number", 1))
    participant_number_spinbox.update()


    # === Save Name Row ===
    save_name_frame = tk.Frame(session_frame, bg="#f0f0f0")
    save_name_frame.pack(pady=(30, 5), fill="x", padx=20)

    save_name_label = ttk.Label(save_name_frame, text=app.tr("save_name"), font=("Segoe UI", 16))
    save_name_label.pack(side="left", padx=(0,10))

    save_name_entry = ttk.Entry(save_name_frame, font=("Segoe UI", 14), width=40)
    save_name_entry.pack(side="left", fill="x", expand=True)

    save_name_error = ttk.Label(save_name_frame, text="", foreground="red", font=("Segoe UI",10))
    save_name_error.pack(anchor="w", padx=(150,0), pady=(2,0))

    # === Save Location Row ===
    save_location_frame = tk.Frame(session_frame, bg="#f0f0f0")
    save_location_frame.pack(pady=(10, 20), fill="x", padx=20)

    save_location_label = ttk.Label(
        save_location_frame,
        text=app.tr("save_location"),
        font=("Segoe UI", 16)
    )
    save_location_label.pack(side="left", padx=(0,10))

    save_location_entry = ttk.Entry(
        save_location_frame,
        font=("Segoe UI", 12),
        width=70
    )
    save_location_entry.pack(side="left", fill="x", expand=True, padx=(0,5))

    # define the browse function *before* the button
    def browse_save_location():
        folder = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Select Save Folder"
        )
        if folder:
            save_location_entry.delete(0, tk.END)
            save_location_entry.insert(0, folder)

    # create exactly one Browse button
    browse_button = ttk.Button(
        save_location_frame,
        text=app.tr("browse"),
        command=browse_save_location
    )
    browse_button.pack(side="left", padx=(5,0))

    # inline error label
    save_location_error = ttk.Label(
        save_location_frame,
        text="",
        foreground="red",
        font=("Segoe UI", 10)
    )
    save_location_error.pack(side="left", padx=(10,0))


    # === Dynamic updating save_name and save_location ===
    def update_save_name_and_location(*args):
        pname = participant_name_entry.get().strip() or "Participant"
        pnumber = participant_number_var.get()
        current_save_name = f"{pname}_{pnumber}"
        save_name_entry.delete(0, tk.END)
        save_name_entry.insert(0, current_save_name)

        # 2) If the app already has a save_location, reuse it…
        if hasattr(app, "save_location") and app.save_location:
            default_save_location = app.save_location
        else:
            # …otherwise fall back to the session_saves/<experiment> folder
            default_save_location = os.path.join("session_saves", experiment_name)

        save_location_entry.delete(0, tk.END)
        save_location_entry.insert(0, default_save_location)

    update_save_name_and_location()

    participant_number_var.trace_add('write', lambda *args: update_save_name_and_location())
    participant_name_entry.bind('<KeyRelease>', lambda event: update_save_name_and_location())

    # === Start Session Button ===
    start_button = ttk.Button(app.root, text=app.tr("start_session"), width=30, command=start_session)
    start_button.pack(pady=20)

