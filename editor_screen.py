import tkinter as tk

import tkinter as tk

class ComponentBlock(tk.Frame):
    def __init__(self, app, parent, label, color, x=0, y=0, 
                 from_timeline=False, preview=False, attachment=None, component_type=None):
        super().__init__(parent, width=80, height=60, bg=color, 
                         highlightbackground="black", highlightthickness=1)
        self.app = app  # Store a reference to the application
        self.label_text = label
        self.color = color
        self.from_timeline = from_timeline
        self.preview = preview
        self.parent = parent
        self.place(x=x, y=y)
        self.attachment = attachment  # can be another ComponentBlock or None
        self.component_type = component_type or label

        self.label_offset_y = 65  # vertical offset for text below the block

        # Hidden internal label inside block
        self.label_widget = tk.Label(self, text="", bg=color)
        self.label_widget.place(relx=0.5, rely=0.5, anchor="center")

        if self.from_timeline and not self.preview:
            # Editable entry for timeline blocks
            self.name_var = tk.StringVar(value=self.label_text)
            self.name_entry = tk.Entry(parent, textvariable=self.name_var, 
                                       font=("Segoe UI", 9), width=10, justify="center")
            self.name_entry.place(x=x, y=y + self.label_offset_y)
            self.name_entry.bind("<Return>", self.update_label)
            self.name_entry.bind("<FocusOut>", self.update_label)
        elif not self.from_timeline and not self.preview:
            # Static label for sidebar components only
            self.name_label = tk.Label(parent, text=self.label_text, 
                                       font=("Segoe UI", 9), bg="white")
            self.name_label.place(x=x, y=y + self.label_offset_y)

        # Bind unified mouse event handlers for timeline components.
        if self.from_timeline and not self.preview:
            self.bind("<Button-1>", self.on_button_press)
            self.bind("<B1-Motion>", self.on_motion)
            self.bind("<ButtonRelease-1>", self.on_button_release)
            self.label_widget.bind("<Button-1>", self.on_button_press)
            self.label_widget.bind("<B1-Motion>", self.on_motion)
            self.label_widget.bind("<ButtonRelease-1>", self.on_button_release)

        # Store the starting mouse coordinates
        self.start_x = 0
        self.start_y = 0
        # Flag indicating whether a drag movement occurred.
        self._is_dragging = False

    def on_button_press(self, event):
        # Record where the press occurred and reset the dragging flag.
        self.start_x = event.x
        self.start_y = event.y
        self._is_dragging = False
        self.lift()
        if self.from_timeline and not self.preview and hasattr(self, "name_entry"):
            self.name_entry.lift()

    def on_motion(self, event):
        # Calculate movement relative to press.
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        threshold = 5  # pixels movement threshold
        if not self._is_dragging and (abs(dx) > threshold or abs(dy) > threshold):
            self._is_dragging = True
        if self._is_dragging:
            # Update x position; here we're only moving horizontally.
            new_x = self.winfo_x() + dx
            self.place(x=new_x, y=10)
            if self.from_timeline and not self.preview and hasattr(self, "name_entry"):
                self.name_entry.place(x=new_x, y=10 + self.label_offset_y)

            # Auto-scroll logic for the timeline canvas:
            try:
                canvas = self.app.timeline_canvas  # app.timeline_canvas must be set.
            except NameError:
                canvas = self.master.master  # Fallback in case
            canvas_left = canvas.winfo_rootx()
            canvas_right = canvas_left + canvas.winfo_width()
            auto_scroll_margin = 20
            if event.x_root < canvas_left + auto_scroll_margin:
                canvas.xview_scroll(-1, "units")
            elif event.x_root > canvas_right - auto_scroll_margin:
                canvas.xview_scroll(1, "units")

    def on_button_release(self, event):
        # If a drag was detected, finalize the drop.
        if self._is_dragging:
            self.on_drop(event)
        else:
            # If no drag occurred, it was simply a click.
            # Only for text components do we select them on click.
            if self.component_type == "Text":
                self.app.select_component(self)
        # Reset dragging state.
        self._is_dragging = False

    def on_drop(self, event):
        if self.from_timeline and not self.preview:
            self.master.reorder_component(self)

    def update_label(self, event=None):
        self.label_text = self.name_var.get()



def show_editor_screen(app):
    app.clear_screen()
    app.timeline_components = []
    app.timeline_spacing = 100  # horizontal space between blocks

   # Create a canvas that will act as a horizontally scrollable container
    timeline_canvas = tk.Canvas(app.root, bg="white", bd=2, relief="flat", height=80)
    timeline_canvas.place(relx=0.025, rely=0.7, relwidth=0.7, relheight=0.2)

    # Create a horizontal scrollbar linked to the canvas
    scrollbar = tk.Scrollbar(app.root, orient="horizontal", command=timeline_canvas.xview)
    # Place the scrollbar at the bottom of the canvas
    scrollbar.place(relx=0.025, rely=0.9, relwidth=0.7)
    timeline_canvas.configure(xscrollcommand=scrollbar.set)

    timeline_container = tk.Frame(timeline_canvas, bg="white", width=580, height=100)
    timeline_canvas.create_window((10, 0), window=timeline_container, anchor="nw")

    # Update the scroll region whenever the size of timeline_container changes
    timeline_container.bind(
        "<Configure>",
        lambda e: timeline_canvas.configure(scrollregion=timeline_canvas.bbox("all"))
    )
    app.timeline_canvas = timeline_canvas
    app.timeline_container = timeline_container
    def update_timeline_container_size():
        # Make sure all geometry calculations are up-to-date
        app.timeline_container.update_idletasks()
        
        # Calculate the required width: For example, get the rightmost component's x position plus its width
        max_width = 100
        for child in app.timeline_container.winfo_children():
            x = child.winfo_x()
            w = child.winfo_width()
            max_width = max(max_width, x + w)
            
        # Optionally, add some padding
        new_width = max_width + 20  
        app.timeline_container.config(width=new_width)
        
        # Update the canvas scroll region in case it changed
        app.timeline_container.event_generate("<Configure>")

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
                block.name_entry.place(in_=app.timeline_container, x=i * app.timeline_spacing, y=75)
        update_timeline_container_size()
    
    render_timeline()
    
    # Automatically add Start block at index 0
    start_block = ComponentBlock(app,app.timeline_container, "Start", "green", x=0, y=10, from_timeline=True,component_type="Start")
    app.timeline_components.append(start_block)
    start_block.name_entry.place(x=0, y=75)

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

        # This function is used to mark a component as selected and set up the editor panels accordingly.
    def select_component(comp):
        app.selected_component = comp
        # Clear the left and main panels (assuming they already exist)
        for widget in left_panel.winfo_children():
            widget.destroy()
        for widget in main_panel.winfo_children():
            widget.destroy()
        if comp.component_type == "Text":
            setup_text_editor(comp)
            setup_text_options(comp)
        else:
            tk.Label(main_panel, text="No text options available for this component").pack()

    app.select_component = select_component  # Make the function accessible to ComponentBlock.on_drop

    # Create a text editor in the main panel for editing the Text component.
    def setup_text_editor(comp):
        text_editor = tk.Text(main_panel)
        text_editor.pack(expand=True, fill="both")
        text_editor.delete("1.0", tk.END)
        text_editor.insert("1.0", comp.label_text)
        # When focus leaves, update the component's text.
        text_editor.bind("<FocusOut>", lambda e: update_component_text(comp, text_editor))
        app.text_editor = text_editor

    # Create text styling options in the left panel.
    def setup_text_options(comp):
        tk.Label(left_panel, text="Text Options", font=("Segoe UI", 12, "bold")).pack(pady=5)
        # Define style option variables.
        font_var = tk.StringVar(value="Arial")
        size_var = tk.IntVar(value=12)
        bold_var = tk.BooleanVar(value=False)
        italic_var = tk.BooleanVar(value=False)
        align_var = tk.StringVar(value="left")
        color_var = tk.StringVar(value="black")
        
        # Function to update text style in the editor.
        def update_text_style():
            weight = "bold" if bold_var.get() else "normal"
            slant = "italic" if italic_var.get() else "roman"
            f = tkfont.Font(family=font_var.get(), size=size_var.get(), weight=weight, slant=slant)
            app.text_editor.config(font=f, fg=color_var.get())
            app.text_editor.tag_configure("align", justify=align_var.get())
            app.text_editor.tag_add("align", "1.0", tk.END)
        
        # --- Font Option ---
        tk.Label(left_panel, text="Font:").pack(anchor="w", padx=5)
        fonts = ["Arial", "Times New Roman", "Courier", "Helvetica"]
        tk.OptionMenu(left_panel, font_var, *fonts, command=lambda x: update_text_style()).pack(fill="x", padx=5)
        
        # --- Size ---
        tk.Label(left_panel, text="Size:").pack(anchor="w", padx=5)
        tk.Spinbox(left_panel, from_=8, to=72, textvariable=size_var, command=update_text_style).pack(fill="x", padx=5)
        
        # --- Bold / Italic ---
        tk.Checkbutton(left_panel, text="Bold", variable=bold_var, command=update_text_style).pack(anchor="w", padx=5)
        tk.Checkbutton(left_panel, text="Italic", variable=italic_var, command=update_text_style).pack(anchor="w", padx=5)
        
        # --- Alignment ---
        tk.Label(left_panel, text="Alignment:").pack(anchor="w", padx=5)
        align_frame = tk.Frame(left_panel)
        align_frame.pack(anchor="w", padx=5)
        tk.Radiobutton(align_frame, text="Left", variable=align_var, value="left", command=update_text_style).pack(side="left")
        tk.Radiobutton(align_frame, text="Center", variable=align_var, value="center", command=update_text_style).pack(side="left")
        tk.Radiobutton(align_frame, text="Right", variable=align_var, value="right", command=update_text_style).pack(side="left")
        
        # --- Color chooser ---
        def choose_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_var.set(color)
                update_text_style()
        tk.Button(left_panel, text="Text Color", command=choose_color).pack(pady=5, padx=5, fill="x")
        
        tk.Button(left_panel, text="Apply Style", command=update_text_style).pack(pady=5, padx=5, fill="x")

    # When leaving the text editor, update the component's text.
    def update_component_text(comp, text_editor):
        new_text = text_editor.get("1.0", tk.END).strip()
        comp.label_text = new_text
        comp.label_widget.config(text=new_text)

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
            return 
        
        if index == 0 and component_type != "Start":
            index = 1
        # Create and insert block
        new_block = ComponentBlock(app,app.timeline_container, label, color, x=index * app.timeline_spacing, y=10, from_timeline=True,component_type=component_type)
        app.timeline_components.insert(index, new_block)

        # Rerender
        render_timeline()

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
                            render_timeline()
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

                    insert_component(
                        drag_data["label"], drag_data["color"], drag_data["component_type"], index=index
                    )

                
            drag_data["temp"].destroy()
            drag_data["temp"] = None
            drag_data["dragging"] = False

        elif not drag_data["dragging"]:
            insert_component(drag_data["label"], drag_data["color"], drag_data["component_type"])


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


    # Create the Create button as before.
    create_button = tk.Button(app.root, text="Create", font=("Segoe UI", 12), bg="#fef6f6", width=12)
    create_button.place(relx=0.82, rely=0.8)

    # Move the back button under the Create button.
    back_btn = tk.Button(app.root, text="←", font=("Arial", 16), bg="#fef6f6", command=app.show_create_screen)
    back_btn.place(relx=0.82, rely=0.9)
