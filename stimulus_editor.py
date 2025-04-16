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
    # Get the currently selected stimulus set.
    stimulus_set = comp.data.get("stimulus_set", "Faces")
    # Allow the selector if the current stimulus set is either "Faces" or an imported set.
    if stimulus_set != "Faces" and stimulus_set not in comp.data.get("imported_stimulus_sets", {}):
        return

    # Set the base path according to the stimulus set.
    if stimulus_set == "Faces":
        base_path = os.path.join("images", "faces")
    else:
        base_path = comp.data["imported_stimulus_sets"][stimulus_set]

    # Create a unique key for this stimulus set and target type
    prev_key = (stimulus_set, target_type)
    # Ensure that a dictionary for remembering selections exists.
    comp.data.setdefault("last_selections", {})

    def get_categories(base_path, target_type):
        """Return a dictionary mapping subfolder names to their full paths 
        for a given target type folder inside base_path.
        """
        target_dir = os.path.join(base_path, target_type)
        if os.path.isdir(target_dir):
            subdirs = [d for d in os.listdir(target_dir) 
                    if os.path.isdir(os.path.join(target_dir, d))]
            if subdirs:
                return {d: os.path.join(target_dir, d) for d in subdirs}
            else:
                return {target_type: target_dir}
        return {}
    
    if target_type in ["positive", "neutral", "negative"]:
        categories = get_categories(base_path, target_type)
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

def open_distractor_selector(comp, distractor_type):
    # Get the current stimulus set.
    stimulus_set = comp.data.get("stimulus_set", "Faces")
    # Proceed only if it's "Faces" or an imported set.
    if stimulus_set != "Faces" and stimulus_set not in comp.data.get("imported_stimulus_sets", {}):
        print("returned")
        return

    # Determine the base folder.
    if stimulus_set == "Faces":
        base_path = os.path.join("images", "faces")
    else:
        base_path = comp.data["imported_stimulus_sets"][stimulus_set]
    print(base_path)

    # Create a unique key for this stimulus set and distractor type.
    prev_key = (stimulus_set, distractor_type)
    # Ensure that a dictionary for remembering distractor selections exists.
    comp.data.setdefault("last_distractors", {})

    def get_categories(base_path, distractor_type):
            """Return a dictionary mapping subfolder names to their full paths 
            for a given target type folder inside base_path.
            """
            target_dir = os.path.join(base_path, distractor_type)
            if os.path.isdir(target_dir):
                subdirs = [d for d in os.listdir(target_dir) 
                        if os.path.isdir(os.path.join(target_dir, d))]
                if subdirs:
                    return {d: os.path.join(target_dir, d) for d in subdirs}
                else:
                    return {distractor_type: target_dir}
            return {}
    
    if distractor_type in ["positive", "neutral", "negative"]:
        categories = get_categories(base_path, distractor_type)
    else:
        return

    selector_win = Toplevel()
    selector_win.title("Select Distractor Images")
    selector_win.geometry("800x500")
    selector_win.image_refs = []  # Prevent image garbage collection

    # Label to show how many images are selected.
    selected_label = Label(selector_win, text="Selected: 0 images")
    selected_label.pack(pady=5)

    # Create a scrollable canvas.
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

    # When the distractor selection window is destroyed, remove the global mouse wheel binding.
    def on_destroy(event):
        canvas.unbind_all("<MouseWheel>")
    selector_win.bind("<Destroy>", on_destroy)

    # For multi-selection, we use a set to store selected distractor image paths.
    selected_distractors = set()
    # To allow shift-selection, we store the key (a tuple like (category, index)) of the last clicked image.
    last_clicked = {"key": None}

    # Dictionaries for lazy loading.
    placeholders = {}
    loaded_images = set()

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

    # Toggle selection for multi-select.
    # event: the click event
    # key: a tuple (cat, i) identifying the image in placeholders
    # path: image file path; container: the widget frame for the image.
    def toggle_selection(event, key, path, container):
        nonlocal selected_distractors
        # Check if Shift is held down.
        if event.state & 0x0001:
            if last_clicked["key"] is not None:
                # Create an ordered list (using the insertion order) of keys.
                ordered_keys = list(placeholders.keys())
                try:
                    anchor_index = ordered_keys.index(last_clicked["key"])
                    current_index = ordered_keys.index(key)
                except ValueError:
                    anchor_index = 0
                    current_index = 0
                start = min(anchor_index, current_index)
                end = max(anchor_index, current_index)
                # Determine base action: if the current image is selected, we deselect the range, otherwise select it.
                base_action = "deselect" if path in selected_distractors else "select"
                for k in ordered_keys[start:end+1]:
                    widget = placeholders[k]
                    if base_action == "select":
                        if widget["path"] not in selected_distractors:
                            selected_distractors.add(widget["path"])
                            widget["container"].config(bg="lightblue")
                    else:
                        if widget["path"] in selected_distractors:
                            selected_distractors.remove(widget["path"])
                            widget["container"].config(bg="SystemButtonFace")
            else:
                # If no anchor exists, do a normal toggle.
                if path in selected_distractors:
                    selected_distractors.remove(path)
                    container.config(bg="SystemButtonFace")
                else:
                    selected_distractors.add(path)
                    container.config(bg="lightblue")
        else:
            # Normal (non-shift) click toggles single selection.
            if path in selected_distractors:
                selected_distractors.remove(path)
                container.config(bg="SystemButtonFace")
            else:
                selected_distractors.add(path)
                container.config(bg="lightblue")
            # Update the last clicked anchor only if shift is not held.
            last_clicked["key"] = key

        selected_label.config(text=f"Selected: {len(selected_distractors)} images")

    # Build a stable grid layout (fixed number of columns).
    images_per_row = 5
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
            row_base = (i // images_per_row) * 2  # using two grid rows per image cell.
            col = i % images_per_row
            # Fixed-size container.
            container = Frame(img_grid, bd=2, relief="solid", width=100, height=100)
            container.grid_propagate(False)
            container.grid(row=row_base, column=col, padx=5, pady=5)
            placeholder = Label(container, text="Loading...")
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
            caption = Label(img_grid, text=img_name, wraplength=90)
            caption.grid(row=row_base+1, column=col, padx=5, pady=(0, 5))
            # Bind both container and placeholder. Pass the event, key, path, and container.
            container.bind("<Button-1>", lambda e, p=path, c=container, key=(cat, i): toggle_selection(e, key, p, c))
            placeholder.bind("<Button-1>", lambda e, p=path, c=container, key=(cat, i): toggle_selection(e, key, p, c))
            placeholders[(cat, i)] = {
                "container": container,
                "placeholder": placeholder,
                "caption": caption,
                "path": path
            }

    # Preselect previously confirmed distractor images (if any exist).
    previous_distractors = comp.data["last_distractors"].get(prev_key, [])
    if previous_distractors:
        # For each placeholder whose path is in previous_distractors, mark it as selected.
        for key, widget in placeholders.items():
            if widget["path"] in previous_distractors:
                # We use the same toggle_selection function without needing shift.
                # Here we simulate a normal click event (state 0).
                fake_event = type("Event", (object,), {"state": 0})()
                toggle_selection(fake_event, key, widget["path"], widget["container"])

    def on_confirm():
        # Save the list of selected distractor image paths.
        comp.data["last_distractors"][prev_key] = list(selected_distractors)
        selector_win.destroy()

    Button(selector_win, text="Confirm", command=on_confirm).pack(pady=10)
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
    # Default options.
    stimulus_options = ["Images", "Faces", "Import"]

    # Initialize app.imported_stimulus_sets if not already present.
    if not hasattr(app, "imported_stimulus_sets"):
        app.imported_stimulus_sets = {}

    # Append any previously imported stimulus sets into the options.
    # Insert them before "Import" so that "Import" remains at the end.
    for imported in app.imported_stimulus_sets:
        stimulus_options.insert(-1, imported)

    # Create an OptionMenu with the combined options.
    stim_dropdown = tk.OptionMenu(left_panel, stim_set_var, *stimulus_options)
    stim_dropdown.pack(anchor="w", padx=10, fill="x")

    def open_import_window():
        # Open a new window for importing a new stimulus set.
        import_win = Toplevel(left_panel)
        import_win.title("Import Stimulus Set")
        
        Label(import_win, text="Stimulus Set Name:").pack(pady=(10, 5))
        name_entry = tk.Entry(import_win)
        name_entry.pack(pady=(0, 10))
        
        Button(import_win, text="Browse Folder", command=lambda: browse_folder()).pack(pady=(0, 5))
        folder_entry = tk.Entry(import_win, width=50)
        folder_entry.pack(pady=(0, 10))
        
        def browse_folder():
            folder = filedialog.askdirectory(title="Select Stimulus Set Folder")
            folder_entry.delete(0, tk.END)
            folder_entry.insert(0, folder)
        
        def add_stimulus_set():
            new_name = name_entry.get().strip()
            folder_path = folder_entry.get().strip()
            if new_name and folder_path:
                # Save in the application-level dictionary.
                app.imported_stimulus_sets[new_name] = folder_path
                # Also store in comp.data so that selectors can access it.
                comp.data.setdefault("imported_stimulus_sets", {})[new_name] = folder_path
                
                # Add the new option to the Stimulus Set OptionMenu.
                menu = stim_dropdown["menu"]
                # Insert the new option before the "Import" option.
                menu.insert_command(0, label=new_name, command=lambda opt=new_name: stim_set_var.set(opt))
                
                # Set the current selection to the newly imported set.
                stim_set_var.set(new_name)
                import_win.destroy()
        
        Button(import_win, text="Add", command=add_stimulus_set).pack(pady=(0, 10))

    def handle_stim_set(*args):
        selection = stim_set_var.get()
        if selection == "Import":
            open_import_window()
        else:
            comp.data["stimulus_set"] = selection

    stim_set_var.trace_add("write", handle_stim_set)

    # ---------- Target Type ----------
    add_label("Target Type")
    target_type_var = tk.StringVar(value=comp.data.get("target_type", "positive"))
    target_type_menu = add_dropdown(target_type_var, ["positive", "negative", "neutral"])  # Save return value here.
    target_type_menu.pack(anchor="w", padx=10, fill="x")
    target_type_var.trace_add("write", lambda *_: comp.data.update({"target_type": target_type_var.get()}))


    # ---------- Selected Target ----------
    add_label("Selected Target")
    selected_target_var = tk.StringVar(value=comp.data.get("selected_target", "Random"))
    selected_target_menu = add_dropdown(selected_target_var, ["Random", "Select from list"])  # Save reference here.
    selected_target_menu.pack(anchor="w", padx=10, fill="x")
    def handle_target_select(*_):
        comp.data["selected_target"] = selected_target_var.get()
        if selected_target_var.get() == "Select from list":
            open_image_selector(comp, target_type_var.get())
    selected_target_var.trace_add("write", handle_target_select)

        # ---------- No Target ----------
    no_target_var = tk.BooleanVar(value=comp.data.get("no_target", False))
    no_target_chk = tk.Checkbutton(left_panel, text="No Target", variable=no_target_var)
    no_target_chk.pack(anchor="w", padx=10, pady=(5, 0))

    # Function to toggle lock status of target type and selected target.
    def toggle_target_lock():
        no_target = no_target_var.get()
        comp.data.update({"no_target": no_target})
        if no_target:
            target_type_menu.config(state="disabled")
            selected_target_menu.config(state="disabled")
        else:
            target_type_menu.config(state="normal")
            selected_target_menu.config(state="normal")

    # Set the initial state based on the value of no_target_var and bind the toggle.
    toggle_target_lock()
    no_target_chk.config(command=toggle_target_lock)

    # ---------- Distractor Type ----------
    add_label("Distractor Type")
    distractor_type_var = tk.StringVar(value=comp.data.get("distractor_type", "positive"))
    dropdown = add_dropdown(distractor_type_var, ["positive", "negative", "neutral"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    distractor_type_var.trace_add("write", lambda *_: comp.data.update({"distractor_type": distractor_type_var.get()}))

    # ---------- Distractor Set ----------
    add_label("Distractor Set")
    distractor_set_var = tk.StringVar(value=comp.data.get("distractor_set", "All"))
    distractor_dropdown = add_dropdown(distractor_set_var, ["All", "Random", "Select set from list"])  # use a unique name for distractor set
    distractor_dropdown.pack(anchor="w", padx=10, fill="x")

    def handle_distractor_set(*args):
        selection = distractor_set_var.get()
        comp.data["distractor_set"] = selection
        if selection == "Select set from list":
            # Call the distractor selector.
            open_distractor_selector(comp, comp.data.get("distractor_type", "positive"))

    distractor_set_var.trace_add("write", handle_distractor_set)


