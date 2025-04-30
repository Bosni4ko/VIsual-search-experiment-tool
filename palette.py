import tkinter as tk
from component_block import ComponentBlock
from styles import COMPONENT_LABEL_FONT, COMPONENT_FONT

def setup_components_palette(app):
    # Component palette container
    components_panel = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    components_panel.place(relx=0.75, rely=0.025, relwidth=0.22, relheight=0.65)

    # Header label
    tk.Label(
        components_panel,
        text=app.tr("components"),
        font=COMPONENT_FONT,
        bg="#dcdcdc"
    ).pack(fill="x")

    # Body frame for palette items
    body = tk.Frame(components_panel, bg="white")
    body.place(relx=0, rely=0.08, relwidth=1, relheight=0.92)

    # Component definitions
    component_data = [
        ("Text", "gray", "Text"),
        ("Stimulus", "yellow", "Stimulus"),
        ("Stimulus notification", "purple", "Stimulus notification"),
        ("End", "red", "End")
    ]

    # Configure grid: one row per component, equally weighted
    for i in range(len(component_data)):
        body.rowconfigure(i, weight=1)
    body.columnconfigure(0, weight=1)

    # Drag state
    drag_data = {
        "start_x": 0,
        "start_y": 0,
        "dragging": False,
        "temp": None,
        "label": "",
        "color": "",
        "component_type": ""
    }

    # Handlers for drag-and-drop (same logic preserved)
    def on_template_press(event, label, color, component_type):
        drag_data.update({
            "start_x": event.x_root,
            "start_y": event.y_root,
            "label": label,
            "color": color,
            "component_type": component_type,
            "dragging": False
        })

    def on_template_motion(event):
        dx = event.x_root - drag_data["start_x"]
        dy = event.y_root - drag_data["start_y"]
        if not drag_data["dragging"] and (abs(dx) > 5 or abs(dy) > 5):
            drag_data["dragging"] = True
            drag_data["temp"] = ComponentBlock(
                app, app.root,
                drag_data["label"], drag_data["color"],
                preview=True,
                component_type=drag_data["component_type"]
            )
            drag_data["temp"].lift()
            app.root.config(cursor="none")

        if drag_data["dragging"] and drag_data["temp"]:
            x_local = event.x_root - app.root.winfo_rootx()
            y_local = event.y_root - app.root.winfo_rooty()
            drag_data["temp"].place(x=x_local-40, y=y_local-30)

            # Auto-scroll timeline during drag
            canvas = app.timeline_canvas
            left = canvas.winfo_rootx()
            right = left + canvas.winfo_width()
            margin = 20
            if event.x_root < left + margin:
                canvas.xview_scroll(-1, 'units')
            elif event.x_root > right - margin:
                canvas.xview_scroll(1, 'units')

    def on_template_release(event):
        app.root.config(cursor="")
        if drag_data["dragging"] and drag_data["temp"]:
            x_root = event.x_root
            tl_x = app.timeline_container.winfo_rootx()
            tl_w = app.timeline_container.winfo_width()
            if tl_x <= x_root <= tl_x + tl_w:
                drop_x = x_root - tl_x
                index = max(0, min(drop_x // app.timeline_spacing, len(app.timeline_components)))
                ct = drag_data["component_type"]
                key = drag_data["label"]
                text = app.tr(key)
                color = drag_data["color"]

                # Enforce Start at first, End at last
                if ct == "Start" and index != 0:
                    print("Start component must be at the beginning!")
                elif ct == "End" and index != len(app.timeline_components):
                    print("End component must be at the end!")
                elif ct == "Stimulus notification":
                    # Attach notification to following Stimulus if free
                    if index < len(app.timeline_components):
                        cand = app.timeline_components[index]
                        if cand.component_type == "Stimulus" and cand.attachment is None:
                            notif = ComponentBlock(
                                app,
                                app.timeline_container,
                                text,
                                color,
                                x=index * app.timeline_spacing,
                                y=10,
                                from_timeline=True,
                                attachment=cand,
                                component_type=ct
                            )
                            cand.attachment = notif
                            app.timeline_components.insert(index, notif)
                            app.render_timeline()
                        else:
                            print("Drop must be before a free Stimulus.")
                    else:
                        print("Drop must be before a Stimulus.")
                else:
                    # Prevent dropping into locked pairs
                    for i in range(len(app.timeline_components)-1):
                        first = app.timeline_components[i]
                        second = app.timeline_components[i+1]
                        if (first.component_type == "Stimulus notification"
                            and second.component_type == "Stimulus"
                            and second.attachment == first
                            and i < index <= i+1):
                            index = i
                            break
                    # Shift and insert new block
                    for i in range(index, len(app.timeline_components)):
                        b = app.timeline_components[i]
                        b.place(x=(i+1)*app.timeline_spacing, y=10)
                        if b.from_timeline:
                            b.name_entry.place(x=(i+1)*app.timeline_spacing, y=75)
                    app.insert_component(text, color, ct, index=index)

            drag_data["temp"].destroy()
        else:
            # Quick click: insert at end
            app.insert_component(
                app.tr(drag_data["label"]),
                drag_data["color"],
                drag_data["component_type"]
            )
        drag_data["dragging"] = False

    # Build palette items with dynamic sizing
    for i, (label, color, component_type) in enumerate(component_data):
        container = tk.Frame(body, bg="white")
        container.grid(row=i, column=0, sticky="nsew", padx=5, pady=5)

        block = tk.Frame(container, bg=color)
        block.place(relx=0.5, rely=0.1, relwidth=0.8, relheight=0.6, anchor="n")

        text_label = tk.Label(container, text=app.tr(label), font=COMPONENT_LABEL_FONT, bg="white")
        text_label.place(relx=0.5, rely=0.75, anchor="n")

        # Bind drag + click events
        block.bind("<ButtonPress-1>", lambda e, l=label, c=color, ct=component_type: on_template_press(e, l, c, ct))
        block.bind("<B1-Motion>", on_template_motion)
        block.bind("<ButtonRelease-1>", on_template_release)

