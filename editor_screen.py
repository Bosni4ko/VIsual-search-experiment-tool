import tkinter as tk

class ComponentBlock(tk.Frame):
    def __init__(self, parent, label, color, x=0, y=0):
        super().__init__(parent, width=80, height=60, bg=color, highlightbackground="black", highlightthickness=1)
        self.label = label
        self.color = color
        self.place(x=x, y=y)
        self.label_widget = tk.Label(self, text=label, bg=color, font=("Segoe UI", 9, "bold"))
        self.label_widget.place(relx=0.5, rely=0.5, anchor="center")

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
        self.start_y = event.y

    def on_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        x = self.winfo_x() + dx
        y = self.winfo_y() + dy
        self.place(x=x, y=y)

    def on_drop(self, event):
        # Optional: Snap to grid, prevent out-of-bounds
        pass


def show_editor_screen(app):
    app.clear_screen()

    # Timeline drop zone
    timeline_frame = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    timeline_frame.place(relx=0.025, rely=0.7, relwidth=0.7, relheight=0.2)
    app.timeline_frame = timeline_frame

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
        ComponentBlock(app.timeline_frame, label, color, x=x, y=y)

    def on_click(event, label, color):
        # Click = add to default location
        create_component(label, color)

    def on_start_drag_from_palette(event, label, color, template):
        # Create temp drag block
        temp = ComponentBlock(app.root, label, color)
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
            drag_data["temp"] = ComponentBlock(app.root, drag_data["label"], drag_data["color"])
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
            x_win = event.x_root - app.root.winfo_rootx()
            y_win = event.y_root - app.root.winfo_rooty()

            timeline_abs_x = app.timeline_frame.winfo_rootx() - app.root.winfo_rootx()
            timeline_abs_y = app.timeline_frame.winfo_rooty() - app.root.winfo_rooty()

            if timeline_abs_x <= x_win <= timeline_abs_x + app.timeline_frame.winfo_width() and \
                timeline_abs_y <= y_win <= timeline_abs_y + app.timeline_frame.winfo_height():
                rel_x = x_win - timeline_abs_x - 40
                rel_y = y_win - timeline_abs_y - 30
                ComponentBlock(app.timeline_frame, drag_data["label"], drag_data["color"], x=rel_x, y=rel_y)

            drag_data["temp"].destroy()
            drag_data["temp"] = None

        elif not drag_data["dragging"]:
            # Only create on click if not dragging
            ComponentBlock(app.timeline_frame, drag_data["label"], drag_data["color"], x=10, y=10)

        drag_data["dragging"] = False


    def on_template_click(event, label, color):
        if not drag_data["dragging"]:
            ComponentBlock(app.timeline_frame, label, color, x=10, y=10)

    for label, color in component_data:
        template = tk.Frame(components_panel, bg=color, width=60, height=40)
        template.pack(pady=10)
        tk.Label(template, text=label, font=("Segoe UI", 10, "bold"), bg=color).place(relx=0.5, rely=0.5, anchor="center")

        # Bind left click and drag
        template.bind("<ButtonPress-1>", lambda e, l=label, c=color: on_template_press(e, l, c))
        template.bind("<B1-Motion>", on_template_motion)
        template.bind("<ButtonRelease-1>", on_template_release)


    # Optional top editor space
    editor_frame = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    editor_frame.place(relx=0.025, rely=0.025, relwidth=0.7, relheight=0.65)

    create_button = tk.Button(app.root, text="Create", font=("Segoe UI", 12), bg="#fef6f6", width=12)
    create_button.place(relx=0.82, rely=0.8)

