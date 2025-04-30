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
    return style
