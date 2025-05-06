import tkinter as tk
from tkinter import ttk

# Theme configuration for the experiment app

# Color palette
BG_COLOR = "#f0f0f0"
CANVAS_BG = "#ffffff"
ACCENT_COLOR = "#007acc"  # Example accent color for buttons or highlights

FONT_FAMILY = "Segoe UI"
FONT_FAMILY_SEMI_BOLD = "Segoe UI Semibold"
BUTTON_FONT = (FONT_FAMILY, 14, "bold")
SMALL_BUTTON_FONT = (FONT_FAMILY, 10)
LABEL_FONT = (FONT_FAMILY, 20, "bold")
ENTRY_FONT = (FONT_FAMILY_SEMI_BOLD, 12)      
COMBO_FONT = (FONT_FAMILY_SEMI_BOLD, 12)
METADATA_ENTRY=(FONT_FAMILY,10)  
SELECT_METADATA=(FONT_FAMILY, 12)
ADD_ITEM_FONT = (FONT_FAMILY, 8)
COMPONENT_FONT        = (FONT_FAMILY, 14,"bold")  # inside the colored block
COMPONENT_LABEL_FONT  = (FONT_FAMILY_SEMI_BOLD, 11)            # under the block in the palette
SMALL_COMBO_FONT = (FONT_FAMILY, 9)
SMALL_TEXT_FONT     = (FONT_FAMILY, 12)   # 
SMALL_TEXT_SEMIBOLD = (FONT_FAMILY_SEMI_BOLD, 13)

# Padding
BUTTON_PADDING = 10
SMALL_BUTTON_PADDING = (2, 2)
ADD_ITEM_PADDING = (1, 1)

def apply_theme(root: tk.Tk) -> ttk.Style:
    """
    Apply a consistent theme to the given root window.
    """
    # Root window background
    root.configure(bg=BG_COLOR)

    # Create and configure ttk styles
    style = ttk.Style(root)
    style.theme_use("clam")

    # Button styles
    style.configure("TButton", font=BUTTON_FONT, padding=BUTTON_PADDING)
    style.configure(
        "Small.TButton", font=SMALL_BUTTON_FONT, padding=SMALL_BUTTON_PADDING
    )
    style.configure("Accent.TButton", font=BUTTON_FONT, padding=BUTTON_PADDING, foreground="white", background=ACCENT_COLOR)

    # Label and Entry
    style.configure("TLabel", font=LABEL_FONT, background=BG_COLOR)
    style.configure("TEntry", font=ENTRY_FONT)

    # All default comboboxes (including metadata selector)
    style.configure("TCombobox", font=SELECT_METADATA)

    style.configure(
        "TCombobox.Listbox",
        font=SELECT_METADATA,
        background=CANVAS_BG,
        foreground="#000000",
    )
    # Language dropdown (inherits bold combo font)
    style.configure(
        "Language.TCombobox",
        font=SELECT_METADATA,
        padding=4,
        fieldbackground=CANVAS_BG,
        background=CANVAS_BG,
    )
    style.map(
        "Language.TCombobox",
        fieldbackground=[("readonly", CANVAS_BG)],
        foreground=[("disabled", "#888888"), ("!disabled", "#000000")],
    )

    # Add-item button (small, inline)
    style.configure(
        "AddItem.TButton", font=ADD_ITEM_FONT, padding=ADD_ITEM_PADDING
    )

    # Canvas default background (for scrollable frames)
    style.configure("TFrame", background=BG_COLOR)

        # Combobox (e.g. language dropdown)
    style.configure(
        "Language.TCombobox",
        font=ENTRY_FONT,
        padding=4,
        fieldbackground=CANVAS_BG,
        background=CANVAS_BG,
    )
    style.map(
        "Language.TCombobox",
        fieldbackground=[("readonly", CANVAS_BG)],
        foreground=[("disabled", "#888888"), ("!disabled", "#000000")],
    )
     # Combobox for font family & size
    style.configure(
        "TextOpt.TCombobox",
        font=COMBO_FONT,
        padding=(5, 4),
        fieldbackground=CANVAS_BG,
        background=CANVAS_BG,
        foreground="#333333",
    )
    style.map(
        "TextOpt.TCombobox",
        fieldbackground=[("readonly", CANVAS_BG)],
        foreground=[("disabled", "#888888"), ("!disabled", "#333333")],
    )

    # Spinbox
    style.configure(
        "TextOpt.TSpinbox",
        font=COMBO_FONT,
        padding=(5, 4),
        background="#ffffff",       # overall bg
        fieldbackground="#ffffff",  # entry area
        arrowsize=14,
        arrowcolor="#333333",       # dark arrows
    )

    # Checkbuttons for Bold/Italic
    style.configure(
        "TextOpt.TCheckbutton",
        font=(FONT_FAMILY, 14),     # ↑ bump text size to 14pt
        padding=(8, 8),             # ↑ more space around box & text
        indicatorpadding=10,        # ↑ extra gap between box and label
        background=BG_COLOR,
    )
    style.map(
        "TextOpt.TCheckbutton",
        background=[("active", CANVAS_BG)],
    )

    # Radiobuttons for Alignment
    style.configure(
        "TextOpt.TRadiobutton",
        font=SMALL_BUTTON_FONT,
        background=BG_COLOR,
        padding=(3, 3),
    )
    style.map(
        "TextOpt.TRadiobutton",
        background=[("active", CANVAS_BG)],
    )

    default_bg = style.lookup("TButton", "background") or "#d9d9d9"
    # Make your “Font Color” button stand out with accent styling
    style.configure(
        "TextOptAccent.TButton",
        font=(FONT_FAMILY, 12, "bold"),
        foreground="black",     # black text
        background=default_bg,  # grey button face
        relief="raised",
        padding=(6, 4),
    )
    style.map(
        "TextOptAccent.TButton",
        # on press/hover, use the same default so there’s no blue flash
        background=[("active", default_bg)],
        foreground=[("disabled", "#888888"), ("!disabled", "black")],
    )
       # ——— Checkbuttons (Bold/Italic): larger clickable area & text ———
    style.configure(
        "TextOpt.TCheckbutton",
        font=(FONT_FAMILY, 12),    # ↑ match spinbox font size
        padding=(4, 4),            # ↑ a bit more space around the box
        background=BG_COLOR,
    )
    style.map(
        "TextOpt.TCheckbutton",
        background=[("active", CANVAS_BG)],
    )
    # ——— Alignment LabelFrame ———
    style.configure(
        "TextOptAlign.TLabelframe",
        background=CANVAS_BG,
        borderwidth=0,
        padding=(5,8)         
    )
#    Center the text in the header     :
    style.configure(
        "TextOptAlign.TLabelframe.Label",
        font=(FONT_FAMILY, 12, "bold"),
        background=CANVAS_BG,
        foreground="#333333",
        anchor="center"        # try to center the label text
    )

    # ——— Alignment Radiobuttons ———
    style.configure(
        "TextOptAlign.TRadiobutton",
        font=(FONT_FAMILY, 12),            # bump text size
        background=CANVAS_BG,              # white bg
        padding=(6, 6),
    )
    style.map(
        "TextOptAlign.TRadiobutton",
        background=[("active", CANVAS_BG)],
    )
    # —— Small Label ——  
    style.configure(
        "Small.TLabel",
        font=SMALL_TEXT_SEMIBOLD,
        background=CANVAS_BG,
        foreground="#333333"   # whatever text color you want
    )

    # —— Small Button ——  
    style.configure(
        "Small.TButton",
        font=SMALL_TEXT_SEMIBOLD,
        padding=SMALL_BUTTON_PADDING,
        background=CANVAS_BG,
        foreground="#000000"
    )
    style.map(
        "Small.TButton",
        background=[("active", CANVAS_BG)],
        foreground=[("disabled", "#888888"), ("!disabled", "#000000")]
    )

    # —— Small Entry ——  
    style.configure(
        "Small.TEntry",
        font=SMALL_TEXT_SEMIBOLD,
        fieldbackground=CANVAS_BG,
        background=CANVAS_BG
    )
    style.map(
        "Small.TEntry",
        fieldbackground=[
            ("disabled", "#A9A9A9"),   # dark grey when disabled
            ("!disabled", CANVAS_BG)
        ],
        background=[
            ("disabled", "#A9A9A9"),   # dark grey when disabled
            ("!disabled", CANVAS_BG)
        ]
    )
    style.map(
        "TEntry",
        fieldbackground=[
            ("readonly", "#A9A9A9"),   # grey for readonly
            ("!readonly", CANVAS_BG)
        ],
        background=[
            ("readonly", "#A9A9A9"),
            ("!readonly", CANVAS_BG)
        ]
    )

    style.configure(
        "Small.TCombobox",
        font=SMALL_COMBO_FONT,
        fieldbackground=CANVAS_BG,
        background=CANVAS_BG,
        foreground="#000000",
    )
    style.configure(
        "Small.TCombobox.Listbox",
        font=SMALL_COMBO_FONT,
        background=CANVAS_BG,
        foreground="#000000",
    )
    style.map(
        "Small.TCombobox",
        fieldbackground=[("readonly", CANVAS_BG), ("!readonly", CANVAS_BG)],
        background=[("readonly", CANVAS_BG), ("!readonly", CANVAS_BG)]
    )
    # —— Small Checkbutton ——  
    style.configure(
        "Small.TCheckbutton",
        font=SMALL_TEXT_FONT,       # your 10pt or 9pt font tuple
        background=CANVAS_BG,       # white widget background
        foreground="#333333",       # dark text
        indicatorbackground=CANVAS_BG,  # white box background
        indicatorforeground="#333333",  # dark check mark
        padding=(4, 4),             # comfortable click area
    )

    style.map(
        "Small.TCheckbutton",
        background=[("active", CANVAS_BG)],        # stay white on hover
        foreground=[("disabled", "#888888"),       # greyed-out when disabled
                    ("!disabled", "#333333")],
        indicatorforeground=[("selected", "#007acc"),  # accent color when checked
                            ("!selected", "#333333")],
    )
    return style

