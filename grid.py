import tkinter as tk
import random

import tkinter as tk
import random

def setup_field_grid(main_panel, comp):
    """
    Creates (or recreates) a Canvas in `main_panel` that draws:
      • A header text
      • A comp.data['field_y']×comp.data['field_x'] grid of squares, padded + centered
      • One target cell (unless comp.data['no_target']) colored by target_type
      • The remaining sampled cells colored by distractor_type
    Binds <Configure> so it auto‐redraws on resize, and exposes
    comp.redraw_field_grid() to re‐randomize + redraw when your
    stimulus_size settings change.
    """
    # Destroy any old canvas
    if hasattr(comp, '_field_canvas'):
        comp._field_canvas.destroy()

    canvas = tk.Canvas(main_panel, bg="white")
    canvas.pack(fill="both", expand=True)
    comp._field_canvas = canvas

    # Will hold our sampled distractor positions
    comp._distractor_positions = []
    # Will hold our single target position (or None)
    comp._target_position = None

    # Color maps
    default_color = {
        "neutral": "grey",
        "positive": "green",
        "negative": "red"
    }
    dark_color = {
        "neutral": "#000000",   # pitch‑black
        "positive": "#004d00",  # very dark green
        "negative": "#660000"   # very dark red
    }

    def randomize_colors():
        cols = comp.data.get("field_x", 10)
        rows = comp.data.get("field_y", 10)
        total = rows * cols

        # 1) Determine how many squares to color
        mode = comp.data.get("stimulus_size_mode", "random")
        if mode == "random":
            count = random.randint(2, total)
        elif mode == "fixed":
            amt = comp.data.get("fixed_amount", 2) or 2
            count = max(2, min(amt, total))
        elif mode == "random in range":
            start = comp.data.get("range_start", 2) or 2
            end   = comp.data.get("range_end", total) or total
            start = max(2, min(start, total))
            end   = max(start, min(end, total))
            count = random.randint(start, end)
        else:
            count = 2

        # 2) Sample that many distinct cells
        all_cells = [(r, c) for r in range(rows) for c in range(cols)]
        sampled = random.sample(all_cells, min(count, total))

        # 3) Decide on target vs distractors
        if comp.data.get("no_target", False):
            comp._target_position = None
            comp._distractor_positions = sampled
        else:
            tgt = random.choice(sampled)
            comp._target_position = tgt
            comp._distractor_positions = [cell for cell in sampled if cell != tgt]

    def draw_grid(event=None):
        canvas.delete("grid", "distractor", "target", "header")

        cols = comp.data.get("field_x", 10)
        rows = comp.data.get("field_y", 10)
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if cols < 1 or rows < 1 or w < 2 or h < 2:
            return

        # Header + padding
        pad = 10
        header_h = 30
        canvas.create_text(
            w / 2, pad + header_h / 2,
            text="Example of the experiment grid",
            font=("Segoe UI", 12, "bold"),
            tag="header"
        )

        # Compute grid area
        usable_w = w - 2 * pad
        usable_h = h - pad - header_h - pad
        if usable_w <= 0 or usable_h <= 0:
            return

        size = min(usable_w / cols, usable_h / rows)
        grid_w = size * cols
        grid_h = size * rows
        offset_x = (w - grid_w) / 2
        offset_y = pad + header_h

        # Draw all outlines
        for r in range(rows):
            for c in range(cols):
                x0 = offset_x + c * size
                y0 = offset_y + r * size
                x1 = x0 + size
                y1 = y0 + size
                canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="black",
                    tag="grid"
                )

        # Figure out colors
        dt = comp.data.get("distractor_type", "positive")
        tt = comp.data.get("target_type", "positive")
        distractor_color = default_color.get(dt, "grey")
        if tt == dt:
            target_color = dark_color.get(tt, "black")
        else:
            target_color = default_color.get(tt, "grey")

        # Fill distractors
        for (r, c) in comp._distractor_positions:
            x0 = offset_x + c * size
            y0 = offset_y + r * size
            x1 = x0 + size
            y1 = y0 + size
            canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=distractor_color,
                outline="black",
                tag="distractor"
            )

        # Fill the target (if any)
        if comp._target_position:
            r, c = comp._target_position
            x0 = offset_x + c * size
            y0 = offset_y + r * size
            x1 = x0 + size
            y1 = y0 + size
            canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=target_color,
                outline="black",
                tag="target"
            )

    # Bind resize to redraw (keeps same sampled cells)
    canvas.bind("<Configure>", draw_grid)

    # Public method: re‐sample & redraw
    def redraw_all():
        randomize_colors()
        draw_grid()
    comp.redraw_field_grid = redraw_all

    # Kick things off
    main_panel.after(50, redraw_all)
