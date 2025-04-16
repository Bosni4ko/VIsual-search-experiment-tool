import tkinter as tk
import os
from tkinter import Toplevel, Listbox, Scrollbar, Label, Button, filedialog
from PIL import Image, ImageTk

import os
import tkinter as tk
from tkinter import Toplevel, Label, Frame, Button, Scrollbar
from PIL import Image, ImageTk
from functools import partial

import os
import tkinter as tk
from tkinter import Toplevel, Label, Frame, Button, Scrollbar
from PIL import Image, ImageTk

import os
import tkinter as tk
from tkinter import Toplevel, Label, Scrollbar, Frame, Button
from PIL import Image, ImageTk

def open_image_selector(comp, target_type):
    # Only proceed if the stimulus set is Faces.
    if comp.data.get("stimulus_set") != "Faces":
        return

    stimulus_set = comp.data.get("stimulus_set")
    # Create a unique key for this stimulus set and target type
    prev_key = (stimulus_set, target_type)
    # Ensure that a dictionary for remembering selections exists.
    comp.data.setdefault("last_selections", {})

    base_path = os.path.join("images", "faces")

    if target_type == "positive":
        categories = {"happy": os.path.join(base_path, "positive", "happy")}
    elif target_type == "neutral":
        categories = {"neutral": os.path.join(base_path, "neutral", "neutral")}
    elif target_type == "negative":
        categories = {
            "angry": os.path.join(base_path, "negative", "angry"),
            "disgust": os.path.join(base_path, "negative", "disgust"),
            "fear": os.path.join(base_path, "negative", "fear"),
            "sad": os.path.join(base_path, "negative", "sad")
        }
    else:
        return

    selector_win = Toplevel()
    selector_win.title("Select Target Image")
    selector_win.geometry("800x500")
    selector_win.image_refs = []  # Prevent image garbage collection

    selected_label = Label(selector_win, text="No image selected.")
    selected_label.pack(pady=5)

    # Create scrollable canvas
    canvas = tk.Canvas(selector_win)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(selector_win, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    content_frame = Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    content_frame.bind("<Configure>", on_frame_configure)

    # Optional mouse wheel scrolling (with lazy loading)
    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
        lazy_load_images()
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    selected_frame = {"ref": None}
    # Store references for image placeholders for lazy loading
    placeholders = {}
    loaded_images = set()

    # -------------------------------
    # Lazy loading logic
    # -------------------------------
    def is_visible(widget):
        try:
            widget_top = widget.winfo_rooty()
            widget_bottom = widget_top + widget.winfo_height()
            canvas_top = canvas.winfo_rooty()
            canvas_bottom = canvas_top + canvas.winfo_height()
            return (widget_bottom > canvas_top) and (widget_top < canvas_bottom)
        except:
            return False

    def lazy_load_images():
        for img_id, widget in placeholders.items():
            if img_id in loaded_images:
                continue
            if is_visible(widget["container"]):
                try:
                    img = Image.open(widget["path"]).convert("RGB")
                    img.thumbnail((90, 90), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    selector_win.image_refs.append(img_tk)
                    widget["placeholder"].config(image=img_tk, text="")
                    widget["placeholder"].image = img_tk
                    loaded_images.add(img_id)
                except Exception as e:
                    print(f"Could not load {widget['path']}: {e}")

    # -------------------------------
    # Image selection callback
    # -------------------------------
    def select_image(path, name, container):
        # Save the current selected image path in comp.data.
        comp.data["target_image"] = path
        selected_label.config(text=f"Selected: {name}")
        # Un-highlight previous selection
        if selected_frame["ref"]:
            selected_frame["ref"].config(bg="SystemButtonFace")
        container.config(bg="lightblue")
        selected_frame["ref"] = container

    # -------------------------------
    # Build a stable grid layout (no dynamic reflow)
    # -------------------------------
    # In this example we choose a fixed number of columns.
    images_per_row = 5

    # Loop through categories. (If you have multiple categories,
    # each will appear with a separate label and grid.)
    for cat, folder in categories.items():
        Label(content_frame, text=cat.capitalize(),
              font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        img_grid = Frame(content_frame)
        img_grid.pack(anchor="w", padx=10, pady=5)

        try:
            images = [f for f in os.listdir(folder)
                      if f.lower().endswith((".jpg", ".png", ".jpeg", ".bmp", ".gif"))]
        except FileNotFoundError:
            images = []

        for i, img_name in enumerate(images):
            path = os.path.join(folder, img_name)
            # Each image occupies two grid rows (one for the container and one for the caption)
            row_base = (i // images_per_row) * 2  
            col = i % images_per_row

            # Create a fixed-size container for the image
            container = Frame(img_grid, bd=2, relief="solid", width=100, height=100)
            container.grid_propagate(False)
            container.grid(row=row_base, column=col, padx=5, pady=5)

            # Placeholder label inside the container (centered)
            placeholder = Label(container, text="Loading...")
            placeholder.place(relx=0.5, rely=0.5, anchor="center")

            # Caption label below for the filename
            caption = Label(img_grid, text=img_name, wraplength=90)
            caption.grid(row=row_base + 1, column=col, padx=5, pady=(0, 5))

            # Bind clicks on both container and placeholder to the select callback.
            container.bind("<Button-1>",
                           lambda e, p=path, n=img_name, c=container: select_image(p, n, c))
            placeholder.bind("<Button-1>",
                             lambda e, p=path, n=img_name, c=container: select_image(p, n, c))

            placeholders[(cat, i)] = {
                "container": container,
                "placeholder": placeholder,
                "caption": caption,
                "path": path
            }

    # -------------------------------
    # Preselect the previous image (if one was confirmed before)
    # -------------------------------
    previous_selected_path = comp.data["last_selections"].get(prev_key)
    if previous_selected_path:
        for key, widget in placeholders.items():
            if widget["path"] == previous_selected_path:
                select_image(widget["path"], widget["caption"].cget("text"), widget["container"])
                break

    # -------------------------------
    # Confirm button: Remember selection and close
    # -------------------------------
    def on_confirm():
        # Save the current selection (if any) for this stimulus set and target type.
        if comp.data.get("target_image"):
            comp.data["last_selections"][prev_key] = comp.data["target_image"]
        selector_win.destroy()

    Button(selector_win, text="Confirm", command=on_confirm).pack(pady=10)

    # Run an initial lazy loading pass.
    lazy_load_images()




def setup_stimulus_options(app, left_panel, comp):
    def add_label(text, pady=8):
        return tk.Label(left_panel, text=text, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(pady, 2))

    def add_dropdown(var, options):
        return tk.OptionMenu(left_panel, var, *options)

    # ---------- Field Size ----------
    add_label("Field Size")
    field_frame = tk.Frame(left_panel)
    field_frame.pack(anchor="w", padx=10)

    field_x = tk.Entry(field_frame, width=5)
    field_y = tk.Entry(field_frame, width=5)

    field_x.insert(0, str(comp.data.get("field_x", 10)))
    field_y.insert(0, str(comp.data.get("field_y", 10)))

    field_x.pack(side="left")
    tk.Label(field_frame, text="  X  ").pack(side="left")
    field_y.pack(side="left")

    def save_field_size(*_):
        try:
            comp.data["field_x"] = int(field_x.get())
            comp.data["field_y"] = int(field_y.get())
        except ValueError:
            pass

    field_x.bind("<FocusOut>", save_field_size)
    field_y.bind("<FocusOut>", save_field_size)

    # ---------- Stimulus Set Size ----------
    add_label("Stimulus Set Size")

    size_var = tk.StringVar(value=comp.data.get("stimulus_size_mode", "random"))
    size_menu = add_dropdown(size_var, ["random", "fixed", "random in range"])
    size_menu.pack(anchor="w", padx=10, fill="x")

    amount_frame = tk.Frame(left_panel)
    amount_frame.pack(anchor="w", padx=10, pady=(5, 0))

    def update_amount_input(*args):
        for widget in amount_frame.winfo_children():
            widget.destroy()

        selection = size_var.get()
        comp.data["stimulus_size_mode"] = selection

        tk.Label(amount_frame, text="Amount:").pack(side="left", padx=(0, 5))

        if selection == "random":
            dash_entry = tk.Entry(amount_frame, width=7, state="readonly", justify="center")
            dash_entry.insert(0, "-")
            dash_entry.pack(side="left")

        elif selection == "fixed":
            amount_entry = tk.Entry(amount_frame, width=7)
            amount_entry.insert(0, str(comp.data.get("fixed_amount", "")))
            amount_entry.pack(side="left")

            def save_fixed_amount(*_):
                try:
                    comp.data["fixed_amount"] = int(amount_entry.get())
                except ValueError:
                    comp.data["fixed_amount"] = None

            amount_entry.bind("<FocusOut>", save_fixed_amount)

        elif selection == "random in range":
            range_start = tk.Entry(amount_frame, width=5)
            range_end = tk.Entry(amount_frame, width=5)

            range_start.insert(0, str(comp.data.get("range_start", "")))
            range_end.insert(0, str(comp.data.get("range_end", "")))

            range_start.pack(side="left")
            tk.Label(amount_frame, text=" to ").pack(side="left")
            range_end.pack(side="left")

            def save_range(*_):
                try:
                    comp.data["range_start"] = int(range_start.get())
                except ValueError:
                    comp.data["range_start"] = None
                try:
                    comp.data["range_end"] = int(range_end.get())
                except ValueError:
                    comp.data["range_end"] = None

            range_start.bind("<FocusOut>", save_range)
            range_end.bind("<FocusOut>", save_range)

    size_var.trace_add("write", update_amount_input)
    update_amount_input()

    # ---------- Stimulus Set ----------
    add_label("Stimulus Set")
    stim_set_var = tk.StringVar(value=comp.data.get("stimulus_set", "Images"))
    dropdown = add_dropdown(stim_set_var, ["Images", "Faces", "Import"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    stim_set_var.trace_add("write", lambda *_: comp.data.update({"stimulus_set": stim_set_var.get()}))

    # ---------- Target Type ----------
    add_label("Target Type")
    target_type_var = tk.StringVar(value=comp.data.get("target_type", "positive"))
    dropdown = add_dropdown(target_type_var, ["positive", "negative", "neutral"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    target_type_var.trace_add("write", lambda *_: comp.data.update({"target_type": target_type_var.get()}))

    # ---------- No Target ----------
    no_target_var = tk.BooleanVar(value=comp.data.get("no_target", False))
    tk.Checkbutton(left_panel, text="No Target", variable=no_target_var,
                   command=lambda: comp.data.update({"no_target": no_target_var.get()})).pack(anchor="w", padx=10, pady=(5, 0))

    # ---------- Selected Target ----------
    add_label("Selected Target")
    selected_target_var = tk.StringVar(value=comp.data.get("selected_target", "Random"))
    dropdown = add_dropdown(selected_target_var, ["Random", "Select from list"])
    dropdown.pack(anchor="w", padx=10, fill="x")

    def handle_target_select(*_):
        comp.data["selected_target"] = selected_target_var.get()
        if selected_target_var.get() == "Select from list" and stim_set_var.get() == "Faces":
            open_image_selector(comp, target_type_var.get())

    selected_target_var.trace_add("write", handle_target_select)


    # ---------- Distractor Type ----------
    add_label("Distractor Type")
    distractor_type_var = tk.StringVar(value=comp.data.get("distractor_type", "positive"))
    dropdown = add_dropdown(distractor_type_var, ["positive", "negative", "neutral"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    distractor_type_var.trace_add("write", lambda *_: comp.data.update({"distractor_type": distractor_type_var.get()}))

    # ---------- Distractor Set ----------
    add_label("Distractor Set")
    distractor_set_var = tk.StringVar(value=comp.data.get("distractor_set", "All"))
    dropdown = add_dropdown(distractor_set_var, ["All", "Random", "Select set from list"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    distractor_set_var.trace_add("write", lambda *_: comp.data.update({"distractor_set": distractor_set_var.get()}))

