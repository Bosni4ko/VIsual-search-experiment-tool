import tkinter as tk
from tkinter import ttk, font, colorchooser
import uuid
import tkinter.font as tkfont

import tkinter as tk
from tkinter import ttk, font, colorchooser
import uuid
import tkinter.font as tkfont


def setup_text_editor(app, main_panel, comp):
    """
    Creates and packs a Text widget into the main_panel for code editing.
    Uses exportselection=False so selection stays visible when focus moves away.
    If the component already has saved text+formatting, loads it.
    """
    comp.text_widget = tk.Text(
        main_panel,
        wrap='word',  # break long words to new line
        undo=True,
        font=('Courier', 12),
        exportselection=False
    )
    comp.text_widget.pack(fill=tk.BOTH, expand=True)
    # Load any previously saved content and styling
    try:
        load_formatting(comp)
    except Exception:
        pass  # no saved state yet, or errors in loading


def setup_text_options(app, left_panel, comp):
    """
    Creates text formatting options in the left_panel:
      - Font family selector
      - Font size spinbox
      - Bold and Italic toggles
      - Font color chooser + preview
      - Text alignment (left, center, right)

    Uses record_selection to capture selected range before any control steals focus.
    Also binds cursor events to refresh formatting controls after options exist.
    """

    left_panel.configure(padx=10, pady=10)
    
    def record_selection(event=None):
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
        state='readonly',
        style='TextOpt.TCombobox'
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
        style='TextOpt.TSpinbox',
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
        command=lambda: update_font(comp),
        style='TextOpt.TCheckbutton'
    )
    bold_check.pack(anchor='w', pady=2)
    bold_check.bind('<Button-1>', record_selection)

    comp.italic_var = tk.BooleanVar(value=False)
    italic_check = ttk.Checkbutton(
        left_panel,
        text='Italic',
        variable=comp.italic_var,
        command=lambda: update_font(comp),
        style='TextOpt.TCheckbutton'
    )
    italic_check.pack(anchor='w', pady=2)
    italic_check.bind('<Button-1>', record_selection)

    # Font color chooser + preview
    comp.color_var = tk.StringVar(value='#000000')
    color_frame = tk.Frame(left_panel)
    color_frame.pack(fill=tk.X, pady=2)
    color_button = ttk.Button(
        color_frame,
        text='Font Color',
        width=12,
        style='TextOptAccent.TButton',
        command=lambda: (record_selection(), choose_color(comp))
    )
    color_button.pack(side=tk.LEFT)
    comp.color_preview = tk.Label(
        color_frame,
        text='   ',
        bg=comp.color_var.get(),
        width=4,
        height=2,
        relief='solid',
        borderwidth=1
    )
    comp.color_preview.pack(side=tk.LEFT, padx=8)

    # Text alignment options
    comp.align_var = tk.StringVar(value='left')
    align_frame = ttk.LabelFrame(left_panel, text='Alignment',style='TextOptAlign.TLabelframe',labelanchor='n')
    align_frame.pack(fill=tk.X, pady=(25, 5))
    for align in ('left', 'center', 'right'):
        rb = ttk.Radiobutton(
            align_frame,
            text=align.capitalize(),
            value=align,
            variable=comp.align_var,
            command=lambda: set_alignment(comp),
            style='TextOptAlign.TRadiobutton'
        )
        rb.pack(side=tk.LEFT, padx=5)
        rb.bind('<Button-1>', record_selection)

    # Bind events for refreshing controls now that vars exist
    comp.text_widget.bind('<KeyRelease>', lambda e: refresh_formatting_options(comp))
    comp.text_widget.bind('<ButtonRelease-1>', lambda e: refresh_formatting_options(comp))
    # Initial sync of controls
    refresh_formatting_options(comp)


def update_font(comp):
    text = comp.text_widget
    start = getattr(comp, '_sel_start', None)
    end = getattr(comp, '_sel_end', None)
    if not start:
        return
    fam = comp.font_family_var.get()
    size = comp.font_size_var.get()
    weight = 'bold' if comp.bold_var.get() else 'normal'
    slant = 'italic' if comp.italic_var.get() else 'roman'
    color = comp.color_var.get()
    fnt = font.Font(family=fam, size=size, weight=weight, slant=slant)
    tag_name = f"font_{uuid.uuid4().hex}"
    text.tag_configure(tag_name, font=fnt, foreground=color)
    text.tag_add(tag_name, start, end)
    text.focus_set()


def choose_color(comp):
    text = comp.text_widget
    color = colorchooser.askcolor(title='Choose font color')[1]
    if not color:
        return
    comp.color_var.set(color)
    comp.color_preview.config(bg=color)
    start = getattr(comp, '_sel_start', None)
    end = getattr(comp, '_sel_end', None)
    if not start:
        return
    tag_name = f"color_{uuid.uuid4().hex}"
    text.tag_configure(tag_name, foreground=color)
    text.tag_add(tag_name, start, end)
    text.focus_set()


def set_alignment(comp):
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


def save_formatting(comp):
    """
    Stores the current text and all styling tags into the component,
    but breaks the font out into explicit family/size/weight/slant.
    """
    text = comp.text_widget
    comp.saved_text = text.get('1.0', 'end-1c')
    comp.saved_tags = []

    for tag in text.tag_names():
        ranges = text.tag_ranges(tag)
        if not ranges:
            continue

        # pull the real Font object (or build one)…
        font_spec = text.tag_cget(tag, 'font')
        try:
            fobj = tkfont.nametofont(font_spec)
        except tk.TclError:
            fobj = tkfont.Font(font=font_spec)

        # now get the actual attributes
        font_info = {
            'family': fobj.actual('family'),
            'size':   fobj.actual('size'),
            'weight': fobj.actual('weight'),
            'slant':  fobj.actual('slant'),
        }

        tag_info = {
            'name':       tag,
            'ranges':     [(str(ranges[i]), str(ranges[i+1]))
                           for i in range(0, len(ranges), 2)],
            'font_info':  font_info,
            'foreground': text.tag_cget(tag, 'foreground'),
            'justify':    text.tag_cget(tag, 'justify'),
        }
        comp.saved_tags.append(tag_info)


def load_formatting(comp):
    """
    Loads previously saved text and styling tags from the component into the editor,
    reconstructing each Font from the saved family/size/weight/slant.
    """
    text = comp.text_widget
    text.delete('1.0', 'end')
    if not hasattr(comp, 'saved_text'):
        return

    text.insert('1.0', comp.saved_text)

    for tag_info in getattr(comp, 'saved_tags', []):
        name = tag_info['name']
        opts = {}

        # rebuild the Font if we have font_info
        fi = tag_info.get('font_info')
        if fi:
            f = tkfont.Font(**fi)
            opts['font'] = f

        fg = tag_info.get('foreground')
        if fg:
            opts['foreground'] = fg

        just = tag_info.get('justify')
        if just:
            opts['justify'] = just

        if opts:
            text.tag_configure(name, **opts)

        for start, end in tag_info['ranges']:
            text.tag_add(name, start, end)

    text.focus_set()


def refresh_formatting_options(comp,
                                default_family='Courier',
                                default_size=12,
                                default_color='#000000',
                                default_align='left'):
    """
    Syncs the controls to the style at sel.first if text is selected,
    else at the character before the cursor. Whitespace or invalid spots
    revert to defaults.
    """
    text = comp.text_widget

    # 1) Decide probe index: selection start if selecting, else insert-1c
    try:
        sel_start = text.index('sel.first')
    except tk.TclError:
        sel_start = None

    if sel_start:
        probe = sel_start
    else:
        try:
            probe = text.index('insert -1c')
        except tk.TclError:
            probe = None

    # 2) If probe is missing or is whitespace, reset to defaults
    if not probe or text.get(probe).isspace():
        comp.font_family_var.set(default_family)
        comp.font_size_var.set(default_size)
        comp.bold_var.set(False)
        comp.italic_var.set(False)
        comp.color_var.set(default_color)
        comp.color_preview.config(bg=default_color)
        comp.align_var.set(default_align)
        return

    # 3) Otherwise, look at all tags at that position
    fam, size, weight, slant = default_family, default_size, 'normal', 'roman'
    fg, just = None, default_align
    for tag in text.tag_names(probe):
        fnt_name = text.tag_cget(tag, 'font')
        if fnt_name:
            try:
                fobj = tkfont.nametofont(fnt_name)
            except tk.TclError:
                fobj = tkfont.Font(font=fnt_name)
            fam = fobj.actual('family')
            size = fobj.actual('size')
            weight = fobj.actual('weight')
            slant = fobj.actual('slant')
        c = text.tag_cget(tag, 'foreground')
        if c:
            fg = c
        j = text.tag_cget(tag, 'justify')
        if j:
            just = j

    # 4) Apply back to controls
    comp.font_family_var.set(fam)
    comp.font_size_var.set(size)
    comp.bold_var.set(weight == 'bold')
    comp.italic_var.set(slant == 'italic')
    if fg:
        comp.color_var.set(fg)
    comp.color_preview.config(bg=comp.color_var.get())
    comp.align_var.set(just)