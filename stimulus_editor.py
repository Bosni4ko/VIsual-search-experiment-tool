import tkinter as tk

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
    selected_target_var.trace_add("write", lambda *_: comp.data.update({"selected_target": selected_target_var.get()}))

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

