import tkinter as tk
from tkinter import ttk
import json
import os
import tkinter.font as tkfont
from PIL import Image, ImageTk

def show_running_session_screen(app, experiment_path):
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

        selections = component.get("last_selections", [])
        distractors = component.get("last_distractors", [])

        image_paths = []

        if selections:
            target_path = selections[0].get('path')
            if target_path:
                full_target_path = os.path.join(app.experiment_path, target_path.replace("/", os.sep))
                image_paths.append((full_target_path, True))

        if distractors:
            distractor_paths = distractors[0].get('paths', [])
            for d_path in distractor_paths:
                full_distractor_path = os.path.join(app.experiment_path, d_path.replace("/", os.sep))
                image_paths.append((full_distractor_path, False))

        import random
        random.shuffle(image_paths)

        app.image_refs = []

        # 🧹 Main Grid Wrapping Frame
        grid_wrapper_outer = tk.Frame(main_frame, bg="#d0d0d0")
        grid_wrapper_outer.pack(expand=True, fill="both")

        grid_wrapper_outer.pack_propagate(False)  # Important: prevent shrinking!

        # 🖼 Inner centered frame
        grid_wrapper = tk.Frame(grid_wrapper_outer, bg="#d0d0d0")
        grid_wrapper.place(relx=0.5, rely=0.5, anchor="center")  # absolute centering

        # 📦 Slot settings
        slot_size = 90  # bigger slots now!

        idx = 0
        for row in range(field_y):
            for col in range(field_x):
                slot = tk.Frame(grid_wrapper, width=slot_size, height=slot_size, bg="#d0d0d0", highlightthickness=0)
                slot.grid(row=row, column=col, padx=4, pady=4)
                slot.grid_propagate(False)

                if idx < len(image_paths):
                    img_path, is_target = image_paths[idx]
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((slot_size - 10, slot_size - 10))  # small margin
                        img_tk = ImageTk.PhotoImage(img)

                        canvas = tk.Canvas(slot, width=slot_size, height=slot_size, bg="#d0d0d0", highlightthickness=0)
                        canvas.pack()

                        canvas.create_image(slot_size // 2, slot_size // 2, image=img_tk, anchor="center")


                        app.image_refs.append(img_tk)

                    except Exception as e:
                        print(f"Failed to load image {img_path}: {e}")

                idx += 1



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
    # Unbind previous space so it doesn't double-bind
    app.root.unbind('<space>')

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
        from launch_screen import show_launch_screen
        show_launch_screen(app)

    back_button = ttk.Button(complete_frame, text="Back to Launch Screen", command=back_to_launch_screen)
    back_button.pack(pady=20)



