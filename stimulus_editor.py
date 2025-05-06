import tkinter as tk
from tkinter import ttk
import os
from tkinter import Toplevel, Scrollbar, Label, Button, filedialog
from PIL import Image, ImageTk
from grid import setup_field_grid
from styles import BG_COLOR, CANVAS_BG, ACCENT_COLOR, SMALL_TEXT_FONT, LABEL_FONT
MAX_GRID_SIZE = 10
MIN_GRID_SIZE = 2
def open_media_selector(comp, kind, sel_type, app, multi_select=False):
    stimulus_set = comp.data.get("stimulus_set", "Faces")
    imported_sets = comp.data.get("imported_stimulus_sets", {})
    if stimulus_set not in ("Faces","Images") and stimulus_set not in imported_sets:
        return
    if stimulus_set == "Faces":
        base_path = os.path.join("images","faces")
    elif stimulus_set == "Images":
        base_path = os.path.join("images","images")
    else:
        base_path = imported_sets[stimulus_set]

    if sel_type not in ("positive","neutral","negative"):
        return
    def get_categories(bp, fld):
        d = os.path.join(bp, fld)
        if os.path.isdir(d):
            subs = [x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))]
            return {s: os.path.join(d,s) for s in subs} if subs else {fld: d}
        return {}
    categories = get_categories(base_path, sel_type)

    win = Toplevel()
    win.configure(bg=BG_COLOR)
    win.geometry("900x650")
    win.image_refs = []

    # one blank thumbnail
    THUMB_SIZE = (90,90)
    blank = Image.new("RGB", THUMB_SIZE, CANVAS_BG)
    blank_tk = ImageTk.PhotoImage(blank)

    win.image_refs.append(blank_tk)

    key_tuple = (stimulus_set, sel_type)
    if multi_select:
        prev = comp.data.get("last_distractors", {}).get(key_tuple, [])
        sel = set(prev)
    else:
        prev = comp.data.get("last_selections", {}).get(key_tuple)
        sel = {prev} if prev is not None else set()
    last_click_key = None
            
    # header & info
    hdr = ttk.Frame(win, style="TFrame", height=50)
    hdr.pack(fill="x")

    def _finish():
        key = (stimulus_set, sel_type)
        if multi_select:
            comp.data.setdefault("last_distractors", {})[key] = list(sel)
        else:
            comp.data.setdefault("last_selections", {})[key] = next(iter(sel))
        win.destroy()

    # 2) Title label fills the rest of the header
    ttk.Label(
        hdr,
        text=app.tr("image_selector_title").format(type=sel_type.capitalize()),
        font=LABEL_FONT,
        background=ACCENT_COLOR,
        foreground="white",
        padding=(15,10)
    ).pack(side="left", fill="x", expand=True)
        # — Button row
    btn_row = ttk.Frame(win, style="TFrame")
    btn_row.pack(fill="x", padx=15, pady=(5,10))

    ttk.Button(
        btn_row,
        text=app.tr("cancel"),
        style="Media.Cancel.TButton",
        command=win.destroy
    ).pack(side="left", padx=(0,5))

    ttk.Button(
        btn_row,
        text=app.tr("button_confirm"),
        style="Media.Confirm.TButton",
        command=_finish
    ).pack(side="left")

    info_var = tk.StringVar(master=win)
    if multi_select:
        cnt = len(sel)
        info_var.set(
            f"{cnt} images selected" if cnt else app.tr("No image selected.")
        )
    else:
        if sel and next(iter(sel)):
            name = os.path.basename(next(iter(sel)))
            info_var.set(app.tr("selected_label").format(name=name))
        else:
           info_var.set(app.tr("No image selected."))

    ttk.Label(win, textvariable=info_var,
              font=LABEL_FONT, background=BG_COLOR)\
       .pack(fill="x", padx=15, pady=(5,0))
    # canvas + scrollbar
    canvas = tk.Canvas(win, bg=CANVAS_BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True, padx=(15,0), pady=10)
    sb = Scrollbar(win, orient="vertical", command=canvas.yview)
    sb.pack(side="left", fill="y", pady=10)

    def on_yscroll(*args):
        sb.set(*args)
        schedule_load()
    canvas.configure(yscrollcommand=on_yscroll)

    content = ttk.Frame(canvas, style="TFrame")
    canvas.create_window((0,0), window=content, anchor="nw")
    content.bind("<Configure>", lambda e: (canvas.configure(scrollregion=canvas.bbox("all")), schedule_load()))

    def _on_mousewheel(event):
        # Windows, macOS
        delta = event.delta
        canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        schedule_load()

        # bind when mouse enters/exits the canvas region
    canvas.bind("<Enter>", lambda e: (
        canvas.bind_all("<MouseWheel>", _on_mousewheel),
    ))
    canvas.bind("<Leave>", lambda e: (
        canvas.unbind_all("<MouseWheel>"),
        canvas.unbind_all("<Button-4>"),
        canvas.unbind_all("<Button-5>")
    ))
    # lazy-loading state
    placeholders = {}   # (cat,idx) -> {"frame", "label", "path"}
    all_keys = []       # flat list in display order
    loaded = set()
    load_queue = []
    load_scheduled = False

    def is_visible(frame):
        try:
            t, b = frame.winfo_rooty(), frame.winfo_rooty() + frame.winfo_height()
            ct, cb = canvas.winfo_rooty(), canvas.winfo_rooty() + canvas.winfo_height()
            return b > ct and t < cb
        except tk.TclError:
            return False

    def schedule_load():
        nonlocal load_scheduled
        if load_scheduled: return
        load_scheduled = True
        win.after(50, do_load_pass)

    def do_load_pass():
        nonlocal load_scheduled
        load_scheduled = False
        # queue newly-visible
        load_queue[:] = [
            k for k,v in placeholders.items()
            if k not in loaded and is_visible(v["frame"])
        ]
        # load up to 5 per pass
        for _ in range(min(5, len(load_queue))):
            key = load_queue.pop(0)
            v = placeholders[key]
            img = Image.open(v["path"]).convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            win.image_refs.append(tkimg)
            v["label"].config(image=tkimg)
            loaded.add(key)
        if load_queue:
            schedule_load()

    last_click_key = None

    def on_click(event, path, key, frame):
        nonlocal last_click_key
        # simple toggle
        if multi_select:
            if path in sel:
                sel.remove(path); frame.config(bg=CANVAS_BG)
            else:
                sel.add(path); frame.config(bg=ACCENT_COLOR)
            info_var.set(f"{len(sel)} images selected")
        else:
            old = next(iter(sel), None)
            if old:
                for v in placeholders.values():
                    if v["path"] == old:
                        v["frame"].config(bg=CANVAS_BG)
            sel.clear(); sel.add(path)
            frame.config(bg=ACCENT_COLOR)
            info_var.set(app.tr("selected_label").format(name=os.path.basename(path)))
        last_click_key = key
        schedule_load()

    def on_shift_click(event, path, key, frame):
        nonlocal last_click_key
        if not multi_select or last_click_key is None or last_click_key not in all_keys:
            return on_click(event, path, key, frame)
        i1 = all_keys.index(last_click_key)
        i2 = all_keys.index(key)
        lo, hi = sorted((i1, i2))
        # decide: are we selecting (if new not in sel) or deselecting (if new in sel)?
        selecting = path not in sel
        for k in all_keys[lo:hi+1]:
            p = placeholders[k]["path"]
            f = placeholders[k]["frame"]
            if selecting and p not in sel:
                sel.add(p); f.config(bg=ACCENT_COLOR)
            elif not selecting and p in sel:
                sel.remove(p); f.config(bg=CANVAS_BG)
        last_click_key = key
        if multi_select:
            info_var.set(f"{len(sel)} images selected")
        else:
            info_var.set(app.tr("selected_label").format(name=os.path.basename(path)))
        schedule_load()

    # build placeholders & bindings
    cols = 8
    for cat, folder in categories.items():
        ttk.Label(content, text=cat.capitalize(),
                  font=SMALL_TEXT_FONT, background=CANVAS_BG)\
           .pack(anchor="w", pady=(10,0), padx=5)

        grid = ttk.Frame(content, style="TFrame")
        grid.pack(anchor="w", padx=5, pady=(0,10))

        files = [f for f in os.listdir(folder)
                 if f.lower().endswith((".jpg",".png",".jpeg",".bmp",".gif"))]
        for i, name in enumerate(files):
            path = os.path.join(folder, name)
            key = (cat, i)
            all_keys.append(key)

            r, c = (i//cols)*2, i%cols
            frm = tk.Frame(grid, width=100, height=100,
                           bg=CANVAS_BG, bd=1, relief="solid")
            frm.grid_propagate(False)
            frm.grid(row=r, column=c, padx=5, pady=5)

            lbl = tk.Label(frm, image=blank_tk, bg=CANVAS_BG)
            lbl.place(relx=0.5, rely=0.5, anchor="center")

            caption = tk.Label(grid, text=name, wraplength=90,
                               bg=CANVAS_BG, font=SMALL_TEXT_FONT)
            caption.grid(row=r+1, column=c, padx=5, pady=(2,5))

            for seq, handler in (("<Button-1>", on_click),
                     ("<Shift-Button-1>", on_shift_click)):
                frm.bind(seq,
                    lambda e, p=path, k=key, f=frm, h=handler: h(e, p, k, f)
                )
                lbl.bind(seq,
                    lambda e, p=path, k=key, f=frm, h=handler: h(e, p, k, f)
                )

            placeholders[key] = {"frame":frm, "label":lbl, "path":path}
            if path in sel:
                frm.config(bg=ACCENT_COLOR)
    schedule_load()


def open_image_selector(comp, target_type, app):
    open_media_selector(comp, "Target", target_type, app, multi_select=False)

def open_distractor_selector(comp, distractor_type, app):
    open_media_selector(comp, "Distractor", distractor_type, app, multi_select=True)

def setup_stimulus_options(app, left_panel,main_panel,comp):
    def add_label(text, pady=8):
        label = ttk.Label(left_panel, text=text, style="Small.TLabel")
        label.pack(anchor="w", padx=10, pady=(pady, 2))
        return label


    def add_dropdown(var, options):
        return ttk.Combobox(
            left_panel,
            textvariable=var,
            values=options,
            state="readonly",
            style="Small.TCombobox",
        )
    

    # ---------- Field Size ----------
    add_label(app.tr("field_size_label"))
    field_frame = ttk.Frame(left_panel)
    field_frame.pack(anchor="w", padx=10)

    field_x = ttk.Entry(field_frame, width=5, style="TEntry")
    field_y = ttk.Entry(field_frame, width=5, style="TEntry")
    field_x.insert(0, str(comp.data.get("field_x", 10)))
    field_y.insert(0, str(comp.data.get("field_y", 10)))

    field_x.pack(side="left")
    ttk.Label(field_frame, text="  X  ", style="Small.TLabel").pack(side="left")
    field_y.pack(side="left")

    def save_field_size(*_):
        # read raw
        # --- store old values so we only redraw on real change ---
        old_x = comp.data.get("field_x", 10)
        old_y = comp.data.get("field_y", 10)
    
        try:
            raw_x = int(field_x.get())
            raw_y = int(field_y.get())
        except ValueError:
            # non‑integer → reset UI to old and skip redraw
            field_x.delete(0, "end")
            field_x.insert(0, str(comp.data.get("field_x", 10)))
            field_y.delete(0, "end")
            field_y.insert(0, str(comp.data.get("field_y", 10)))
            return

        # clamp to [2,20]
        x = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, raw_x))
        y = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, raw_y))

        # if they typed out-of-bounds, reset the entries to the clamped values
        if raw_x != x:
            field_x.delete(0, "end")
            field_x.insert(0, str(x))
        if raw_y != y:
            field_y.delete(0, "end")
            field_y.insert(0, str(y))

        # save and rebuild
        # only save & redraw if something actually changed
        if x != old_x or y != old_y:
            comp.data["field_x"] = x
            comp.data["field_y"] = y
            setup_field_grid(main_panel, comp)
            update_amount_input() 

    # bind on focus‑out
    field_x.bind("<FocusOut>", save_field_size)
    field_y.bind("<FocusOut>", save_field_size)

    # initial draw
    setup_field_grid(main_panel, comp)

    # helper to clamp a value into [lo, hi]
    def clamp(val, lo, hi):
        return max(lo, min(val, hi))

    # --------- Stimulus Set Size ----------
    add_label(app.tr("stimulus_set_size_label"))
    size_var = tk.StringVar(value=comp.data.get("stimulus_size_mode", "random"))
    size_menu = ttk.Combobox(left_panel, textvariable=size_var, values=["random", "fixed", "random in range"], state="readonly", style="Small.TCombobox")
    size_menu.pack(anchor="w", padx=10, fill="x")

    amount_frame = ttk.Frame(left_panel)
    amount_frame.pack(anchor="w", padx=10, pady=(5, 0))

    def update_amount_input(*args):
        # wipe out any old widgets
        for w in amount_frame.winfo_children():
            w.destroy()

        mode = size_var.get()
        comp.data["stimulus_size_mode"] = mode

        ttk.Label(amount_frame, text=app.tr("amount_label"), style="Small.TLabel").pack(side="left", padx=(0, 5))

        # the maximum possible stimuli
        total = comp.data.get("field_x", 10) * comp.data.get("field_y", 10)

        if mode == "random":
            # readonly dash, then rebuild grid
            dash = ttk.Entry(amount_frame, width=7, state="readonly", justify="center", style="TEntry")
            dash.insert(0, "-")
            dash.pack(side="left")
            setup_field_grid(main_panel, comp)

        elif mode == "fixed":
            # show an entry for fixed amount
            amt_e = ttk.Entry(amount_frame, width=7, style="Small.TEntry")
            amt_e.insert(0, str(comp.data.get("fixed_amount", 2)))
            amt_e.pack(side="left")

            def save_fixed(event=None):
                # parse or fallback
                old = comp.data.get("fixed_amount", 2)
                try:
                    raw = int(amt_e.get())
                except ValueError:
                    raw = comp.data.get("fixed_amount", 2)
                # clamp into [2, total]
                val = clamp(raw, 2, total)
                # reflect clamp back into the UI
                amt_e.delete(0, "end")
                amt_e.insert(0, str(val))

                if val != old:
                    comp.data["fixed_amount"] = val
                    setup_field_grid(main_panel, comp)


            amt_e.bind("<FocusOut>", save_fixed)

        else:  # "random in range"
            # two entries: start and end
            start_e = ttk.Entry(amount_frame, width=5, style="Small.TEntry")
            end_e = ttk.Entry(amount_frame, width=5, style="Small.TEntry")
            start_e.insert(0, str(comp.data.get("range_start", 2)))
            end_e.insert(0,   str(comp.data.get("range_end",   total)))
            start_e.pack(side="left")
            ttk.Label(amount_frame, text=" to ", style="Small.TLabel").pack(side="left")
            end_e.pack(side="left")

            def save_range(event=None):
                # store old so we only redraw on change
                old_s = comp.data.get("range_start", 2)
                old_e = comp.data.get("range_end", total)
                # parse or fallback
                try:
                    raw_s = int(start_e.get())
                except ValueError:
                    raw_s = comp.data.get("range_start", 2)
                try:
                    raw_e = int(end_e.get())
                except ValueError:
                    raw_e = comp.data.get("range_end", total)

                # clamp both into [2, total]
                s = clamp(raw_s, 2, total)
                e = clamp(raw_e, 2, total)
                # ensure e >= s
                if e < s:
                    e = s

                # only save & redraw if either end changed
                if s != old_s or e != old_e:
                    comp.data["range_start"] = s
                    comp.data["range_end"]   = e
                    # redraw grid
                    setup_field_grid(main_panel, comp)

                # reflect clamp back into the UI
                start_e.delete(0, "end"); start_e.insert(0, str(s))
                end_e.delete(0,   "end"); end_e.insert(0,   str(e))



            start_e.bind("<FocusOut>", save_range)
            end_e.bind(  "<FocusOut>", save_range)

    # re‑build the amount inputs whenever the mode changes
    size_var.trace_add("write", update_amount_input)
    # initial layout + grid draw
    update_amount_input()


    # ---------- Stimulus Set ----------
    add_label(app.tr("stimulus_set_label"))
    stim_set_var = tk.StringVar(value=comp.data.get("stimulus_set", "Images"))
    # Default options.
    stimulus_options = ["Images", "Faces", "Import"]
    # stimulus set: default to Images if not set
    stimulus_set = comp.data.get("stimulus_set")
    if stimulus_set is None:
        stimulus_set = "Images"
        comp.data["stimulus_set"] = "Images"  # <- fix: save it to comp.data immediately

    stim_set_var = tk.StringVar(value=stimulus_set)

    # Initialize app.imported_stimulus_sets if not already present.
    if not hasattr(app, "imported_stimulus_sets"):
        app.imported_stimulus_sets = {}

    # Append any previously imported stimulus sets into the options.
    # Insert them before "Import" so that "Import" remains at the end.
    for imported in app.imported_stimulus_sets:
        stimulus_options.insert(-1, imported)

    # Create an OptionMenu with the combined options.
    stim_dropdown = ttk.Combobox(
        left_panel,
        textvariable=stim_set_var,
        values=stimulus_options,
        state="readonly",
        style="Small.TCombobox"        # ← small white background
    )
    stim_dropdown.pack(anchor="w", padx=10, fill="x")

    def open_import_window():
        # Open a new window for importing a new stimulus set.
        import_win = Toplevel(left_panel)
        import_win.title(app.tr("import_window_title"))
        
        Label(import_win, text=app.tr("import_name_label")).pack(pady=(10, 5))
        name_entry = tk.Entry(import_win)
        name_entry.pack(pady=(0, 10))
        
        Button(import_win, text=app.tr("browse_folder_button"), command=lambda: browse_folder()).pack(pady=(0, 5))
        folder_entry = tk.Entry(import_win, width=50)
        folder_entry.pack(pady=(0, 10))
        
        def browse_folder():
            folder = filedialog.askdirectory(title=app.tr("import_folder_prompt"))
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
        
        Button(import_win, text=app.tr("add_button"), command=add_stimulus_set).pack(pady=(0, 10))

    def handle_stim_set(*args):
            selection = stim_set_var.get()
            if selection == "Import":
                open_import_window()
            else:
                # 1) Update the stimulus set
                comp.data["stimulus_set"] = selection

                # 2) Reset distractor‐set back to “All”
                comp.data["distractor_set"] = "All"
                distractor_set_var.set("All")

                # 3) Reset selected‐target back to “Random”
                comp.data["selected_target"] = "Random"
                selected_target_var.set("Random")

                # 4) Clear out any previous image picks
                comp.data["last_selections"] = {}
                comp.data["last_distractors"] = {}

                # 5) Redraw the field grid to pick up the new state
                setup_field_grid(main_panel, comp)

    stim_set_var.trace_add("write", handle_stim_set)

    # ---------- Target Type ----------
    add_label(app.tr("target_type_label"))
    target_type_var = tk.StringVar(value=comp.data.get("target_type", "positive"))
    target_type_menu = add_dropdown(target_type_var, ["positive", "negative", "neutral"])

    target_type_menu.pack(anchor="w", padx=10, fill="x")
    def on_target_type_change(*_):
        comp.data["target_type"] = target_type_var.get()
        setup_field_grid(main_panel, comp)
    target_type_var.trace_add("write", on_target_type_change)


    # ---------- Selected Target ----------
    add_label(app.tr("selected_target_label"))
    selected_target_var = tk.StringVar(value=comp.data.get("selected_target", "Random"))
    selected_target_menu = ttk.Combobox(
        left_panel,
        textvariable=selected_target_var,
        values=["Random", "Select from list"],
        state="readonly",
        style="Small.TCombobox"   
    )
    selected_target_menu.pack(anchor="w", padx=10, fill="x")
    def handle_target_select(*_):
        comp.data["selected_target"] = selected_target_var.get()
        if selected_target_var.get() == "Select from list":
            open_image_selector(comp, target_type_var.get(),app)
    selected_target_var.trace_add("write", handle_target_select)

    # ---------- No Target ----------
    no_target_var = tk.BooleanVar(value=comp.data.get("no_target", False))
    no_target_chk = ttk.Checkbutton(
        left_panel,
        text=app.tr("no_target_checkbox"),
        variable=no_target_var,
        style="Small.TCheckbutton"      # ← use your small, white‐bg checkbox style
    )
    no_target_chk.pack(anchor="w", padx=10, pady=(5, 0))

    # Function to toggle lock status of target type and selected target.
    def toggle_target_lock():
        no_target = no_target_var.get()
        comp.data.update({"no_target": no_target})
        if no_target:
            target_type_menu.config(state="disabled")
            selected_target_menu.config(state="disabled")
        else:
            target_type_menu.config(state="readonly")
            selected_target_menu.config(state="readonly")
        setup_field_grid(main_panel, comp)

    # Set the initial state based on the value of no_target_var and bind the toggle.
    toggle_target_lock()
    no_target_chk.config(command=toggle_target_lock)

    # ---------- Distractor Type ----------
    add_label(app.tr("distractor_type_label"))
    distractor_type_var = tk.StringVar(value=comp.data.get("distractor_type", "positive"))
    dropdown = add_dropdown(distractor_type_var, ["positive", "negative", "neutral"])
    dropdown.pack(anchor="w", padx=10, fill="x")
    def on_distractor_type_change(*_):
        comp.data["distractor_type"] = distractor_type_var.get()
        setup_field_grid(main_panel, comp)

    distractor_type_var.trace_add("write", on_distractor_type_change)

    # ---------- Distractor Set ----------
    add_label(app.tr("distractor_set_label"))
    distractor_set_var = tk.StringVar(value=comp.data.get("distractor_set", "All"))
    distractor_dropdown = add_dropdown(distractor_set_var, ["All", "Random", "Select set from list"])  # use a unique name for distractor set
    distractor_dropdown.pack(anchor="w", padx=10, fill="x")

    def handle_distractor_set(*args):
        selection = distractor_set_var.get()
        comp.data["distractor_set"] = selection
        if selection == "Select set from list":
            # Call the distractor selector.
            open_distractor_selector(comp, comp.data.get("distractor_type", "positive"),app)
    
    distractor_set_var.trace_add("write", handle_distractor_set)


