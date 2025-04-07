import tkinter as tk

class ComponentBlock(tk.Frame):
    def __init__(self, parent, label, color, x=0, y=0, from_timeline=False, preview=False):
        super().__init__(parent, width=80, height=60, bg=color, highlightbackground="black", highlightthickness=1)
        self.label_text = label
        self.color = color
        self.from_timeline = from_timeline
        self.preview = preview
        self.parent = parent
        self.place(x=x, y=y)

        self.label_offset_y = 65  # vertical offset for text below the block

        # Hidden internal label inside block
        self.label_widget = tk.Label(self, text="", bg=color)
        self.label_widget.place(relx=0.5, rely=0.5, anchor="center")

        if self.from_timeline and not self.preview:
            # Editable entry for timeline blocks
            self.name_var = tk.StringVar(value=self.label_text)
            self.name_entry = tk.Entry(parent, textvariable=self.name_var, font=("Segoe UI", 9), width=10, justify="center")
            self.name_entry.place(x=x, y=y + self.label_offset_y)
            self.name_entry.bind("<Return>", self.update_label)
            self.name_entry.bind("<FocusOut>", self.update_label)

        elif not self.from_timeline and not self.preview:
            # Static label for sidebar components only
            self.name_label = tk.Label(parent, text=self.label_text, font=("Segoe UI", 9), bg="white")
            self.name_label.place(x=x, y=y + self.label_offset_y)

        if self.from_timeline and not self.preview:
            # Make draggable if it's in the timeline (not preview)
            self.bind("<Button-1>", self.on_start_drag)
            self.bind("<B1-Motion>", self.on_drag)
            self.bind("<ButtonRelease-1>", self.on_drop)
            self.label_widget.bind("<Button-1>", self.on_start_drag)
            self.label_widget.bind("<B1-Motion>", self.on_drag)
            self.label_widget.bind("<ButtonRelease-1>", self.on_drop)

        self.start_x = 0
        self.start_y = 0

    def on_start_drag(self, event):
        self.start_x = event.x
        self.lift()
        if self.from_timeline and not self.preview:
            self.name_entry.lift()

    def on_drag(self, event):
        dx = event.x - self.start_x
        new_x = self.winfo_x() + dx
        self.place(x=new_x, y=10)

        if self.from_timeline and not self.preview:
            self.name_entry.place(x=new_x, y=10 + self.label_offset_y)

    def on_drop(self, event):
        if self.from_timeline and not self.preview:
            self.master.reorder_component(self)

    def update_label(self, event=None):
        self.label_text = self.name_var.get()

def show_editor_screen(app):
    app.clear_screen()
    app.timeline_components = []
    app.timeline_spacing = 90  # horizontal space between blocks

    # Timeline drop zone
    timeline_frame = tk.Frame(app.root, bg="white", bd=2, relief="flat", height=80)
    timeline_frame.place(relx=0.025, rely=0.7, relwidth=0.7, relheight=0.2)
    app.timeline_frame = timeline_frame

    def reorder_component(component):
        x = component.winfo_x()
        new_index = x // app.timeline_spacing
        new_index = max(0, min(new_index, len(app.timeline_components) - 1))

        if component not in app.timeline_components:
            return

        current_index = app.timeline_components.index(component)
        label = component.label_text

        # Prevent "Start" from being moved
        if label == "Start" and new_index != 0:
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Prevent "End" from being moved
        if label == "End" and new_index != len(app.timeline_components) - 1:
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Prevent dropping INTO Start or End slot
        target_block = app.timeline_components[new_index]
        target_label = target_block.label_text

        if target_label == "Start" and new_index == 0:
            # Can't insert at index 0
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        if target_label == "End" and new_index == len(app.timeline_components) - 1:
            # Can't insert before End
            component.place(x=current_index * app.timeline_spacing, y=10)
            component.name_entry.place(x=current_index * app.timeline_spacing, y=75)
            return

        # Perform the reordering
        app.timeline_components.remove(component)
        app.timeline_components.insert(new_index, component)

        # Rerender
        for i, block in enumerate(app.timeline_components):
            block.place(x=i * app.timeline_spacing, y=10)
            if block.from_timeline:
                block.name_entry.place(x=i * app.timeline_spacing, y=75)



    app.timeline_frame.reorder_component = reorder_component

    def insert_component(label, color):
        index = len(app.timeline_components)

        # Prevent duplicates
        if label == "Start" and any(b.label_text == "Start" for b in app.timeline_components):
            print("Only one Start allowed.")
            return
        if label == "End" and any(b.label_text == "End" for b in app.timeline_components):
            print("Only one End allowed.")
            return

        # Enforce Start at beginning
        if label == "Start":
            index = 0
            for i in range(len(app.timeline_components)):
                block = app.timeline_components[i]
                block.place(x=(i + 1) * app.timeline_spacing, y=10)
                if block.from_timeline:
                    block.name_entry.place(x=(i + 1) * app.timeline_spacing, y=75)

        # Enforce End at the end
        elif label == "End":
            index = len(app.timeline_components)

        # For others, insert before End if it exists
        else:
            for i, block in enumerate(app.timeline_components):
                if block.label_text == "End":
                    index = i
                    break

        # Create and insert block
        new_block = ComponentBlock(app.timeline_frame, label, color, x=index * app.timeline_spacing, y=10, from_timeline=True)
        app.timeline_components.insert(index, new_block)

        # Rerender
        for i, block in enumerate(app.timeline_components):
            block.place(x=i * app.timeline_spacing, y=10)
            if block.from_timeline:
                block.name_entry.place(x=i * app.timeline_spacing, y=75)


    # Back button
    back_btn = tk.Button(app.root, text="←", font=("Arial", 16), bg="#fef6f6", command=app.show_create_screen)
    back_btn.place(x=10, y=10)

    # Component palette
    components_panel = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    components_panel.place(relx=0.75, rely=0.025, relwidth=0.22, relheight=0.65)

    tk.Label(components_panel, text="Components", font=("Segoe UI", 12, "bold"), bg="#dcdcdc").pack(fill="x")

    component_data = [
        ("Start", "green"),
        ("Text", "gray"),
        ("Stimulus", "yellow"),
        ("Stimulus notification", "purple"),
        ("End", "red")
    ]

    def create_component(label, color, x=10, y=10):
        ComponentBlock(app.timeline_frame, label, color, x=x, y=y,from_timeline=True)

    def on_click(event, label, color):
        # Click = add to default location
        create_component(label, color)

    def on_start_drag_from_palette(event, label, color, template):
        # Create temp drag block
        temp = ComponentBlock(app.root, label, color,from_timeline=True)
        temp.lift()

        def follow_mouse(ev):
            temp.place(x=ev.x_root - 50, y=ev.y_root - 50)

        def on_release(ev):
            # Check if dropped inside timeline
            x_win = ev.x_root - app.root.winfo_rootx()
            y_win = ev.y_root - app.root.winfo_rooty()

            timeline_bbox = app.timeline_frame.bbox()
            timeline_abs_x = app.timeline_frame.winfo_rootx() - app.root.winfo_rootx()
            timeline_abs_y = app.timeline_frame.winfo_rooty() - app.root.winfo_rooty()

            if timeline_abs_x <= x_win <= timeline_abs_x + app.timeline_frame.winfo_width() and \
               timeline_abs_y <= y_win <= timeline_abs_y + app.timeline_frame.winfo_height():
                rel_x = x_win - timeline_abs_x
                rel_y = y_win - timeline_abs_y
                create_component(label, color, x=rel_x, y=rel_y)

            temp.destroy()

            app.root.unbind("<Motion>")
            app.root.unbind("<ButtonRelease-1>")

        app.root.bind("<Motion>", follow_mouse)
        app.root.bind("<ButtonRelease-1>", on_release)

    drag_data = {
        "start_x": 0,
        "start_y": 0,
        "dragging": False,
        "temp": None,
        "label": "",
        "color": ""
    }

    def on_template_press(event, label, color):
        drag_data["start_x"] = event.x_root
        drag_data["start_y"] = event.y_root
        drag_data["label"] = label
        drag_data["color"] = color
        drag_data["dragging"] = False

    def on_template_motion(event):
        dx = event.x_root - drag_data["start_x"]
        dy = event.y_root - drag_data["start_y"]

        if not drag_data["dragging"] and (abs(dx) > 5 or abs(dy) > 5):
            drag_data["dragging"] = True
            drag_data["temp"] = ComponentBlock(app.root, drag_data["label"], drag_data["color"], preview=True)
            drag_data["temp"].lift()
            app.root.config(cursor="none")  # hide mouse

        if drag_data["dragging"] and drag_data["temp"]:
            # Convert absolute mouse position to app.root-relative coordinates
            x_local = event.x_root - app.root.winfo_rootx()
            y_local = event.y_root - app.root.winfo_rooty()

            # Place centered under cursor
            drag_data["temp"].place(x=x_local - 40, y=y_local - 30)


    def on_template_release(event):
        app.root.config(cursor="")  # Show mouse again

        if drag_data["dragging"] and drag_data["temp"]:
            x_root = event.x_root
            timeline_x = app.timeline_frame.winfo_rootx()
            timeline_y = app.timeline_frame.winfo_rooty()
            timeline_w = app.timeline_frame.winfo_width()
            timeline_h = app.timeline_frame.winfo_height()

            if timeline_x <= x_root <= timeline_x + timeline_w:
                drop_x = x_root - timeline_x
                index = drop_x // app.timeline_spacing
                index = min(index, len(app.timeline_components))

                label = drag_data["label"]

                # Constraint: Only allow "Start" at position 0
                if label == "Start" and index != 0:
                    print("Start component must be at the beginning!")
                    drag_data["temp"].destroy()
                    drag_data["temp"] = None
                    drag_data["dragging"] = False
                    return

                # Constraint: Only allow "End" at the last position
                if label == "End" and index != len(app.timeline_components):
                    print("End component must be at the end!")
                    drag_data["temp"].destroy()
                    drag_data["temp"] = None
                    drag_data["dragging"] = False
                    return

                # Shift right from insert point
                for i in range(index, len(app.timeline_components)):
                    block = app.timeline_components[i]
                    block.place(x=(i + 1) * app.timeline_spacing, y=10)
                    if block.from_timeline:
                        block.name_entry.place(x=(i + 1) * app.timeline_spacing, y=75)

                insert_component(drag_data["label"], drag_data["color"])


                
            drag_data["temp"].destroy()
            drag_data["temp"] = None

        elif not drag_data["dragging"]:
            insert_component(drag_data["label"], drag_data["color"])


        drag_data["dragging"] = False


    for label, color in component_data:
        container = tk.Frame(components_panel, bg="white")
        container.pack(pady=10)

        block = tk.Frame(container, bg=color, width=60, height=40)
        block.pack()

        text_label = tk.Label(container, text=label, font=("Segoe UI", 9), bg="white")
        text_label.pack()

        # Bind drag + click events
        block.bind("<ButtonPress-1>", lambda e, l=label, c=color: on_template_press(e, l, c))
        block.bind("<B1-Motion>", on_template_motion)
        block.bind("<ButtonRelease-1>", on_template_release)



    # Optional top editor space
    editor_frame = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    editor_frame.place(relx=0.025, rely=0.025, relwidth=0.7, relheight=0.65)

    create_button = tk.Button(app.root, text="Create", font=("Segoe UI", 12), bg="#fef6f6", width=12)
    create_button.place(relx=0.82, rely=0.8)

