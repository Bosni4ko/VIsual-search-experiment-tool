import tkinter as tk
from tkinter import ttk
import json
import os
import tkinter.font as tkfont
import time
import csv
from PIL import Image, ImageTk


def show_running_session_screen(app, experiment_path):
    app.stimulus_log = []  #  New empty list to collect stimulus results
    app.stimulus_counter = 0  # counts how many stimulus were shown

    app.clear_screen()
    app.experiment_path = experiment_path
    # Load the experiment_state.json
    experiment_state_path = os.path.join(experiment_path, "experiment_state.json")

    experiment_state = []
    if os.path.exists(experiment_state_path):
        try:
            with open(experiment_state_path, "r") as f:
                experiment_state = json.load(f)
            print(f"Loaded {len(experiment_state)} components from experiment_state.json")
        except Exception as e:
            print(f"Failed to load experiment_state.json: {e}")
    else:
        print(f"experiment_state.json not found at {experiment_state_path}")

    app.experiment_components = experiment_state
    app.current_component_index = 0

    render_current_component(app)
from PIL import Image, ImageTk

def insert_text_with_images(text_widget, content):
    """
    Inserts text into a Text widget, replacing <<image:path>> placeholders with actual images.
    """
    parts = content.split("<<image:")
    text_widget.insert("end", parts[0])

    for part in parts[1:]:
        if ">>" in part:
            image_path, rest_text = part.split(">>", 1)
            try:
                img = Image.open(image_path)
                img = img.resize((150, 150))  # Resize if needed
                img_tk = ImageTk.PhotoImage(img)

                # Keep reference to prevent garbage collection
                if not hasattr(text_widget, "image_refs"):
                    text_widget.image_refs = []
                text_widget.image_refs.append(img_tk)

                text_widget.image_create("end", image=img_tk)
            except Exception as e:
                print(f"Failed to load image {image_path}: {e}")
                text_widget.insert("end", f"[Image Error]")

            text_widget.insert("end", rest_text)
        else:
            text_widget.insert("end", part)

def render_current_component(app):
    # Clear the screen
    for widget in app.root.winfo_children():
        widget.destroy()

    app.root.configure(bg="#d0d0d0")

    if not hasattr(app, 'experiment_components') or app.current_component_index >= len(app.experiment_components):
        show_session_complete_screen(app)
        return

    component = app.experiment_components[app.current_component_index]

    def back_to_start_screen():
        from experiment_session_start import show_experiment_session_start
        show_experiment_session_start(app, experiment_name=os.path.basename(app.experiment_path), experiment_path=app.experiment_path)

    back_button = ttk.Button(app.root, text="←", command=back_to_start_screen, width=3)
    back_button.place(x=10, y=10)  # ← Place it absolutely at the top-left

    # === Main Area ===
    main_frame = tk.Frame(app.root, bg="#d0d0d0", highlightthickness=0, bd=0)
    main_frame.pack(expand=True, fill="both", pady=0, padx=0)

    # === Handling Different Component Types ===
    if component['type'] in ["Start", "Text", "Stimulus notification", "End"]:
        # --- Text-based components ---
        text_widget = tk.Text(
            main_frame,
            font=("Segoe UI", 16),
            wrap="word",
            width=80,
            height=20,
            bg="#d0d0d0",
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        text_widget.pack(expand=True, padx=20, pady=20, fill="both")

        # --- Load the text ---
        text_content = component.get('saved_text', '')

        if component['type'] == 'Stimulus notification':
            # Special replacement of [/image/] with real image
            if app.current_component_index + 1 < len(app.experiment_components):
                next_comp = app.experiment_components[app.current_component_index + 1]
                if next_comp['type'] == 'Stimulus':
                    selections = next_comp.get('last_selections', [])
                    if selections:
                        first_image_path = selections[0].get('path')
                        if first_image_path:
                            full_image_path = os.path.join(app.experiment_path, first_image_path.replace("/", os.sep))
                            text_content = text_content.replace("[/image/]", f"<<image:{full_image_path}>>")

        # --- Insert content with images ---
        insert_text_with_images(text_widget, text_content)

        # --- Apply saved formatting ---
        apply_formatting_tags(text_widget, component)

        text_widget.configure(state="disabled")

    elif component['type'] == "Stimulus":
        field_x = component.get("data", {}).get("field_x", 5)
        field_y = component.get("data", {}).get("field_y", 5)

        data = component.get("data", {})

        stimulus_size_mode = data.get("stimulus_size_mode", "random")
        no_target = data.get("no_target", False)
        fixed_amount = data.get("fixed_amount", 5)
        range_start = data.get("range_start", 2)
        range_end = data.get("range_end", field_x * field_y)

        selections = component.get("last_selections", [])
        distractors = component.get("last_distractors", [])

        target_image = None
        distractor_images = []

        if not no_target and selections:
            target_path = selections[0].get('path')
            if target_path:
                target_image = os.path.join(app.experiment_path, target_path.replace("/", os.sep))

        if distractors:
            distractor_paths = distractors[0].get('paths', [])
            for d_path in distractor_paths:
                full_distractor_path = os.path.join(app.experiment_path, d_path.replace("/", os.sep))
                distractor_images.append(full_distractor_path)

        import random

        if stimulus_size_mode == "random":
            num_images = random.randint(2, field_x * field_y)
        elif stimulus_size_mode == "fixed":
            num_images = fixed_amount
        elif stimulus_size_mode == "random in range":
            num_images = random.randint(range_start, range_end)
        else:
            num_images = 2

        images_to_display = []

        if target_image:
            images_to_display.append((target_image, True))

        distractors_needed = num_images - len(images_to_display)

        if distractor_images:
            expanded_distractors = []
            while len(expanded_distractors) < distractors_needed:
                remaining = distractor_images.copy()
                random.shuffle(remaining)
                expanded_distractors.extend(remaining)

            expanded_distractors = expanded_distractors[:distractors_needed]
            for d_path in expanded_distractors:
                images_to_display.append((d_path, False))

        random.shuffle(images_to_display)
        app.current_stimulus_info = {
            "stimulus_number": app.stimulus_counter + 1,
            "number_of_distractors": 0,  # will count below
            "target_present": False,
            "placements": []
        }


        app.image_refs = []
        loaded_images = []

        # 🖼 Preload all images
        for img_path, is_target in images_to_display:
            try:
                img = Image.open(img_path)
                img.thumbnail((80, 80))
                img_tk = ImageTk.PhotoImage(img)

                loaded_images.append((img_tk, is_target, img_path))  # 🔥 Save path together!
                app.image_refs.append(img_tk)
            except Exception as e:
                print(f"Failed to preload image {img_path}: {e}")

        # 🧹 Main Grid Frame
        grid_wrapper_outer = tk.Frame(main_frame, bg="#d0d0d0")
        grid_wrapper_outer.pack(expand=True, fill="both")
        grid_wrapper_outer.pack_propagate(False)

        grid_wrapper = tk.Frame(grid_wrapper_outer, bg="#d0d0d0")
        grid_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        slot_size = 90

        # Prepare slots
        slot_frames = []
        for row in range(field_y):
            row_slots = []
            for col in range(field_x):
                slot = tk.Frame(grid_wrapper, width=slot_size, height=slot_size, bg="#d0d0d0", highlightthickness=0)
                slot.grid(row=row, column=col, padx=2, pady=2)
                slot.grid_propagate(False)
                row_slots.append(slot)
            slot_frames.append(row_slots)

        total_slots = [(r, c) for r in range(field_y) for c in range(field_x)]
        random.shuffle(total_slots)

        # === Phase 1: Chessboard 1 ===
        def show_chessboard(color1, color2):
            for r in range(field_y):
                for c in range(field_x):
                    color = color1 if (r + c) % 2 == 0 else color2
                    slot_frames[r][c].configure(bg=color)

        show_chessboard("#d8d8d8", "#b8b8b8")  # light/dark grey

        def phase2_invert_chessboard():
            show_chessboard("#b8b8b8", "#d8d8d8")

        def phase3_fixation_cross():
            # Set all to neutral grey
            for r in range(field_y):
                for c in range(field_x):
                    slot_frames[r][c].configure(bg="#d0d0d0")

            # Draw cross
            cross_canvas = tk.Canvas(grid_wrapper_outer, bg="#d0d0d0", highlightthickness=0)
            cross_canvas.place(relx=0.5, rely=0.5, anchor="center", width=50, height=50)

            cross_canvas.create_line(0, 25, 50, 25, fill="white", width=8)
            cross_canvas.create_line(25, 0, 25, 50, fill="white", width=8)

            app.stimulus_start_time = None
            # Next phase after delay
            def phase4_show_images():
                cross_canvas.destroy()

                for slot in sum(slot_frames, []):
                    for widget in slot.winfo_children():
                        widget.destroy()

                for (img_tk, is_target, img_path), (r, c) in zip(loaded_images, total_slots):

                    canvas = tk.Canvas(slot_frames[r][c], width=slot_size, height=slot_size, bg="#d0d0d0", highlightthickness=0)
                    canvas.pack()
                    canvas.create_image(slot_size // 2, slot_size // 2, image=img_tk, anchor="center")

                    # 📋 Save placement info
                    app.current_stimulus_info["placements"].append({
                        "row": r,
                        "col": c,
                        "is_target": is_target,
                        "image_path": img_path    # we cannot get file path from img_tk easily, you may want to map manually
                    })

                    if is_target:
                        app.current_stimulus_info["target_present"] = True
                    else:
                        app.current_stimulus_info["number_of_distractors"] += 1

                #RECORD THE TIME when images appear
                app.stimulus_start_time_ns = time.perf_counter_ns()

            app.root.after(1500, phase4_show_images)

        # Timed transitions
        app.root.after(500, phase2_invert_chessboard)
        app.root.after(1000, phase3_fixation_cross)

    # === Bind space key for next ===
    app.root.bind('<space>', lambda event: next_component(app))

def apply_formatting_tags(text_widget, component):
    """
    Apply formatting tags to an already inserted text in a tk.Text widget.
    """
    for tag_info in component.get('saved_tags', []):
        name = tag_info['name']
        opts = {}

        font_info = tag_info.get('font_info')
        if font_info:
            font_obj = tkfont.Font(**font_info)
            opts['font'] = font_obj

        fg = tag_info.get('foreground')
        if fg:
            opts['foreground'] = fg

        just = tag_info.get('justify')
        if just:
            opts['justify'] = just

        if opts:
            text_widget.tag_configure(name, **opts)

        for start, end in tag_info['ranges']:
            text_widget.tag_add(name, start, end)


def next_component(app):
    app.root.unbind('<space>')

    if hasattr(app, 'stimulus_start_time_ns'):
        reaction_time_ns = time.perf_counter_ns() - app.stimulus_start_time_ns
        reaction_time_seconds = reaction_time_ns / 1_000_000_000

        if hasattr(app, 'current_stimulus_info'):
            stimulus_info = app.current_stimulus_info
            stimulus_info["reaction_time_seconds"] = reaction_time_seconds
            app.stimulus_log.append(stimulus_info)

            app.stimulus_counter += 1  # Increment stimulus number

            del app.current_stimulus_info

        del app.stimulus_start_time_ns


    app.current_component_index += 1
    render_current_component(app)


def show_session_complete_screen(app):
    for widget in app.root.winfo_children():
        widget.destroy()

    complete_frame = tk.Frame(app.root, bg="#d0d0d0")
    complete_frame.pack(expand=True, fill="both")

    complete_label = ttk.Label(
        complete_frame,
        text="Session Complete!",
        font=("Segoe UI", 24, "bold"),
        background="#d0d0d0",
        foreground="black"
    )
    complete_label.pack(expand=True, pady=20)

    def back_to_launch_screen():
        app.participant_number = app.participant_number + 1
        from experiment_session_start import show_experiment_session_start
        show_experiment_session_start(
            app,
            experiment_name=os.path.basename(app.experiment_path),
            experiment_path=app.experiment_path
        )

    back_button = ttk.Button(
        complete_frame,
        text="Back to Launch Screen",
        command=back_to_launch_screen
    )
    back_button.pack(pady=20)

    # === Save stimulus log using app.save_location and app.save_name ===
    try:
        # Ensure the save directory exists
        os.makedirs(app.save_location, exist_ok=True)

        # Build the full path: <save_location>/<save_name>.json
        filename = f"{app.save_name}.json"
        save_path = os.path.join(app.save_location, filename)
        output = {
            "participant_name":    app.participant_name,
            "participant_number":  app.participant_number,
            "metadata":            app.metadata,
            "stimulus_log":        app.stimulus_log
        }
        
        with open(save_path, "w") as f:
            json.dump(output, f, indent=2)

        print(f"Saved stimulus log to {save_path}")

    except Exception as e:
        print(f"Failed to save stimulus log: {e}")

 # === Write all reaction times in one single CSV row, prefixed by name & number ===
    try:
        os.makedirs(app.save_location, exist_ok=True)
        csv_path = os.path.join(app.save_location, "stimulus_times.csv")

        # 1) collect reaction times in order
        reaction_times = [trial["reaction_time_seconds"] for trial in app.stimulus_log]

        # 2) build header:
        #    - fixed columns: name & number
        #    - one column per metadata key (in insertion order)
        #    - one column per stimulus
        metadata_keys   = list(app.metadata.keys())
        stimulus_cols   = [f"stimulus_{i+1}" for i in range(len(reaction_times))]
        headers = (
            ["participant_name", "participant_number"]
            + metadata_keys
            + stimulus_cols
        )

        # 3) build the row:
        #    - participant info
        #    - metadata values (in the same order as metadata_keys)
        #    - reaction times
        row = (
            [app.participant_name, app.participant_number]
            +[app.metadata[k] for k in metadata_keys]
            +reaction_times
        )

        # 4) decide whether to write header
        write_header = not os.path.isfile(csv_path)

        # 5) append to CSV
        with open(csv_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(headers)
            writer.writerow(row)

        print(f"Wrote single‐row stimulus times (with participant info) to {csv_path}")

    except Exception as e:
        print(f"Failed to write stimulus_times.csv: {e}")
