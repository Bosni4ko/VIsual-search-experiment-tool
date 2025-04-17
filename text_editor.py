import tkinter as tk
from tkinter import ttk, font, colorchooser
import uuid
# def setup_text_editor(app, main_panel, comp):
#     # pull saved family/size (or fall back to your defaults)
#     default_family = getattr(comp, "font_family", "Arial")
#     default_size   = getattr(comp, "font_size", 12)

#     # create the widget with that font
#     text_editor = tk.Text(main_panel, font=(default_family, default_size))
#     text_editor.pack(expand=True, fill="both")
#     text_editor.delete("1.0", "end")
#     text_editor.insert("1.0", comp.label_text)

#     # Reapply stored formatting styles if available.
#     if hasattr(comp, "text_styles") and comp.text_styles:
#         for tag, data in comp.text_styles.items():
#             # Configure the tag using the stored configuration.
#             text_editor.tag_configure(tag,
#                                       font=data["config"].get("font"),
#                                       foreground=data["config"].get("foreground"),
#                                       justify=data["config"].get("justify"))
#             # Reapply the tag over each stored range.
#             for start, end in data["ranges"]:
#                 text_editor.tag_add(tag, start, end)

#     # Bind update on focus loss.
#     text_editor.bind("<FocusOut>", lambda e: update_component_text(comp, text_editor))
#     app.text_editor = text_editor



# def setup_text_options(app, left_panel, comp):
#     """
#     Sets up the left panel with text formatting options.
#     When the user clicks in the text editor, the options update based on the formatting
#     at the current caret position.
#     Changes in the options update the style immediately on the selected text.
#     Each applied style uses a unique tag.
#     """
#     global style_counter  # Global counter for unique style tags.
#     style_counter = 0
    
#     # --- Create a label for the options panel ---
#     tk.Label(left_panel, text="Text Options", font=("Segoe UI", 12, "bold")).pack(pady=5)
    
#     # Variables to store style options.
#     font_var   = tk.StringVar(value="Arial")
#     size_var   = tk.IntVar(value=12)
#     bold_var   = tk.BooleanVar(value=False)
#     italic_var = tk.BooleanVar(value=False)
#     align_var  = tk.StringVar(value="left")
#     color_var  = tk.StringVar(value="black")
    
#     # --- Function to update the left-panel controls based on the text at the insertion point ---
#     def update_options_from_cursor(event=None):
#         # Get the index of the current insertion (caret) point.
#         index = app.text_editor.index("insert")
#         tags_at_index = app.text_editor.tag_names(index)
#         # Filter for tags that start with "styled_"
#         styled_tags = [tag for tag in tags_at_index if tag.startswith("styled_")]
        
#         # If no styled tag is found at "insert", try one character back.
#         if not styled_tags:
#             try:
#                 index_before = app.text_editor.index(f"{index} - 1c")
#             except tk.TclError:
#                 index_before = index
#             tags_at_before = app.text_editor.tag_names(index_before)
#             styled_tags = [tag for tag in tags_at_before if tag.startswith("styled_")]
        
#         if styled_tags:
#             # Use the last styled tag found.
#             tag = styled_tags[-1]
#             tag_font    = app.text_editor.tag_cget(tag, "font")
#             tag_fg      = app.text_editor.tag_cget(tag, "foreground")
#             tag_justify = app.text_editor.tag_cget(tag, "justify")
#             if tag_font:
#                 current_font   = tkfont.Font(font=tag_font)
#                 current_family = current_font.actual("family")
#                 current_size   = current_font.actual("size")
#                 current_weight = current_font.actual("weight")
#                 current_slant  = current_font.actual("slant")
#             else:
#                 current_family, current_size, current_weight, current_slant = "Arial", 12, "normal", "roman"
#             font_var.set(current_family)
#             size_var.set(current_size)
#             bold_var.set(current_weight == "bold")
#             italic_var.set(current_slant == "italic")
#             align_var.set(tag_justify if tag_justify else "left")
#             color_var.set(tag_fg if tag_fg else "black")
#         else:
#             # No styled tag found at the insertion point; revert to defaults.
#             font_var.set("Arial")
#             size_var.set(12)
#             bold_var.set(False)
#             italic_var.set(False)
#             align_var.set("left")
#             color_var.set("black")
    
#     # Bind the update_options_from_cursor function to cursor movement events.
#     def local_update_options(event):
#         update_options_from_cursor()
#     app.text_editor.bind("<ButtonRelease-1>", local_update_options)
#     app.text_editor.bind("<KeyRelease>", local_update_options)
    
#     # --- Function to apply style only to the selected text immediately ---
#     def update_text_style():
#         global style_counter
#         weight = "bold" if bold_var.get() else "normal"
#         slant  = "italic" if italic_var.get() else "roman"
#         f = tkfont.Font(family=font_var.get(), size=size_var.get(), weight=weight, slant=slant)
#         # Get the currently selected text range.
#         sel_ranges = app.text_editor.tag_ranges("sel")
#         if len(sel_ranges) < 2:
#             return  # No selection; do nothing.
#         start, end = sel_ranges[0], sel_ranges[1]
#         # Generate a unique tag name.
#         style_counter += 1
#         tag_name = f"styled_{style_counter}"
#         # Configure the new tag with the current style options.
#         app.text_editor.tag_configure(tag_name,
#                                       font=f,
#                                       foreground=color_var.get(),
#                                       justify=align_var.get())
#         # Apply the new tag only to the selected text.
#         app.text_editor.tag_add(tag_name, start, end)
    
#     # --- Now create the UI controls for each style option.
    
#     # Font OptionMenu with immediate update:
#     tk.Label(left_panel, text="Font:").pack(anchor="w", padx=5)
#     fonts = ["Arial", "Times New Roman", "Courier", "Helvetica"]
#     tk.OptionMenu(left_panel, font_var, *fonts, command=lambda x: update_text_style()).pack(fill="x", padx=5)
    
#     # Font Size Spinbox with immediate update:
#     tk.Label(left_panel, text="Size:").pack(anchor="w", padx=5)
#     size_spin = tk.Spinbox(left_panel, from_=8, to=72, textvariable=size_var, command=update_text_style)
#     size_spin.pack(fill="x", padx=5)
#     # Bind key release in case the user types a value manually.
#     size_spin.bind("<KeyRelease>", lambda e: update_text_style())
    
#     # Bold and Italic Checkbuttons with immediate update:
#     tk.Checkbutton(left_panel, text="Bold", variable=bold_var, command=update_text_style).pack(anchor="w", padx=5)
#     tk.Checkbutton(left_panel, text="Italic", variable=italic_var, command=update_text_style).pack(anchor="w", padx=5)
    
#     # Alignment Radiobuttons with immediate update:
#     tk.Label(left_panel, text="Alignment:").pack(anchor="w", padx=5)
#     align_frame = tk.Frame(left_panel)
#     align_frame.pack(anchor="w", padx=5)
#     tk.Radiobutton(align_frame, text="Left", variable=align_var, value="left", command=update_text_style).pack(side="left")
#     tk.Radiobutton(align_frame, text="Center", variable=align_var, value="center", command=update_text_style).pack(side="left")
#     tk.Radiobutton(align_frame, text="Right", variable=align_var, value="right", command=update_text_style).pack(side="left")
    
#     # Color chooser button with immediate update:
#     def choose_color():
#         chosen = colorchooser.askcolor()[1]
#         if chosen:
#             color_var.set(chosen)
#             update_text_style()
#     tk.Button(left_panel, text="Text Color", command=choose_color).pack(pady=5, padx=5, fill="x")


# def update_component_text(comp, text_editor):
#     # Save the plain text.
#     new_text = text_editor.get("1.0", "end-1c")
#     comp.label_text = new_text

#     # now grab the widget’s current font and size …
#     editor_font = text_editor.cget("font")
#     f = tkfont.Font(font=editor_font)
#     comp.font_family = f.actual("family")
#     comp.font_size   = f.actual("size")

#     # DEBUG:
#     print(f"[DEBUG] Saved component.font_family = {comp.font_family!r}, font_size = {comp.font_size}")
#     # Save formatting information.
#     comp.text_styles = {}  # clear previous styles
#     for tag in text_editor.tag_names():
#         if tag.startswith("styled_"):
#             ranges = text_editor.tag_ranges(tag)
#             if ranges and len(ranges) >= 2:
#                 range_list = []
#                 for i in range(0, len(ranges), 2):
#                     start = text_editor.index(ranges[i])
#                     end   = text_editor.index(ranges[i+1])
#                     range_list.append((start, end))
#                 config = {
#                     "font": text_editor.tag_cget(tag, "font"),
#                     "foreground": text_editor.tag_cget(tag, "foreground"),
#                     "justify": text_editor.tag_cget(tag, "justify")
#                 }
#                 comp.text_styles[tag] = {"ranges": range_list, "config": config}

#     # --- now also save the editor’s default font + size ---
#     editor_font = text_editor.cget("font")
#     f = tkfont.Font(font=editor_font)
#     comp.font_family = f.actual("family")
#     comp.font_size   = f.actual("size")


def setup_text_editor(app, main_panel, comp):
    """
    Creates and packs a Text widget into the main_panel for code editing.
    Uses exportselection=False so selection stays visible when focus moves away.
    Assigns the widget to comp.text_widget.
    """
    comp.text_widget = tk.Text(
        main_panel,
        wrap='none',
        undo=True,
        font=('Courier', 12),
        exportselection=False
    )
    comp.text_widget.pack(fill=tk.BOTH, expand=True)


def setup_text_options(app, left_panel, comp):
    """
    Creates text formatting options in the left_panel:
      - Font family selector
      - Font size spinbox
      - Bold and Italic toggles
      - Font color chooser
      - Text alignment (left, center, right)

    Uses record_selection to capture selected range before any control steals focus.
    """
    def record_selection(event=None):
        # Capture current selection indices
        try:
            comp._sel_start = comp.text_widget.index('sel.first')
            comp._sel_end = comp.text_widget.index('sel.last')
        except tk.TclError:
            comp._sel_start = comp._sel_end = None

    # Font family selector
    families = sorted(font.families())
    comp.font_family_var = tk.StringVar(value='Courier')
    font_menu = ttk.Combobox(
        left_panel,
        textvariable=comp.font_family_var,
        values=families,
        state='readonly'
    )
    font_menu.pack(fill=tk.X, pady=2)
    font_menu.bind('<Button-1>', record_selection)
    font_menu.bind('<<ComboboxSelected>>', lambda e: update_font(comp))

    # Font size spinbox
    comp.font_size_var = tk.IntVar(value=12)
    size_spin = ttk.Spinbox(
        left_panel,
        from_=8,
        to=72,
        textvariable=comp.font_size_var,
        width=5,
        command=lambda: update_font(comp)
    )
    size_spin.pack(fill=tk.X, pady=2)
    size_spin.bind('<Button-1>', record_selection)

    # Bold and Italic toggles
    comp.bold_var = tk.BooleanVar(value=False)
    bold_check = ttk.Checkbutton(
        left_panel,
        text='Bold',
        variable=comp.bold_var,
        command=lambda: update_font(comp)
    )
    bold_check.pack(anchor='w', pady=2)
    bold_check.bind('<Button-1>', record_selection)

    comp.italic_var = tk.BooleanVar(value=False)
    italic_check = ttk.Checkbutton(
        left_panel,
        text='Italic',
        variable=comp.italic_var,
        command=lambda: update_font(comp)
    )
    italic_check.pack(anchor='w', pady=2)
    italic_check.bind('<Button-1>', record_selection)

    # Font color chooser
    color_button = ttk.Button(
        left_panel,
        text='Font Color',
        command=lambda: (record_selection(), choose_color(comp))
    )
    color_button.pack(fill=tk.X, pady=2)

    # Text alignment options
    comp.align_var = tk.StringVar(value='left')
    align_frame = ttk.LabelFrame(left_panel, text='Alignment')
    align_frame.pack(fill=tk.X, pady=5)
    for align in ('left', 'center', 'right'):
        rb = ttk.Radiobutton(
            align_frame,
            text=align.capitalize(),
            value=align,
            variable=comp.align_var,
            command=lambda: set_alignment(comp)
        )
        rb.pack(side=tk.LEFT, padx=5)
        rb.bind('<Button-1>', record_selection)


def update_font(comp):
    """
    Applies the selected font attributes only to the recorded selection range.
    Uses a unique tag per application so previous ranges aren’t affected.
    """
    text = comp.text_widget
    start = getattr(comp, '_sel_start', None)
    end = getattr(comp, '_sel_end', None)
    if not start:
        return
    fam = comp.font_family_var.get()
    size = comp.font_size_var.get()
    weight = 'bold' if comp.bold_var.get() else 'normal'
    slant = 'italic' if comp.italic_var.get() else 'roman'
    fnt = font.Font(family=fam, size=size, weight=weight, slant=slant)
    tag_name = f"font_{uuid.uuid4().hex}"
    text.tag_configure(tag_name, font=fnt)
    text.tag_add(tag_name, start, end)
    text.focus_set()


def choose_color(comp):
    """
    Opens a color chooser and applies the selected color only to the recorded selection.
    Uses a unique tag per application so previous ranges aren’t affected.
    """
    text = comp.text_widget
    color = colorchooser.askcolor(title='Choose font color')[1]
    if not color:
        return
    start = getattr(comp, '_sel_start', None)
    end = getattr(comp, '_sel_end', None)
    if not start:
        return
    tag_name = f"color_{uuid.uuid4().hex}"
    text.tag_configure(tag_name, foreground=color)
    text.tag_add(tag_name, start, end)
    text.focus_set()


def set_alignment(comp):
    """
    Sets justification (left, center, right) on the recorded selection or entire text if none.
    Uses a unique tag so previous alignments aren’t overwritten.
    """
    text = comp.text_widget
    align = comp.align_var.get()
    start = getattr(comp, '_sel_start', None)
    end = getattr(comp, '_sel_end', None)
    if not start:
        start, end = '1.0', 'end'
    tag_name = f"align_{uuid.uuid4().hex}"
    text.tag_configure(tag_name, justify=align)
    text.tag_add(tag_name, start, end)
    text.focus_set()

