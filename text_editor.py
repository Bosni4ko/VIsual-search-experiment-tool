import tkinter as tk
from tkinter import font as tkfont, colorchooser
def setup_text_editor(app, main_panel, comp):
    text_editor = tk.Text(main_panel)
    text_editor.pack(expand=True, fill="both")
    text_editor.delete("1.0", tk.END)
    text_editor.insert("1.0", comp.label_text)
    text_editor.bind("<FocusOut>", lambda e: update_component_text(comp, text_editor))
    app.text_editor = text_editor

def setup_text_options(app, left_panel, comp):
    """
    Sets up the left panel with text formatting options.
    When the user clicks in the text editor, the options update based on the formatting
    at the current caret position.
    Changes in the options update the style immediately on the selected text.
    Each applied style uses a unique tag.
    """
    global style_counter  # Global counter for unique style tags.
    style_counter = 0
    
    # --- Create a label for the options panel ---
    tk.Label(left_panel, text="Text Options", font=("Segoe UI", 12, "bold")).pack(pady=5)
    
    # Variables to store style options.
    font_var   = tk.StringVar(value="Arial")
    size_var   = tk.IntVar(value=12)
    bold_var   = tk.BooleanVar(value=False)
    italic_var = tk.BooleanVar(value=False)
    align_var  = tk.StringVar(value="left")
    color_var  = tk.StringVar(value="black")
    
    # --- Function to update the left-panel controls based on the text at the insertion point ---
    def update_options_from_cursor(event=None):
        # Get the index of the current insertion (caret) point.
        index = app.text_editor.index("insert")
        tags_at_index = app.text_editor.tag_names(index)
        # Filter for tags that start with "styled_"
        styled_tags = [tag for tag in tags_at_index if tag.startswith("styled_")]
        
        # If no styled tag is found at "insert", try one character back.
        if not styled_tags:
            try:
                index_before = app.text_editor.index(f"{index} - 1c")
            except tk.TclError:
                index_before = index
            tags_at_before = app.text_editor.tag_names(index_before)
            styled_tags = [tag for tag in tags_at_before if tag.startswith("styled_")]
        
        if styled_tags:
            # Use the last styled tag found.
            tag = styled_tags[-1]
            tag_font    = app.text_editor.tag_cget(tag, "font")
            tag_fg      = app.text_editor.tag_cget(tag, "foreground")
            tag_justify = app.text_editor.tag_cget(tag, "justify")
            if tag_font:
                current_font   = tkfont.Font(font=tag_font)
                current_family = current_font.actual("family")
                current_size   = current_font.actual("size")
                current_weight = current_font.actual("weight")
                current_slant  = current_font.actual("slant")
            else:
                current_family, current_size, current_weight, current_slant = "Arial", 12, "normal", "roman"
            font_var.set(current_family)
            size_var.set(current_size)
            bold_var.set(current_weight == "bold")
            italic_var.set(current_slant == "italic")
            align_var.set(tag_justify if tag_justify else "left")
            color_var.set(tag_fg if tag_fg else "black")
        else:
            # No styled tag found at the insertion point; revert to defaults.
            font_var.set("Arial")
            size_var.set(12)
            bold_var.set(False)
            italic_var.set(False)
            align_var.set("left")
            color_var.set("black")
    
    # Bind the update_options_from_cursor function to cursor movement events.
    def local_update_options(event):
        update_options_from_cursor()
    app.text_editor.bind("<ButtonRelease-1>", local_update_options)
    app.text_editor.bind("<KeyRelease>", local_update_options)
    
    # --- Function to apply style only to the selected text immediately ---
    def update_text_style():
        global style_counter
        weight = "bold" if bold_var.get() else "normal"
        slant  = "italic" if italic_var.get() else "roman"
        f = tkfont.Font(family=font_var.get(), size=size_var.get(), weight=weight, slant=slant)
        # Get the currently selected text range.
        sel_ranges = app.text_editor.tag_ranges("sel")
        if len(sel_ranges) < 2:
            return  # No selection; do nothing.
        start, end = sel_ranges[0], sel_ranges[1]
        # Generate a unique tag name.
        style_counter += 1
        tag_name = f"styled_{style_counter}"
        # Configure the new tag with the current style options.
        app.text_editor.tag_configure(tag_name,
                                      font=f,
                                      foreground=color_var.get(),
                                      justify=align_var.get())
        # Apply the new tag only to the selected text.
        app.text_editor.tag_add(tag_name, start, end)
    
    # --- Now create the UI controls for each style option.
    
    # Font OptionMenu with immediate update:
    tk.Label(left_panel, text="Font:").pack(anchor="w", padx=5)
    fonts = ["Arial", "Times New Roman", "Courier", "Helvetica"]
    tk.OptionMenu(left_panel, font_var, *fonts, command=lambda x: update_text_style()).pack(fill="x", padx=5)
    
    # Font Size Spinbox with immediate update:
    tk.Label(left_panel, text="Size:").pack(anchor="w", padx=5)
    size_spin = tk.Spinbox(left_panel, from_=8, to=72, textvariable=size_var, command=update_text_style)
    size_spin.pack(fill="x", padx=5)
    # Bind key release in case the user types a value manually.
    size_spin.bind("<KeyRelease>", lambda e: update_text_style())
    
    # Bold and Italic Checkbuttons with immediate update:
    tk.Checkbutton(left_panel, text="Bold", variable=bold_var, command=update_text_style).pack(anchor="w", padx=5)
    tk.Checkbutton(left_panel, text="Italic", variable=italic_var, command=update_text_style).pack(anchor="w", padx=5)
    
    # Alignment Radiobuttons with immediate update:
    tk.Label(left_panel, text="Alignment:").pack(anchor="w", padx=5)
    align_frame = tk.Frame(left_panel)
    align_frame.pack(anchor="w", padx=5)
    tk.Radiobutton(align_frame, text="Left", variable=align_var, value="left", command=update_text_style).pack(side="left")
    tk.Radiobutton(align_frame, text="Center", variable=align_var, value="center", command=update_text_style).pack(side="left")
    tk.Radiobutton(align_frame, text="Right", variable=align_var, value="right", command=update_text_style).pack(side="left")
    
    # Color chooser button with immediate update:
    def choose_color():
        chosen = colorchooser.askcolor()[1]
        if chosen:
            color_var.set(chosen)
            update_text_style()
    tk.Button(left_panel, text="Text Color", command=choose_color).pack(pady=5, padx=5, fill="x")


def update_component_text(comp, text_editor):
    new_text = text_editor.get("1.0", tk.END).strip()
    comp.label_text = new_text
    comp.label_widget.config(text=new_text)