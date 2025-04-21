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

    top_frame = tk.Frame(app.root, bg="#d0d0d0", highlightthickness=0, bd=0)
    top_frame.pack(fill="x", pady=0, padx=0)

    def back_to_start_screen():
        from experiment_session_start import show_experiment_session_start
        show_experiment_session_start(app, experiment_name=os.path.basename(app.experiment_path), experiment_path=app.experiment_path)

    back_button = ttk.Button(top_frame, text="←", command=back_to_start_screen, width=3)
    back_button.pack(side="left", padx=10, pady=5)

    main_frame = tk.Frame(app.root, bg="#d0d0d0", highlightthickness=0, bd=0)
    main_frame.pack(expand=True, fill="both", pady=0, padx=0)

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

    # Prepare content
    text_content = component.get('saved_text', '')

    if component['type'] == 'Stimulus notification':
        # Look for image in next Stimulus
        if app.current_component_index + 1 < len(app.experiment_components):
            next_comp = app.experiment_components[app.current_component_index + 1]
            if next_comp['type'] == 'Stimulus':
                selections = next_comp.get('last_selections', [])
                if selections:
                    first_image_path = selections[0].get('path')
                    if first_image_path:
                        full_image_path = os.path.join(app.experiment_path, first_image_path.replace("/", os.sep))
                        text_content = text_content.replace("[/image/]", f"<<image:{full_image_path}>>")

    # Insert text and images
    insert_text_with_images(text_widget, text_content)

    # Apply formatting (but do NOT delete text anymore)
    apply_formatting_tags(text_widget, component)

    text_widget.configure(state="disabled")

    # Bind space key for next
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



