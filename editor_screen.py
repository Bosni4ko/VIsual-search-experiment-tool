import tkinter as tk
import shutil
import json
import os
from PIL import Image
from tkinter import messagebox
from random import sample
from styles import apply_theme

from component_block import ComponentBlock
from palette import setup_components_palette
from text_editor import setup_text_editor, setup_text_options,save_formatting
from stimulus_editor import setup_stimulus_options
from TEXT_AND_TAGS import NOTIFICATION_DEFAULT_TAGS,END_DEFAULT_TAGS, START_DEFAULT_TAGS
STATE_FILE = "timeline_state.json"

def save_visual_search_experiment(app, base_save_dir, compress_images=True, image_quality=85):
    """
    Save the visual search experiment, including copying used images.
    
    Args:
        app: Application instance with timeline_components.
        base_save_dir: Base directory where the experiment folder will be created.
        compress_images: Whether to compress images when saving.
        image_quality: Quality setting for JPEG compression (1-95).
    """

     # Format experiment folder name
    exp_folder_name = app.saved_exp_name.strip().replace(" ", "_")  # Clean name: replace spaces with underscores
    save_dir = os.path.join(base_save_dir, exp_folder_name)
    # Delete existing folder if it already exists
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir, exist_ok=True)

    # Prepare subfolders for selections and distractors
    selections_dir = os.path.join(save_dir, "selections")
    distractors_dir = os.path.join(save_dir, "distractors")
    os.makedirs(selections_dir, exist_ok=True)
    os.makedirs(distractors_dir, exist_ok=True)

    image_map = {}  # (original_path, destination_folder) -> relative_path
    state = []
    # Iterate through each component in the timeline
    for idx, block in enumerate(app.timeline_components):
        entry = {
            "type": block.component_type,
            "label": block.label_text,
            "color": block.color,
            "index": idx,
        }
        entry["saved_text"] = block.saved_text
        entry["saved_tags"] = block.saved_tags
        # Extract non-transient block data
        raw_data = getattr(block, "data", {}) or {}
        main_data = {k: v for k, v in raw_data.items() if k not in ("last_selections", "last_distractors")}
        entry["data"] = main_data
         # Handle Stimulus-specific last selections & distractors
        if block.component_type == "Stimulus":
             # Process last selections 
            last_sel = raw_data.get("last_selections", {}).copy()
            selected_target_mode = raw_data.get("selected_target", "Random")
            stimulus_set = raw_data.get("stimulus_set", "Faces")
            target_type = raw_data.get("target_type", "positive")
            no_target = raw_data.get("no_target", False)
             # Determine root image directory based on stimulus set
            stim_set = raw_data.get("stimulus_set", "Faces")
            # Randomly pick a target if needed
            if selected_target_mode == "Random" or no_target:
                from random import choice
                if stim_set == "Faces":
                    root_dir = os.path.join("images", "faces")
                elif stim_set == "Images":
                    root_dir = os.path.join("images", "images")
                else:
                    # handle any imported sets you’ve registered on app.imported_stimulus_sets
                    root_dir = app.imported_stimulus_sets.get(stim_set, "")
                base_path = os.path.join(root_dir, target_type)
                if os.path.isdir(base_path):
                    # Walk through base_path and all its subdirectories
                    all_imgs = []
                    # Collect all valid image files
                    for root, dirs, files in os.walk(base_path):
                        for fname in files:
                            if fname.lower().endswith((".jpg", ".jpeg", ".png",".bmp")):
                                all_imgs.append(os.path.join(root, fname))
                    if all_imgs:
                        random_img = choice(all_imgs)
                        last_sel[(stimulus_set, target_type)] = random_img
            # Copy/compress selected images and update entry
            new_last_sel = []
            for key, path in last_sel.items():
                new_path = copy_and_compress_image(
                    path, selections_dir, ("selections",), image_map, compress_images, image_quality
                )
                new_last_sel.append({
                    "stimulus_set": key[0],
                    "stimulus_type": key[1],
                    "path": new_path
                })
            entry["last_selections"] = new_last_sel
            # Process last distractors similarly
            last_dist = raw_data.get("last_distractors", {}).copy()
            distractor_set_mode = raw_data.get("distractor_set", "All")
            distractor_type = raw_data.get("distractor_type", "positive")
            grid_x = raw_data.get("field_x", 10)
            grid_y = raw_data.get("field_y", 10)
            # Reuse root_dir logic
            if stim_set == "Faces":
                root_dir = os.path.join("images", "faces")
            elif stim_set == "Images":
                root_dir = os.path.join("images", "images")
            else:
                root_dir = app.imported_stimulus_sets.get(stim_set, "")

            base_path = os.path.join(root_dir, distractor_type)
            if os.path.isdir(base_path):
                all_imgs = []
                for root, dirs, files in os.walk(base_path):
                    for fname in files:
                        if fname.lower().endswith((".jpg", ".jpeg", ".png",".bmp")):
                            all_imgs.append(os.path.join(root, fname))
                if distractor_set_mode == "Random":
                    total_needed = max(0, grid_x * grid_y - 1)
                    if len(all_imgs) >= total_needed:
                        random_set = sample(all_imgs, total_needed)
                        last_dist[(stimulus_set, distractor_type)] = random_set
                elif distractor_set_mode == "All":
                    last_dist[(stimulus_set, distractor_type)] = all_imgs

            new_last_dist = []
            for key, paths in last_dist.items():
                new_paths = [
                    copy_and_compress_image(
                        p, distractors_dir, ("distractors",), image_map, compress_images, image_quality
                    )
                    for p in paths
                ]
                new_last_dist.append({
                    "stimulus_set": key[0],
                    "distractor_type": key[1],
                    "paths": new_paths
                })
            entry["last_distractors"] = new_last_dist

        # Handle attachment if any
        if block.component_type == "Stimulus notification" and block.attachment:
            entry["attachment"] = {
                "label": block.attachment.label_text,
                "color": block.attachment.color,
                "index": app.timeline_components.index(block.attachment)
            }

        state.append(entry)

    # Save the final JSON
    state_file = os.path.join(save_dir, "experiment_state.json")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    # --- New: Copy create_screen_state.json ---
    try:
        if os.path.exists("create_screen_state.json"):
            shutil.copy2("create_screen_state.json", save_dir)
        else:
            print("Warning: create_screen_state.json not found, skipping copy.")
    except Exception as e:
        print(f"Error copying create_screen_state.json: {e}")

def copy_and_compress_image(original_path, dest_dir, folder_tag, image_map, compress_images, image_quality):
    """
    Copy and optionally compress an image.
    Keeps track of already-copied images to avoid duplicates.
    
    folder_tag: ("selections",) or ("distractors",) - used to separate images.
    """
    map_key = (original_path, folder_tag)

    if map_key in image_map:
        return image_map[map_key]

    filename = os.path.basename(original_path)
    save_path = os.path.join(dest_dir, filename)

    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Image not found: {original_path}")

    if compress_images:
        try:
            with Image.open(original_path) as img:
                img.save(save_path, format="JPEG", quality=image_quality, optimize=True)
        except Exception as e:
            print(f"Compression failed for {original_path}, falling back to copy. Error: {e}")
            shutil.copy2(original_path, save_path)
    else:
        shutil.copy2(original_path, save_path)

    # Relative path saved in JSON
    relative_path = os.path.join(folder_tag[0], filename)
    image_map[map_key] = relative_path
    return relative_path

def save_timeline_state(app):
    # Commit any in‑progress Text edits
    sel = getattr(app, "selected_component", None)
    if sel and sel.component_type in ["Text", "Stimulus notification", "End", "Start"]:
        try:
            save_formatting(sel)
        except Exception:
            pass
    # --- commit formatting of *all* text-like components 
    for block in app.timeline_components:
        if block.component_type in ["Text", "Stimulus notification", "Start", "End"]:
            try:
                save_formatting(block)
            except Exception:
                pass
    state = []
    for idx, block in enumerate(app.timeline_components):
        entry = {
            "type": block.component_type,
            "label": block.label_text,
            "color": block.color,
            "index": idx,
        }
        entry["saved_text"] = block.saved_text
        entry["saved_tags"] = block.saved_tags

        raw_data = getattr(block, "data", {}) or {}
        # main data sans transient maps
        main_data = {k: v for k, v in raw_data.items()
                     if k not in ("last_selections", "last_distractors")}
        entry["data"] = main_data

        # serialize last_selections as list to avoid tuple keys
        last_sel = raw_data.get("last_selections", {})
        entry["last_selections"] = [
            {"stimulus_set": key[0],
             "stimulus_type": key[1],
             "path": value}
            for key, value in last_sel.items()
        ]
        # serialize last_distractors similarly
        last_dist = raw_data.get("last_distractors", {})
        entry["last_distractors"] = [
            {"stimulus_set": key[0],
             "distractor_type": key[1],
             "paths": value}
            for key, value in last_dist.items()
        ]

        # Include attachment information for Stimulus notification
        if block.component_type == "Stimulus notification" and block.attachment:
            entry["attachment"] = {
                "label": block.attachment.label_text,
                "color": block.attachment.color,
                "index": app.timeline_components.index(block.attachment)
            }

        state.append(entry)

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def load_timeline_state(app):
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    app.timeline_components.clear()
    block_map = {}  # Track all blocks by original index
    attachment_pairs = []  # Store (notification_index, stimulus_index) pairs

    # First pass: create all components and record attachments
    for item in sorted(state, key=lambda x: x["index"]):
        # Skip creating notification components for now, just record them
        if item["type"] == "Stimulus notification":
            attachment_info = item.get("attachment")
            if attachment_info:
                attachment_pairs.append((item["index"], attachment_info["index"]))
            continue
            
        # Create non-notification components
        app.insert_component(
            label=item["label"],
            color=item["color"],
            component_type=item["type"]
        )
        block = app.timeline_components[-1]

        block.saved_text = item.get("saved_text", "")
        block.saved_tags = item.get("saved_tags", [])

        # Restore main data
        block.data = item.get("data", {})
        # Rebuild last_selections map with tuple keys
        block.data["last_selections"] = {}
        for rec in item.get("last_selections", []):
            key = (rec.get("stimulus_set"), rec.get("stimulus_type"))
            block.data["last_selections"][key] = rec.get("path")

        # Rebuild last_distractors map
        block.data["last_distractors"] = {}
        for rec in item.get("last_distractors", []):
            key = (rec.get("stimulus_set"), rec.get("distractor_type"))
            block.data["last_distractors"][key] = rec.get("paths")

        block_map[item["index"]] = block

    # Second pass: create notification components and establish attachments
    for item in sorted(state, key=lambda x: x["index"]):
        if item["type"] != "Stimulus notification":
            continue
            
        # Find the original position where this notification should be inserted
        original_index = item["index"]
        
        # Create the notification component
        notification = ComponentBlock(
            app,
            app.timeline_container,
            item["label"],
            item["color"],
            x=0,  # Position will be fixed during render
            y=10,
            from_timeline=True,
            component_type="Stimulus notification"
        )
        notification.saved_text = item.get("saved_text", "")
        notification.saved_tags = item.get("saved_tags", [])
        # Insert at the original position
        app.timeline_components.insert(original_index, notification)
        block_map[original_index] = notification

        # Find and attach to the stimulus component
        attachment_info = item.get("attachment")
        if attachment_info and attachment_info["index"] in block_map:
            stimulus = block_map[attachment_info["index"]]
            notification.attachment = stimulus
            stimulus.attachment = notification

def show_editor_screen(app):
    app.clear_screen()
    app.timeline_components = []
    app.timeline_spacing = 120  # horizontal space between blocks
    app.selected_component = None

   # Create a canvas that will act as a horizontally scrollable container
    timeline_canvas = tk.Canvas(app.root, bg="white", bd=2, relief="flat", height=140)
    app.root.update_idletasks()  
    curr_h = app.root.winfo_height()
    # prevent the user from ever resizing the window smaller than this
    app.root.minsize(800, curr_h)
    timeline_canvas.place(relx=0.025, rely=0.75, relwidth=0.7, height=120)

    # Create a horizontal scrollbar linked to the canvas
    scrollbar = tk.Scrollbar(app.root, orient="horizontal", command=timeline_canvas.xview)
    scrollbar.place(relx=0.025, y=timeline_canvas.winfo_y() + 140, relwidth=0.7, height=15)
    timeline_canvas.configure(xscrollcommand=scrollbar.set)
    app.scrollbar = scrollbar

    canvas_height = int(timeline_canvas['height'])
    timeline_container = tk.Frame(timeline_canvas, bg="white", width=580, height=canvas_height)
    timeline_canvas.create_window((10, 0), window=timeline_container, anchor="nw")
    def on_root_resize(event):
        # canvas keeps its fixed 140px height,
        # so scrollbar always sits right below it
        if not timeline_canvas.winfo_exists():
            return
        y_pixel = timeline_canvas.winfo_y() + timeline_canvas.winfo_height()
        app.scrollbar.place_configure(y=y_pixel)

    # bind once, after creating the widgets:
    app.root.bind("<Configure>", on_root_resize)

    # bind once, after creating the widgets:
    app.root.bind("<Configure>", on_root_resize)
    # Update the scroll region whenever the size of timeline_container changes
    timeline_container.bind(
        "<Configure>",
        lambda e: timeline_canvas.configure(scrollregion=timeline_canvas.bbox("all"))
    )
    def _is_in_timeline(widget):
    # climb the master chain looking for our timeline widgets
        while widget:
            if widget in (app.timeline_canvas, app.scrollbar, app.timeline_container):
                return True
            widget = getattr(widget, "master", None)
        return False
    def _on_mousewheel(event):
        if not _is_in_timeline(event.widget):
            # not over timeline → do nothing, let other widgets scroll
            return

        canvas = app.timeline_canvas
        units = -1 * (event.delta // 120)

        lo, hi = canvas.xview()
        if (units < 0 and lo <= 0.0) or (units > 0 and hi >= 1.0):
            # at one edge → eat the event so you can’t drift past
            return "break"

        canvas.xview_scroll(units, "units")
        return "break"


    app.root.bind_all("<MouseWheel>", _on_mousewheel)

    app.timeline_canvas = timeline_canvas
    app.timeline_container = timeline_container
    def update_timeline_container_size():
        # 1) Force geometry update
        app.timeline_container.update_idletasks()

        # 2) Compute needed inner-frame width
        max_w = 100
        for child in app.timeline_container.winfo_children():
            x, w = child.winfo_x(), child.winfo_width()
            max_w = max(max_w, x + w)
        new_w = max_w + 20
        app.timeline_container.config(width=new_w)

        # 3) Update scrollregion
        canvas    = app.timeline_canvas
        scrollbar = app.scrollbar
        canvas.configure(scrollregion=canvas.bbox("all"))

        # 4) Show/hide scrollbar & set can_scroll
        bbox = canvas.bbox("all") or (0, 0, 0, 0)
        content_w = bbox[2] - bbox[0]
        visible_w = canvas.winfo_width()

        if content_w <= visible_w:
            # nothing to scroll
            app.can_scroll = False
            scrollbar.place_forget()
            canvas.xview_moveto(0)
        else:
            # overflow → enable scroll
            app.can_scroll = True
            y = canvas.winfo_y() + canvas.winfo_height()  # always 140px below top
            scrollbar.place(relx=0.025, y=y, relwidth=0.7, height=15)


    # Function to render timeline content horizontally
    def render_timeline():
    # Iterate over 15 items or however many rectangles you want to add.
        update_timeline_container_size()
        # Iterate over each timeline component and position it inside the scrollable container.
        for i, block in enumerate(app.timeline_components):
            # Place each block in the timeline container using absolute positioning.
            block.place(in_=app.timeline_container, x=i * app.timeline_spacing, y=10)
            # If the block is from the timeline and has an entry widget, position it as well.
            if block.from_timeline and hasattr(block, 'name_entry'):
                block.name_entry.place(in_=app.timeline_container, x=i * app.timeline_spacing,  y=10 + block.label_offset_y, width=block.winfo_width())
        update_timeline_container_size()
    
    render_timeline()
    app.render_timeline= render_timeline

    setup_components_palette(app)

    # Define the overall area for the two regions (example values as before)
    overall_relx = 0.025
    overall_rely = 0.025
    overall_relwidth = 0.7
    overall_relheight = 0.65
    left_panel_relwidth = overall_relwidth * (1/3)
    gap = 0.02

    # Place the left panel
    left_panel = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    left_panel.place(relx=overall_relx, rely=overall_rely, relwidth=left_panel_relwidth, relheight=overall_relheight)

    # Place the main panel (for text editing)
    main_panel_relx = overall_relx + left_panel_relwidth + gap
    main_panel_relwidth = overall_relwidth - left_panel_relwidth - gap
    main_panel = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    main_panel.place(relx=main_panel_relx, rely=overall_rely, relwidth=main_panel_relwidth, relheight=overall_relheight)
    style = apply_theme(app.root)
    # This function is used to mark a component as selected and set up the editor panels accordingly.
    def select_component(comp):
        prev = getattr(app, 'selected_component', None)
        # only save if previous Text block is still in the timeline
        if prev and prev.component_type in ["Text", "Stimulus notification", "Start","End"] and prev in app.timeline_components:
            try:
                save_formatting(prev)
            except tk.TclError:
                # underlying Text widget was already destroyed
                pass 
        
        save_timeline_state(app)
            # --- Remove highlight from previous ---
        if prev:
            prev.configure(highlightbackground="white", highlightthickness=0)

        app.selected_component = comp

        # --- Highlight the new one ---
        comp.configure(highlightbackground="blue", highlightthickness=3)
        # Clear the left and main panels
        for widget in left_panel.winfo_children():
            widget.destroy()
        for widget in main_panel.winfo_children():
            widget.destroy()
        if comp.component_type in ["Text", "Stimulus notification", "Start", "End"]:
            # If it's a Stimulus notification, set up default text if empty
            if comp.component_type == "Stimulus notification":
                if not hasattr(comp, 'saved_text') or not comp.saved_text:
                    comp.saved_text = app.tr("notification_default_text")
                    comp.saved_tags = NOTIFICATION_DEFAULT_TAGS.get(app.current_language, NOTIFICATION_DEFAULT_TAGS["EN"])
            elif comp.component_type == "Start":
                if not hasattr(comp, 'saved_text') or not comp.saved_text:
                    comp.saved_text = app.tr("start_default_text")
                    comp.saved_tags = START_DEFAULT_TAGS.get(app.current_language, START_DEFAULT_TAGS["EN"])
            elif comp.component_type == "End":
                if not hasattr(comp, 'saved_text') or not comp.saved_text:
                    comp.saved_text = app.tr("end_default_text")
                    comp.saved_tags = END_DEFAULT_TAGS.get(app.current_language, END_DEFAULT_TAGS["EN"])  
            setup_text_editor(app, main_panel, comp)
            setup_text_options(app, left_panel, comp)

        elif comp.component_type == "Stimulus":
            setup_stimulus_options(app, left_panel,main_panel, comp)
        else:
            tk.Label(main_panel, text="No text options available for this component").pack()


    app.select_component = select_component  # Make the function accessible to ComponentBlock.on_drop

    def reorder_component(component):
        x = component.winfo_x()
        new_index = x // app.timeline_spacing
        new_index = max(0, min(new_index, len(app.timeline_components) - 1))
        current_index = app.timeline_components.index(component)
        component_type = component.component_type
        # Prevent Start from being moved
        if component_type == "Start" and new_index != 0:
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Prevent End from being moved
        if component_type == "End" and new_index != len(app.timeline_components) - 1:
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Prevent dropping into position 0 (reserved for Start)
        if new_index == 0 and component.component_type != "Start" and component.component_type != "Stimulus notification" and component.component_type != "Stimulus":
            new_index = 1  # force move to second slot
            # Move to corrected position in list
            app.timeline_components.remove(component)
            app.timeline_components.insert(new_index, component)
            # Rerender all components
            render_timeline()
            return

        # Prevent dropping after End
        if len(app.timeline_components) > 0:
            last = app.timeline_components[-1]
            if last.component_type == "End" and new_index >= len(app.timeline_components) - 1:
                if component.component_type != "End":  # End is already protected above
                    component.place(x=current_index * app.timeline_spacing, y=10)
                    component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
                    return
        # Prevent placing between Stimulus and its attached Notification
        for i in range(len(app.timeline_components) - 1):
            first = app.timeline_components[i]
            second = app.timeline_components[i + 1]

            if first.component_type == "Stimulus notification" and \
            second.component_type == "Stimulus" and \
            second.attachment == first and i <= new_index < i+1:
                if component in app.timeline_components:
                    current_index = app.timeline_components.index(component)
                    app.timeline_components.remove(component)
                    # Adjust insertion index if component was before the pair
                    if current_index <= i:
                        i -= 1
                        
                app.timeline_components.insert(i, component)
                # Rerender after safe insert
                render_timeline()
                return
        if component not in app.timeline_components:
            return

        if component_type == "Stimulus notification":
            # Search for Stimulus directly after intended drop position
            if new_index < len(app.timeline_components):
                candidate = app.timeline_components[new_index + 1]
                if candidate.component_type == "Stimulus" and candidate.attachment is None:
                    # Detach from previous stimulus if attached
                    if component.attachment:
                        component.attachment.attachment = None

                    # Attach to new Stimulus
                    candidate.attachment = component
                    component.attachment = candidate  # Keep track on the notification too if needed
                    # Adjust new_index if component came from later in the list
                    if new_index < current_index:
                        new_index += 1
                    app.timeline_components.remove(component)
                    app.timeline_components.insert(new_index, component)

                    render_timeline()
                    return
                else:
                    print("Stimulus notification can only be moved before a free Stimulus.")
            else:
                print("Drop must be before a Stimulus.")

            # Restore previous position
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Stimulus with notification — move both together
        if component_type == "Stimulus" and component.attachment:
            notification = component.attachment
            # Remove both components (if they exist)
            if notification in app.timeline_components:
                app.timeline_components.remove(notification)
            if component in app.timeline_components:
                app.timeline_components.remove(component)

            # Special Case: drop to the end (before End)
            if len(app.timeline_components) > 0 and \
            app.timeline_components[-1].component_type == "End" and \
            new_index >= len(app.timeline_components):
                new_index = len(app.timeline_components) - 1

            else:
                # Adjust index if component was moved forward
                if new_index > current_index:
                    new_index -= 1 
                if new_index < current_index:
                    new_index += 1 
                new_index = max(1, min(new_index, len(app.timeline_components)))

            # Insert both in order
            app.timeline_components.insert(new_index, notification)
            app.timeline_components.insert(new_index + 1, component)

            # Rerender
            render_timeline()
            return

        if new_index < current_index:
                    new_index += 1 
        # Normal move for other components
        app.timeline_components.remove(component)
        app.timeline_components.insert(new_index, component)

        # Rerender
        render_timeline()

    app.timeline_container.reorder_component = reorder_component

    def insert_component(label, color, component_type, index=None ):
        if index == None: 
            index = len(app.timeline_components)

        # Prevent duplicates
        if component_type == "Start" and any(b.component_type == "Start" for b in app.timeline_components):
            print("Only one Start allowed.")
            return
        if component_type == "End" and any(b.component_type == "End" for b in app.timeline_components):
            print("Only one End allowed.")
            return

        # Enforce Start at beginning
        if component_type == "Start":
            index = 0
            for i in range(len(app.timeline_components)):
                block = app.timeline_components[i]
                block.place(x=(i + 1) * app.timeline_spacing, y=10)
                if block.from_timeline:
                    block.name_entry.place(x=(i + 1) * app.timeline_spacing, y=75)

        # Enforce End at the end
        elif component_type == "End":
            index = len(app.timeline_components)

        # For others, insert before End if it exists
        else:
            for i, block in enumerate(app.timeline_components):
                if (block.component_type == "End" and index > i):
                    index = i
                    break
        if component_type == "Stimulus notification":
            # Find the first Stimulus with no attachment
            for i, block in enumerate(app.timeline_components):
                if block.component_type == "Stimulus" and block.attachment is None:
                    stimulus_block = block
                    stimulus_index = i
                    break
            else:
                print("No available Stimulus for notification.")
                return

            # Create the notification and attach it
            notification = ComponentBlock(
                app,
                app.timeline_container,
                label,
                color,
                x=stimulus_index * app.timeline_spacing,
                y=10,
                from_timeline=True,
                attachment=stimulus_block,
                component_type = component_type
            )

            stimulus_block.attachment = notification

            app.timeline_components.insert(stimulus_index, notification)

            # Rerender
            render_timeline()
            #app.select_component(notification) 
            return 
        
        if index == 0 and component_type != "Start":
            index = 1
        # Create and insert block
        new_block = ComponentBlock(app,app.timeline_container, label, color, x=index * app.timeline_spacing, y=10, from_timeline=True,component_type=component_type)
        app.timeline_components.insert(index, new_block)

        # Rerender
        render_timeline()
        #app.select_component(new_block)

    app.insert_component = insert_component
    load_timeline_state(app)

    render_timeline()
    # after loading & initial render, add Start only if JSON didn't have one
    if not any(b.component_type == "Start" for b in app.timeline_components):
        start_block = ComponentBlock(
            app, app.timeline_container,
            "Start", "green",
            x=0, y=10,
            from_timeline=True,
            component_type="Start"
        )
        app.timeline_components.insert(0, start_block)
        start_block.name_entry.place(
            x=0,
            y=10 + start_block.label_offset_y,
            width=start_block.winfo_width()
        )
        render_timeline()

    def on_create():
        # Save any pending text formatting
        sel = getattr(app, "selected_component", None)
        if sel and sel.component_type in ["Text", "Stimulus notification", "Start", "End"]:
            try:
                save_formatting(sel)
            except Exception:
                pass
        answer = messagebox.askyesno("Confirm", "Are you sure you want to create the experiment?")
        if answer:
            save_visual_search_experiment(app, app.saved_save_location)
            messagebox.showinfo("Success", "Experiment created successfully!")

    app.root.update_idletasks()
    base_rely = 0.75      # that’s where your timeline starts
    step      = 0.05     # gap
    def style_button(btn,
                    bg="#f8f8f8",
                    fg="#333333",
                    activebg="#e0e0e0",
                    activefg="#333333",
                    bd=1,
                    relief="raised",
                    font=("Segoe UI", 14, "bold")):
        btn.configure(
            bg=bg,
            fg=fg,
            activebackground=activebg,
            activeforeground=activefg,
            bd=bd,
            relief=relief,
            font=font,
            highlightthickness=0,
            cursor="hand2",
        )
        def on_enter(e):
            btn['bg'] = activebg
        def on_leave(e):
            btn['bg'] = bg
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # uniform font for all
    COMMON_FONT = ("Segoe UI", 14, "bold")

    create_button = tk.Button(app.root, text=app.tr("create"), font=("Segoe UI", 12), bg="#fef6f6", width=12, command=on_create)
    h = create_button.winfo_reqheight()  # button’s height
    style_button(
        create_button,
        bg="#fef6f6",
        activebg="#d0f0d0",      # light green on hover
        font=COMMON_FONT
    )
    create_button.place(
        relx=0.82, rely=base_rely,
        relwidth=0.15, relheight=0.055
    )


# --- Added: removal logic and button ---
    def remove_selected_component():
        comp = getattr(app, 'selected_component', None)
        if not comp or comp.component_type == "Start":
            return  # nothing to remove or protected

        # If removing a Stimulus with a notification, delete the notification too
        if comp.component_type == "Stimulus" and getattr(comp, 'attachment', None):
            notif = comp.attachment
            if notif in app.timeline_components:
                app.timeline_components.remove(notif)
                notif.destroy()
                if hasattr(notif, 'name_entry'):
                    notif.name_entry.destroy()
            comp.attachment = None

        # If removing a Stimulus notification, detach it from its Stimulus
        if comp.component_type == "Stimulus notification" and getattr(comp, 'attachment', None):
            stim = comp.attachment
            stim.attachment = None

        # Remove the component itself
        if comp in app.timeline_components:
            app.timeline_components.remove(comp)
        comp.destroy()
        if hasattr(comp, 'name_entry'):
            comp.name_entry.destroy()
        app.selected_component = None

        # --- Clear editing panels ---
        for widget in left_panel.winfo_children():
            widget.destroy()
        for widget in main_panel.winfo_children():
           widget.destroy()
        render_timeline()

    remove_button = tk.Button(
        app.root,
        text="Remove",
        font=("Segoe UI", 12),
        bg="#fdecea",
        width=12,
        command=remove_selected_component
    )
    style_button(
        remove_button,
        bg="#fdecea",            # light red base
        fg="#a94442",            # dark red text
        activebg="#f8d7da",      # richer red on hover
        activefg="#a94442",
        font=COMMON_FONT
    )
    remove_button.place(
        relx=0.82, rely=base_rely + step,
        relwidth=0.15, relheight=0.055
    )
    # --- end added ---
    
    # Back buttton
    def on_back():
        save_timeline_state(app)
        app.show_create_screen()

    back_btn = tk.Button(app.root, text="←", font=("Arial", 16), bg="#fef6f6", command=on_back)
    style_button(
        back_btn,
        bg="#fef6f6",
        activebg="#e0e0e0",
        font=COMMON_FONT
    )
    back_btn.place(
        relx=0.82, rely=base_rely + 2*step,
        relwidth=0.15, relheight=0.055
    )