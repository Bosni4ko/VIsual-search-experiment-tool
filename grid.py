import tkinter as tk
import random

def setup_field_grid(main_panel, comp):
    """
    Creates (or recreates) a Canvas in `main_panel` that draws:
      • A header text
      • A comp.data['field_y']×comp.data['field_x'] grid of squares, padded + centered
      • A random selection of those squares filled in according to
        comp.data['stimulus_size_mode'], fixed_amount, range_start/range_end.
    Binds <Configure> so it auto‐redraws the existing selection on resize,
    and sets comp.redraw_field_grid() to re‐randomize+redraw when your
    stimulus_size settings change.
    """
    # destroy old canvas if there
    if hasattr(comp, '_field_canvas'):
        comp._field_canvas.destroy()

    canvas = tk.Canvas(main_panel, bg="white")
    canvas.pack(fill="both", expand=True)
    comp._field_canvas = canvas

    # store which cells are filled
    comp._colored_positions = []

    def randomize_colors():
        cols = comp.data.get("field_x", 10)
        rows = comp.data.get("field_y", 10)
        total = rows * cols

        mode = comp.data.get("stimulus_size_mode", "random")
        if mode == "random":
            num = random.randint(2, max(2, total))
        elif mode == "fixed":
            amt = comp.data.get("fixed_amount") or 2
            num = max(2, min(amt, total))
        elif mode == "random in range":
            start = comp.data.get("range_start") or 2
            end   = comp.data.get("range_end")   or total
            start = max(2, min(start, total))
            end   = max(start, min(end, total))
            num = random.randint(start, end)
        else:
            num = 2

        # pick that many distinct (r,c)
        positions = [(r,c) for r in range(rows) for c in range(cols)]
        comp._colored_positions = random.sample(positions, min(num, total))

    def draw_grid(event=None):
        # clear previous
        canvas.delete("grid", "colored", "header")

        cols = comp.data.get("field_x", 10)
        rows = comp.data.get("field_y", 10)
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if cols <= 0 or rows <= 0 or w < 2 or h < 2:
            return

        # padding + header
        pad = 10
        header_height = 30
        header_text = "Example of the experiment grid"
        canvas.create_text(
            w/2, pad + header_height/2,
            text=header_text,
            font=("Segoe UI", 12, "bold"),
            tag="header"
        )

        # usable area under header
        usable_w = w - 2*pad
        usable_h = h - pad - header_height - pad
        if usable_w <= 0 or usable_h <= 0:
            return

        size = min(usable_w/cols, usable_h/rows)
        grid_w = size * cols
        grid_h = size * rows

        offset_x = (w - grid_w)/2
        offset_y = pad + header_height

        # 1) draw all outlines
        for r in range(rows):
            for c in range(cols):
                x0 = offset_x + c*size
                y0 = offset_y + r*size
                x1 = x0 + size
                y1 = y0 + size
                canvas.create_rectangle(x0, y0, x1, y1,
                                        outline="black",
                                        tag="grid")

        # 2) fill the randomly selected cells
        for (r, c) in comp._colored_positions:
            x0 = offset_x + c*size
            y0 = offset_y + r*size
            x1 = x0 + size
            y1 = y0 + size
            canvas.create_rectangle(x0, y0, x1, y1,
                                    fill="lightblue",
                                    outline="black",
                                    tag="colored")

    # auto‐redraw outlines + fills (same selection) on resize
    canvas.bind("<Configure>", draw_grid)

    # publicly available: randomize + redraw
    def redraw_all():
        randomize_colors()
        draw_grid()
    comp.redraw_field_grid = redraw_all

    # initial population + draw
    main_panel.after(50, redraw_all)

    # redraw on resize
    canvas.bind("<Configure>", draw_grid)

    # allow manual redraw if your data changes
    comp.redraw_field_grid = draw_grid

    # initial draw
    main_panel.after(50, draw_grid)