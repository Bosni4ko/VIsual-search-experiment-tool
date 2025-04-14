import tkinter as tk
from tkinter import font as tkfont, colorchooser
def setup_text_editor(app, main_panel, comp):
    text_editor = tk.Text(main_panel)
    text_editor.pack(expand=True, fill="both")
    text_editor.delete("1.0", tk.END)
    text_editor.insert("1.0", comp.label_text)
    text_editor.bind("<FocusOut>", lambda e: update_component_text(comp, text_editor))
    app.text_editor = text_editor

# Create text styling options in the left panel.
def setup_text_options(app, left_panel, comp):
    tk.Label(left_panel, text="Text Options", font=("Segoe UI", 12, "bold")).pack(pady=5)
    font_var = tk.StringVar(value="Arial")
    size_var = tk.IntVar(value=12)
    bold_var = tk.BooleanVar(value=False)
    italic_var = tk.BooleanVar(value=False)
    align_var = tk.StringVar(value="left")
    color_var = tk.StringVar(value="black")
    
    # Option for Font
    tk.Label(left_panel, text="Font:").pack(anchor="w", padx=5)
    fonts = ["Arial", "Times New Roman", "Courier", "Helvetica"]
    tk.OptionMenu(left_panel, font_var, *fonts, command=lambda x: None).pack(fill="x", padx=5)
    
    # Option for Size
    tk.Label(left_panel, text="Size:").pack(anchor="w", padx=5)
    tk.Spinbox(left_panel, from_=8, to=72, textvariable=size_var).pack(fill="x", padx=5)
    
    # Checkboxes for Bold and Italic
    tk.Checkbutton(left_panel, text="Bold", variable=bold_var).pack(anchor="w", padx=5)
    tk.Checkbutton(left_panel, text="Italic", variable=italic_var).pack(anchor="w", padx=5)
    
    # Radio Buttons for Alignment
    tk.Label(left_panel, text="Alignment:").pack(anchor="w", padx=5)
    align_frame = tk.Frame(left_panel)
    align_frame.pack(anchor="w", padx=5)
    tk.Radiobutton(align_frame, text="Left", variable=align_var, value="left").pack(side="left")
    tk.Radiobutton(align_frame, text="Center", variable=align_var, value="center").pack(side="left")
    tk.Radiobutton(align_frame, text="Right", variable=align_var, value="right").pack(side="left")
    
    # Color chooser button
    tk.Button(left_panel, text="Text Color").pack(pady=5, padx=5, fill="x")
    
    tk.Button(left_panel, text="Apply Style").pack(pady=5, padx=5, fill="x")

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
        
        def choose_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_var.set(color)
                update_text_style()
        tk.Button(left_panel, text="Text Color", command=choose_color).pack(pady=5, padx=5, fill="x")
        tk.Button(left_panel, text="Apply Style", command=update_text_style).pack(pady=5, padx=5, fill="x")

def update_component_text(comp, text_editor):
    new_text = text_editor.get("1.0", tk.END).strip()
    comp.label_text = new_text
    comp.label_widget.config(text=new_text)