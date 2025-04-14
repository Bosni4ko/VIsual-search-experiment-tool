# ui/palette.py
import tkinter as tk
from component_block import ComponentBlock

def setup_components_palette(app):
    # Component palette
    components_panel = tk.Frame(app.root, bg="white", bd=2, relief="flat")
    components_panel.place(relx=0.75, rely=0.025, relwidth=0.22, relheight=0.65)

    tk.Label(components_panel, text="Components", font=("Segoe UI", 12, "bold"), bg="#dcdcdc").pack(fill="x")

    component_data = [
        ("Text", "gray","Text"),
        ("Stimulus", "yellow","Stimulus"),
        ("Stimulus notification", "purple","Stimulus notification"),
        ("End", "red","End")
    ]

    drag_data = {
        "start_x": 0,
        "start_y": 0,
        "dragging": False,
        "temp": None,
        "label": "",
        "color": "",
        "component_type":""
    }

    def on_template_press(event, label, color, component_type):
        drag_data["start_x"] = event.x_root
        drag_data["start_y"] = event.y_root
        drag_data["label"] = label
        drag_data["color"] = color
        drag_data["dragging"] = False
        drag_data["component_type"] = component_type

    def on_template_motion(event):
        dx = event.x_root - drag_data["start_x"]
        dy = event.y_root - drag_data["start_y"]

        if not drag_data["dragging"] and (abs(dx) > 5 or abs(dy) > 5):
            drag_data["dragging"] = True
            # Create a temporary preview component for dragging.
            drag_data["temp"] = ComponentBlock(app,app.root, drag_data["label"], drag_data["color"],
                                                preview=True, component_type=drag_data["component_type"])
            drag_data["temp"].lift()
            app.root.config(cursor="none")  # Hide mouse cursor during drag

        if drag_data["dragging"] and drag_data["temp"]:
            # Convert absolute mouse position to app.root-relative coordinates
            x_local = event.x_root - app.root.winfo_rootx()
            y_local = event.y_root - app.root.winfo_rooty()
            # Place the temporary component centered under the cursor
            drag_data["temp"].place(x=x_local - 40, y=y_local - 30)

            # --- Auto-scrolling logic for dragging new components ---
            # Get the timeline canvas (ensure you stored it as app.timeline_canvas)
            canvas = app.timeline_canvas  
            # Determine canvas boundaries in screen coordinates
            canvas_left = canvas.winfo_rootx()
            canvas_right = canvas_left + canvas.winfo_width()
            auto_scroll_margin = 20  # pixels from the edge

            # If the mouse is near the left border, scroll left; if near right, scroll right.
            if event.x_root < canvas_left + auto_scroll_margin:
                canvas.xview_scroll(-1, "units")
            elif event.x_root > canvas_right - auto_scroll_margin:
                canvas.xview_scroll(1, "units")



    def on_template_release(event):
        app.root.config(cursor="")  # Show mouse again
        component_type = drag_data["component_type"]
        if drag_data["dragging"] and drag_data["temp"]:
            x_root = event.x_root
            timeline_x = app.timeline_container.winfo_rootx()
            timeline_w = app.timeline_container.winfo_width()

            if timeline_x <= x_root <= timeline_x + timeline_w:
                drop_x = x_root - timeline_x
                index = drop_x // app.timeline_spacing
                index = min(index, len(app.timeline_components))

                label = drag_data["label"]
                color = drag_data["color"]

                # Constraint: Only allow "Start" at position 0
                if component_type == "Start" and index != 0:
                    print("Start component must be at the beginning!")
                    drag_data["temp"].destroy()
                    drag_data["temp"] = None
                    drag_data["dragging"] = False
                    return

                # Constraint: Only allow "End" at the last position
                if component_type == "End" and index != len(app.timeline_components):
                    print("End component must be at the end!")
                    drag_data["temp"].destroy()
                    drag_data["temp"] = None
                    drag_data["dragging"] = False
                    return
                if component_type == "Stimulus notification":
                # Check the block that will come AFTER the drop
                    if index < len(app.timeline_components):
                        stimulus_candidate = app.timeline_components[index]
                        if stimulus_candidate.component_type == "Stimulus" and stimulus_candidate.attachment is None:
                            # Valid: insert and attach
                            notification = ComponentBlock(
                                app,
                                app.timeline_container,
                                label,
                                color,
                                x=index * app.timeline_spacing,
                                y=10,
                                from_timeline=True,
                                attachment=stimulus_candidate,
                                component_type=component_type
                            )
                            stimulus_candidate.attachment = notification
                            app.timeline_components.insert(index, notification)

                            # Rerender
                            app.render_timeline()
                        else:
                            print("Drop must be before a free Stimulus.")
                    else:
                        print("Drop must be before a Stimulus.")
                else:
                    # Prevent dropping into a locked Stimulus-Notification pair
                    for i in range(len(app.timeline_components) - 1):
                        first = app.timeline_components[i]
                        second = app.timeline_components[i + 1]
                        if (
                            first.component_type == "Stimulus notification"
                            and second.component_type == "Stimulus"
                            and second.attachment == first
                            and i < index <= i + 1
                        ):
                            print("Redirecting to safe position before the notification")
                            index = i  # redirect insert before notification
                            break

                    # If allowed, shift right and insert
                    for i in range(index, len(app.timeline_components)):
                        block = app.timeline_components[i]
                        block.place(x=(i + 1) * app.timeline_spacing, y=10)
                        if block.from_timeline:
                            block.name_entry.place(x=(i + 1) * app.timeline_spacing, y=75)

                    app.insert_component(
                        drag_data["label"], drag_data["color"], drag_data["component_type"], index=index
                    )

                
            drag_data["temp"].destroy()
            drag_data["temp"] = None
            drag_data["dragging"] = False

        elif not drag_data["dragging"]:
            app.insert_component(drag_data["label"], drag_data["color"], drag_data["component_type"])


        drag_data["dragging"] = False


    for label, color, component_type in component_data:
        container = tk.Frame(components_panel, bg="white")
        container.pack(pady=10)

        block = tk.Frame(container, bg=color, width=60, height=40)
        block.pack()

        text_label = tk.Label(container, text=label, font=("Segoe UI", 9), bg="white")
        text_label.pack()

        # Bind drag + click events
        block.bind("<ButtonPress-1>", lambda e, l=label, c=color,ct=component_type: on_template_press(e, l, c,ct))
        block.bind("<B1-Motion>", on_template_motion)
        block.bind("<ButtonRelease-1>", on_template_release)
