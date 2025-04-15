# ui/component_block.py
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
        self.text_styles = {}    # new dictionary to store styles
        self.data = {}
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
            # Update x position; only moving horizontally.
            new_x = self.winfo_x() + dx
            self.place(x=new_x, y=10)
            if self.from_timeline and not self.preview and hasattr(self, "name_entry"):
                self.name_entry.place(x=new_x, y=10 + self.label_offset_y)

            # Auto-scroll logic for the timeline canvas:
            try:
                canvas = self.app.timeline_canvas
            except NameError:
                canvas = self.master.master  # Fallback

            canvas_left = canvas.winfo_rootx()
            canvas_right = canvas_left + canvas.winfo_width()
            auto_scroll_margin = 20

            scroll_region = canvas.bbox("all")
            if scroll_region and (scroll_region[2] - scroll_region[0]) > canvas.winfo_width():
                # Only scroll if canvas content exceeds visible area
                if event.x_root < canvas_left + auto_scroll_margin:
                    canvas.xview_scroll(-1, "units")
                elif event.x_root > canvas_right - auto_scroll_margin:
                    canvas.xview_scroll(1, "units")
            else:
                # Lock scroll if not needed (prevents visual jump)
                canvas.xview_moveto(0)


    def on_button_release(self, event):
        # If a drag was detected, finalize the drop.
        if self._is_dragging:
            self.on_drop(event)
        else:
            self.app.select_component(self)
        # Reset dragging state.
        self._is_dragging = False

    def on_drop(self, event):
        if self.from_timeline and not self.preview:
            self.master.reorder_component(self)

    def update_label(self, event=None):
        self.label_text = self.name_var.get()
