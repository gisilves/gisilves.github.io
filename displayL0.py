"""
Detector layout JS viewer — Bokeh backend
Script generates html file detector_layout.html
"""

import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CustomJS, Label, Arrow, OpenHead, CheckboxGroup, Button, Div, Select, Spacer
from bokeh.layouts import row, column
from bokeh.io import output_file, save
    
# ---------------------------------------------------------------------------
# Detector configurations
# ---------------------------------------------------------------------------

BASE_CFG = dict(
    N_LADDERS     = 9,
    CELL_WIDTH    = 113.0,
    CELL_HEIGHT   = 80.0,
    LADDER_GAP    = 0.2,
    SI_GAP        = 0.15,
    CROSS_OFFSET_X        = 0.235,
    CROSS_OFFSET_Y        = 0.235,
    ACTIVE_AREA_OFFSET_X  = 0.235 + 0.470625,
    ACTIVE_AREA_OFFSET_Y  = 0.235 + 0.345,
    CROSS_ARM_X   = 0.05,
    CROSS_ARM_Y   = 0.05,
    SI_PER_LADDER = [12, 12, 12, 12, 12, 10, 10, 8, 8],
    GLOBAL_X_OFFSET = 0.1,
    GLOBAL_Y_OFFSET = 0.1,
    LADDER_Y_OFFSET = [5, 0, 0, 0, 0, 0, 0, 0, 0],
    CENTER_GAP_X  = 0.0,
    CENTER_GAP_Y  = 0.0,
    ZOOM_MARGIN   = 5.0,
    ROTATION_DEG  = 0.0,
)

CFG_U = {
    **BASE_CFG,
    "TITLE": "AMS-L0 U Detector Layout (seen from above AMS looking down)",
    "ROTATION_DEG": 45.0,
    "LADDER_LABELS": {
        "QL-L3": [["L12-30", "L12-26", "L12-09", "L12-42", "L12-05", "L10-13", "L10-05", "L08-08", "L08-07"], 1,  -1],
        "QL-R2": [["L12-04", "L12-10", "L12-34", "L12-02", "L12-47", "L10-08", "L10-06", "L08-15", "L08-04"], -1, -1],
        "QL-L1": [["L12-36", "L12-38", "L12-43", "L12-35", "L12-19", "L10-10", "L10-07", "L08-06", "L08-02"], -1,  1],
        "QL-R1": [["L12-37", "L12-40", "L12-39", "L12-21", "L12-20", "L10-16", "L10-11", "L08-12", "L08-11"],  1,  1],
    },
    "LEF_LABELS": {
        "QL-L3": ["LEF-1-1", "LEF-1-2", "LEF-1-3", "LEF-1-4", "LEF-1-5", "LEF-1-6", "LEF-1-7", "LEF-1-8", "LEF-1-9"],
        "QL-R2": ["LEF-3-1", "LEF-3-2", "LEF-3-3", "LEF-3-4", "LEF-3-5", "LEF-3-6", "LEF-3-7", "LEF-3-8", "LEF-3-9"],
        "QL-L1": ["LEF-5-1", "LEF-5-2", "LEF-5-3", "LEF-5-4", "LEF-5-5", "LEF-5-6", "LEF-5-7", "LEF-5-8", "LEF-5-9"],
        "QL-R1": ["LEF-7-1", "LEF-7-2", "LEF-7-3", "LEF-7-4", "LEF-7-5", "LEF-7-6", "LEF-7-7", "LEF-7-8", "LEF-7-9"],
    },
}

CFG_Y = {
    **BASE_CFG,
    "TITLE": "AMS-L0 Y Detector Layout (seen from above AMS looking down)",
    "ROTATION_DEG": 0.0,
    "LADDER_LABELS": {
        "QL-R3": [["L12-16", "L12-03", "L12-29", "L12-46", "L12-45", "L10-18", "L10-17", "L08-05", "L08-18"],  1, -1],
        "QL-L2": [["L12-41", "L12-14", "L12-24", "L12-18", "L12-06", "L10-03", "L10-14", "L08-10", "L08-13"], -1, -1],
        "QL-R4": [["L12-01", "L12-28", "L12-08", "L12-11", "L12-25", "L10-15", "L10-02", "L08-17", "L08-14"], -1,  1],
        "QL-L4": [["L12-33", "L12-12", "L12-31", "L12-15", "L12-17", "L10-12", "L10-04", "L08-09", "L08-16"],  1,  1],
    },
    "LEF_LABELS": {
        "QL-R3": ["LEF-2-1", "LEF-2-2", "LEF-2-3", "LEF-2-4", "LEF-2-5", "LEF-2-6", "LEF-2-7", "LEF-2-8", "LEF-2-9"],
        "QL-L2": ["LEF-4-1", "LEF-4-2", "LEF-4-3", "LEF-4-4", "LEF-4-5", "LEF-4-6", "LEF-4-7", "LEF-4-8", "LEF-4-9"],
        "QL-R4": ["LEF-6-1", "LEF-6-2", "LEF-6-3", "LEF-6-4", "LEF-6-5", "LEF-6-6", "LEF-6-7", "LEF-6-8", "LEF-6-9"],
        "QL-L4": ["LEF-8-1", "LEF-8-2", "LEF-8-3", "LEF-8-4", "LEF-8-5", "LEF-8-6", "LEF-8-7", "LEF-8-8", "LEF-8-9"],
    },
}

COLOR_NORMAL      = "#a048c8"
COLOR_ACTIVE      = "#a0a8c8"
COLOR_HIGHLIGHT   = "#44cc44"
COLOR_EDGE        = "#222244"
COLOR_ACTIVE_EDGE = "#441144"
COLOR_CROSS       = "#cc2222"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def import_csv(filename):
    points = []
    with open(filename) as f:
        for line in f:
            points.append(tuple(map(float, line.split(','))))
    return points


def _safe_hits_str(hits):
    """Convert a hits value (set or 'NO LEF' string) to a clean comma-separated string."""
    if isinstance(hits, set):
        cleaned = ", ".join(sorted(h for h in hits if h))
        return cleaned if cleaned else "NO LEF"
    # already a string (e.g. "NO LEF")
    return hits if hits else "NO LEF"


def get_tiles_in_radius(p_x, p_y, radius, die_source):
    hits = []
    data = die_source.data
    r_sq = radius ** 2

    for i in range(len(data['x'])):
        corners = [
            (data['x_bl'][i], data['y_bl'][i]),
            (data['x_br'][i], data['y_br'][i]),
            (data['x_tr'][i], data['y_tr'][i]),
            (data['x_tl'][i], data['y_tl'][i]),
        ]

        # Point-in-polygon
        inside = False
        k = len(corners) - 1
        for j in range(len(corners)):
            if ((corners[j][1] > p_y) != (corners[k][1] > p_y)) and \
               (p_x < (corners[k][0] - corners[j][0]) * (p_y - corners[j][1]) /
               (corners[k][1] - corners[j][1]) + corners[j][0]):
                inside = not inside
            k = j
        if inside:
            hits.append(data['lef'][i])
            continue

        # Edge distance
        hit_edge = False
        for m in range(len(corners)):
            p1 = corners[m]
            p2 = corners[(m + 1) % len(corners)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            mag_sq = dx * dx + dy * dy
            if mag_sq == 0:
                continue
            t = max(0, min(1, ((p_x - p1[0]) * dx + (p_y - p1[1]) * dy) / mag_sq))
            dist_sq = (p_x - p1[0] - t * dx) ** 2 + (p_y - p1[1] - t * dy) ** 2
            if dist_sq <= r_sq:
                hit_edge = True
                break
        if hit_edge:
            hits.append(data['lef'][i])

    return set(hits)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_detector_panel(cfg, width=850, height=850, points_file=None, cupola_points_file=None):

    N_LADDERS            = cfg["N_LADDERS"]
    CELL_WIDTH           = cfg["CELL_WIDTH"]
    CELL_HEIGHT          = cfg["CELL_HEIGHT"]
    LADDER_GAP           = cfg["LADDER_GAP"]
    SI_GAP               = cfg["SI_GAP"]
    CROSS_OFFSET_X       = cfg["CROSS_OFFSET_X"]
    CROSS_OFFSET_Y       = cfg["CROSS_OFFSET_Y"]
    ACTIVE_AREA_OFFSET_X = cfg["ACTIVE_AREA_OFFSET_X"]
    ACTIVE_AREA_OFFSET_Y = cfg["ACTIVE_AREA_OFFSET_Y"]
    CROSS_ARM_X          = cfg["CROSS_ARM_X"]
    CROSS_ARM_Y          = cfg["CROSS_ARM_Y"]
    SI_PER_LADDER        = cfg["SI_PER_LADDER"]
    GLOBAL_X_OFFSET      = cfg["GLOBAL_X_OFFSET"]
    GLOBAL_Y_OFFSET      = cfg["GLOBAL_Y_OFFSET"]
    LADDER_Y_OFFSET      = cfg["LADDER_Y_OFFSET"]
    CENTER_GAP_X         = cfg["CENTER_GAP_X"]
    CENTER_GAP_Y         = cfg["CENTER_GAP_Y"]
    ZOOM_MARGIN          = cfg["ZOOM_MARGIN"]
    ROTATION_DEG         = cfg.get("ROTATION_DEG", 0.0)
    TITLE                = cfg["TITLE"]

    QL_LIST       = [(k, v[1], v[2]) for k, v in cfg["LADDER_LABELS"].items()]
    LADDER_LABELS = {k: v[0]         for k, v in cfg["LADDER_LABELS"].items()}
    LEF_LABELS    = cfg["LEF_LABELS"]

    ACTIVE_WIDTH  = CELL_WIDTH  - 2 * ACTIVE_AREA_OFFSET_X
    ACTIVE_HEIGHT = CELL_HEIGHT - 2 * ACTIVE_AREA_OFFSET_Y

    CROSS_POSITIONS_LOCAL = [
        (CROSS_OFFSET_X,              CROSS_OFFSET_Y),
        (CELL_WIDTH - CROSS_OFFSET_X, CROSS_OFFSET_Y),
        (CELL_WIDTH - CROSS_OFFSET_X, CELL_HEIGHT - CROSS_OFFSET_Y),
        (CROSS_OFFSET_X,              CELL_HEIGHT - CROSS_OFFSET_Y),
    ]

    def _expand(param, n):
        if isinstance(param, (int, float)):
            return [param] * n
        return list(param)

    si_per_ladder   = _expand(SI_PER_LADDER,   N_LADDERS)
    ladder_y_offset = _expand(LADDER_Y_OFFSET, N_LADDERS)

    ladder_pitch      = CELL_WIDTH + LADDER_GAP
    si_step           = CELL_HEIGHT + SI_GAP
    col_x_start_local = [GLOBAL_X_OFFSET + col * ladder_pitch for col in range(N_LADDERS)]

    def _col_top_local(col):
        return GLOBAL_Y_OFFSET + ladder_y_offset[col] + si_per_ladder[col] * si_step - SI_GAP

    def _col_left_local(col):
        return col_x_start_local[col]

    q1_cells_local = []
    for col in range(N_LADDERS):
        xc = col_x_start_local[col]
        y0 = GLOBAL_Y_OFFSET + ladder_y_offset[col]
        for row_idx in range(si_per_ladder[col]):
            q1_cells_local.append((col, row_idx, xc, y0 + row_idx * si_step))

    CX = CENTER_GAP_X / 2
    CY = CENTER_GAP_Y / 2

    def transform(x_local, y_local, flip_x, flip_y):
        xg = (CX + x_local)         if flip_x == 1 else (-CX - (x_local + CELL_WIDTH))
        yg = (CY + y_local)         if flip_y == 1 else (-CY - (y_local + CELL_HEIGHT))
        return xg, yg

    _cos = np.cos(np.radians(ROTATION_DEG))
    _sin = np.sin(np.radians(ROTATION_DEG))

    def rotate(x, y, deg):
        c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
        return x * c - y * s, x * s + y * c

    # ---- Silicon die data ----
    die_data = {k: [] for k in [
        "x", "y", "w", "h", "xs", "ys", "qname", "lef", "col", "row", "label", "si_idx",
        "x_bl", "y_bl", "x_br", "y_br", "x_tr", "y_tr", "x_tl", "y_tl",
        "ax_bl_x", "ax_bl_y", "ax_br_x", "ax_br_y",
        "ax_tr_x", "ax_tr_y", "ax_tl_x", "ax_tl_y",
        "die_cx", "die_cy",
        "bbox_xmin", "bbox_xmax", "bbox_ymin", "bbox_ymax",
    ]}

    # Load points files
    points = []
    cupola_points = []
    if points_file is not None:
        points = import_csv(points_file)
        if cupola_points_file is not None:
            cupola_points = import_csv(cupola_points_file)

    # Correct for different robotic arms coordinate system
    if "AMS-L0 U Detector Layout" in cfg["TITLE"]:
        points        = [(-p[0],  p[1]) for p in points]
        cupola_points = [(-p[0],  p[1]) for p in cupola_points]
        
    # Note: for Y layer, combination of coordinate system correction and mirroring 
    # (Y layer seen from above AMS looking down)
    # gives points with the same coordinates as the ones in the csv file

    for (qname, fx, fy) in QL_LIST:
        for (col, row_idx, xl, yl) in q1_cells_local:
            xg, yg = transform(xl, yl, fx, fy)

            x_bl, y_bl = rotate(xg,             yg,             ROTATION_DEG)
            x_br, y_br = rotate(xg + CELL_WIDTH, yg,             ROTATION_DEG)
            x_tr, y_tr = rotate(xg + CELL_WIDTH, yg + CELL_HEIGHT, ROTATION_DEG)
            x_tl, y_tl = rotate(xg,             yg + CELL_HEIGHT, ROTATION_DEG)
            cx = (x_bl + x_br + x_tr + x_tl) / 4
            cy = (y_bl + y_br + y_tr + y_tl) / 4

            ax_bl_x_r, ax_bl_y_r = rotate(xg + ACTIVE_AREA_OFFSET_X,               yg + ACTIVE_AREA_OFFSET_Y,                ROTATION_DEG)
            ax_br_x_r, ax_br_y_r = rotate(xg + ACTIVE_AREA_OFFSET_X + ACTIVE_WIDTH, yg + ACTIVE_AREA_OFFSET_Y,                ROTATION_DEG)
            ax_tr_x_r, ax_tr_y_r = rotate(xg + ACTIVE_AREA_OFFSET_X + ACTIVE_WIDTH, yg + ACTIVE_AREA_OFFSET_Y + ACTIVE_HEIGHT, ROTATION_DEG)
            ax_tl_x_r, ax_tl_y_r = rotate(xg + ACTIVE_AREA_OFFSET_X,               yg + ACTIVE_AREA_OFFSET_Y + ACTIVE_HEIGHT, ROTATION_DEG)

            lbl     = LADDER_LABELS[qname][col]
            lbl_lef = LEF_LABELS[qname][col]
            si_idx  = si_per_ladder[col] - row_idx - 1

            die_data["xs"].append([x_bl, x_br, x_tr, x_tl])
            die_data["ys"].append([y_bl, y_br, y_tr, y_tl])
            die_data["x"].append(cx);             die_data["y"].append(cy)
            die_data["w"].append(CELL_WIDTH);      die_data["h"].append(CELL_HEIGHT)
            die_data["qname"].append(qname)
            die_data["lef"].append(lbl_lef)
            die_data["col"].append(col);           die_data["row"].append(row_idx)
            die_data["label"].append(lbl);         die_data["si_idx"].append(si_idx)
            die_data["x_bl"].append(x_bl);         die_data["y_bl"].append(y_bl)
            die_data["x_br"].append(x_br);         die_data["y_br"].append(y_br)
            die_data["x_tr"].append(x_tr);         die_data["y_tr"].append(y_tr)
            die_data["x_tl"].append(x_tl);         die_data["y_tl"].append(y_tl)
            die_data["ax_bl_x"].append(ax_bl_x_r); die_data["ax_bl_y"].append(ax_bl_y_r)
            die_data["ax_br_x"].append(ax_br_x_r); die_data["ax_br_y"].append(ax_br_y_r)
            die_data["ax_tr_x"].append(ax_tr_x_r); die_data["ax_tr_y"].append(ax_tr_y_r)
            die_data["ax_tl_x"].append(ax_tl_x_r); die_data["ax_tl_y"].append(ax_tl_y_r)
            die_data["die_cx"].append(cx);         die_data["die_cy"].append(cy)
            all_cx = [x_bl, x_br, x_tr, x_tl]
            all_cy = [y_bl, y_br, y_tr, y_tl]
            die_data["bbox_xmin"].append(min(all_cx))
            die_data["bbox_xmax"].append(max(all_cx))
            die_data["bbox_ymin"].append(min(all_cy))
            die_data["bbox_ymax"].append(max(all_cy))

    die_source = ColumnDataSource(die_data)

    # ---- Save nominal positions CSV ----
    with open(f"{cfg['TITLE'][7]}_nominal_positions.csv", "w") as f:
        print(f"Writing nominal positions to {f.name}")
        f.write("Layer,qname,Si detector,LEF,"
                "Die BL x,Die BL y,Die BR x,Die BR y,Die TR x,Die TR y,Die TL x,Die TL y,"
                "Active BL x,Active BL y,Active BR x,Active BR y,"
                "Active TR x,Active TR y,Active TL x,Active TL y\n")
        for i in range(len(die_data["qname"])):
            si_det = f"{die_data['label'][i]}-{die_data['si_idx'][i]}"
            f.write(
                f"{cfg['TITLE'][7]},{die_data['qname'][i]},{si_det},{die_data['lef'][i]},"
                f"{die_data['x_bl'][i]},{die_data['y_bl'][i]},"
                f"{die_data['x_br'][i]},{die_data['y_br'][i]},"
                f"{die_data['x_tr'][i]},{die_data['y_tr'][i]},"
                f"{die_data['x_tl'][i]},{die_data['y_tl'][i]},"
                f"{die_data['ax_bl_x'][i]},{die_data['ax_bl_y'][i]},"
                f"{die_data['ax_br_x'][i]},{die_data['ax_br_y'][i]},"
                f"{die_data['ax_tr_x'][i]},{die_data['ax_tr_y'][i]},"
                f"{die_data['ax_tl_x'][i]},{die_data['ax_tl_y'][i]}\n"
            )

    # ---- Compute TB hits ----
    TB_hits        = []   # list of [layer, idx, hits_set_or_str]
    TB_hits_cupola = []

    if points_file is not None:
        hits_file = f"{cfg['TITLE'][7]}_TB_hits.csv"
        print(f"Writing hits to {hits_file}")
        with open(hits_file, "w") as f:
            f.write("Layer,TB point,Hits\n")
            for idx, (ptx, pty) in enumerate(points, start=1):
                hits = get_tiles_in_radius(ptx, pty, 10, die_source)
                hits_str = _safe_hits_str(hits)
                f.write(f"{cfg['TITLE'][7]},{idx},{hits_str}\n")
                TB_hits.append([cfg['TITLE'][7], idx, hits])   # store set

        if cupola_points_file is not None:
            hits_file = f"{cfg['TITLE'][7]}_Cupola_TB_hits.csv"
            print(f"Writing hits to {hits_file}")
            with open(hits_file, "w") as f:
                f.write("Layer,TB point,Hits\n")
                for idx, (ptx, pty) in enumerate(cupola_points, start=1):
                    hits = get_tiles_in_radius(ptx, pty, 10, die_source)
                    hits_str = _safe_hits_str(hits)
                    f.write(f"{cfg['TITLE'][7]},{idx},{hits_str}\n")
                    TB_hits_cupola.append([cfg['TITLE'][7], idx, hits])   # store set

    # ---- Active area ----
    active_data = dict(xs=[], ys=[])
    for (qname, fx, fy) in QL_LIST:
        for (col, row_idx, xl, yl) in q1_cells_local:
            xg, yg = transform(xl, yl, fx, fy)
            corners = [
                rotate(xg + ACTIVE_AREA_OFFSET_X,               yg + ACTIVE_AREA_OFFSET_Y,                ROTATION_DEG),
                rotate(xg + ACTIVE_AREA_OFFSET_X + ACTIVE_WIDTH, yg + ACTIVE_AREA_OFFSET_Y,                ROTATION_DEG),
                rotate(xg + ACTIVE_AREA_OFFSET_X + ACTIVE_WIDTH, yg + ACTIVE_AREA_OFFSET_Y + ACTIVE_HEIGHT, ROTATION_DEG),
                rotate(xg + ACTIVE_AREA_OFFSET_X,               yg + ACTIVE_AREA_OFFSET_Y + ACTIVE_HEIGHT, ROTATION_DEG),
            ]
            active_data["xs"].append([c[0] for c in corners])
            active_data["ys"].append([c[1] for c in corners])
    active_source = ColumnDataSource(active_data)

    # ---- Ladder label boxes ----
    LABEL_HEIGHT = si_step
    LABEL_PAD_Y  = 1.0

    def label_box_global(col, flip_x, flip_y):
        xl = _col_left_local(col)
        bx_loc = (CX + xl + 2) if flip_x == 1 else (-CX - (xl + CELL_WIDTH) + 2)
        top_local = _col_top_local(col)
        by_loc = (CY + top_local + LABEL_PAD_Y) if flip_y == 1 else \
                 (-CY - top_local - LABEL_PAD_Y - LABEL_HEIGHT)
        bw = CELL_WIDTH - 4
        c0 = rotate(bx_loc,      by_loc,              ROTATION_DEG)
        c1 = rotate(bx_loc + bw, by_loc,              ROTATION_DEG)
        c2 = rotate(bx_loc + bw, by_loc + LABEL_HEIGHT, ROTATION_DEG)
        c3 = rotate(bx_loc,      by_loc + LABEL_HEIGHT, ROTATION_DEG)
        xs = [c0[0], c1[0], c2[0], c3[0]]
        ys = [c0[1], c1[1], c2[1], c3[1]]
        return xs, ys, sum(xs) / 4, sum(ys) / 4

    label_box_data = dict(xs=[], ys=[])
    for (qname, fx, fy) in QL_LIST:
        for col in range(N_LADDERS):
            xs, ys, _, _ = label_box_global(col, fx, fy)
            label_box_data["xs"].append(xs)
            label_box_data["ys"].append(ys)
    label_box_source = ColumnDataSource(label_box_data)

    # ---- Crosses ----
    cross_xs, cross_ys = [], []
    for (qname, fx, fy) in QL_LIST:
        for (col, row_idx, xl, yl) in q1_cells_local:
            xg, yg = transform(xl, yl, fx, fy)
            for (dx, dy) in CROSS_POSITIONS_LOCAL:
                ccx, ccy = xg + dx, yg + dy
                ax, ay = rotate(ccx - CROSS_ARM_X, ccy,             ROTATION_DEG)
                bx, by = rotate(ccx + CROSS_ARM_X, ccy,             ROTATION_DEG)
                cross_xs.append([ax, bx]); cross_ys.append([ay, by])
                ax, ay = rotate(ccx,             ccy - CROSS_ARM_Y, ROTATION_DEG)
                bx, by = rotate(ccx,             ccy + CROSS_ARM_Y, ROTATION_DEG)
                cross_xs.append([ax, bx]); cross_ys.append([ay, by])
    cross_source = ColumnDataSource(dict(xs=cross_xs, ys=cross_ys))

    # ---- Quadrant centroid labels ----
    quadrant_labels = []
    for (qname, fx, fy) in QL_LIST:
        xs_q = [die_data["die_cx"][i] for i, qn in enumerate(die_data["qname"]) if qn == qname]
        ys_q = [die_data["die_cy"][i] for i, qn in enumerate(die_data["qname"]) if qn == qname]
        quadrant_labels.append((qname, float(np.mean(xs_q)), float(np.mean(ys_q))))

    # ---- Figure ----
    all_xs_flat = die_data["bbox_xmin"] + die_data["bbox_xmax"]
    all_ys_flat = die_data["bbox_ymin"] + die_data["bbox_ymax"]
    x_pad = 175
    y_pad = 175 + LABEL_PAD_Y + LABEL_HEIGHT

    full_x_start = min(all_xs_flat) - x_pad
    full_x_end   = max(all_xs_flat) + x_pad
    full_y_start = max(all_ys_flat) + y_pad
    full_y_end   = min(all_ys_flat) - y_pad

    p = figure(
        title=TITLE,
        x_axis_label="y [mm]", y_axis_label="x [mm]",
        width=width, height=height,
        x_range=(full_x_start, full_x_end),
        y_range=(full_y_start, full_y_end),
        tools="pan,wheel_zoom,tap,reset",
        active_scroll="wheel_zoom",
        match_aspect=True,
        output_backend="webgl",
    )
    p.toolbar.logo = None

    p.segment(x0=[full_x_start], y0=[0], x1=[full_x_end], y1=[0],
              line_color="#888888", line_dash="dashed", line_width=0.6)
    p.segment(x0=[0], y0=[full_y_start], x1=[0], y1=[full_y_end],
              line_color="#888888", line_dash="dashed", line_width=0.6)

    die_glyph = p.patches(xs="xs", ys="ys", source=die_source,
                           fill_color=COLOR_NORMAL, fill_alpha=0.85,
                           line_color=COLOR_EDGE, line_width=0.6)

    p.patches(xs="xs", ys="ys", source=active_source,
              fill_color=COLOR_ACTIVE, fill_alpha=0.85,
              line_color=COLOR_ACTIVE_EDGE, line_width=0.5,
              nonselection_fill_alpha=0.85)

    p.multi_line(xs="xs", ys="ys", source=cross_source,
                 line_color=COLOR_CROSS, line_width=1.5)

    # ---- Ladder label boxes (captured for toggle) ----
    lb_renderer = p.patches(xs="xs", ys="ys", source=label_box_source,
                             fill_color=COLOR_HIGHLIGHT, fill_alpha=1.0,
                             line_color=COLOR_EDGE, line_width=0.8)

    rot_rad = -ROTATION_DEG * np.pi / 180.0

    # ---- "0" marker at first silicon of each ladder (captured for toggle) ----
    strip_renderers = []
    for (qname, fx, fy) in QL_LIST:
        for col in range(N_LADDERS):
            xl = col_x_start_local[col]
            yl = GLOBAL_Y_OFFSET + ladder_y_offset[col] + (si_per_ladder[col] - 1) * si_step
            xg, yg = transform(xl, yl, fx, fy)
            if cfg["ROTATION_DEG"] == 0:
                if fy == -1:
                    brx, bry = rotate(xg + CELL_WIDTH - 20, yg + 10,              ROTATION_DEG)
                else:
                    brx, bry = rotate(xg + 10,              yg + CELL_HEIGHT - 30, ROTATION_DEG)
            else:
                if fy == -1:
                    brx, bry = rotate(xg + 10,              yg + 10,              ROTATION_DEG)
                else:
                    brx, bry = rotate(xg + CELL_WIDTH - 20, yg + CELL_HEIGHT - 30, ROTATION_DEG)
            r = p.text(x=[brx], y=[bry], text=["0"],
                       angle=rot_rad,
                       text_font_size="7pt", text_font_style="bold",
                       text_color="#ffffff", text_align="left", text_baseline="top")
            strip_renderers.append(r)

    # ---- Ladder label text (captured for toggle, grouped with lb_renderer) ----
    lb_text_renderers = []
    for (qname, fx, fy) in QL_LIST:
        for col in range(N_LADDERS):
            lbl     = LADDER_LABELS[qname][col]
            lbl_lef = LEF_LABELS[qname][col]
            if lbl is None:
                continue
            xs, ys, tcx, tcy = label_box_global(col, fx, fy)
            r = p.text(x=[tcx], y=[tcy], text=[lbl + "\n" + lbl_lef],
                       angle=rot_rad,
                       text_font_size="6pt", text_font_style="bold",
                       text_color="#003300", text_align="center", text_baseline="middle")
            lb_text_renderers.append(r)

    # ---- Quadrant overlay labels (captured for toggle) ----
    ql_overlay_labels = []
    for (qname, qcx, qcy) in quadrant_labels:
        ql_lbl = Label(
            x=qcx, y=qcy, x_units="data", y_units="data",
            text=qname,
            text_font_size="28px", text_font_style="bold",
            text_color="#ffffff", text_align="center", text_baseline="middle",
            background_fill_color="#00000066", background_fill_alpha=0.6,
            border_line_color=None, padding=6, visible=True,
        )
        p.add_layout(ql_lbl)
        ql_overlay_labels.append(ql_lbl)

    # ---- Relative bearing labels ----
    for text, x, y, angle, baseline in [
        ("PORT", width / 2 - 50, 0,           0,      "bottom"),
        ("STBD", width / 2 - 50, height - 70, 0,      "top"),
        ("WAKE", width - 100,    height/2-30,  1.5708, "bottom"),
        ("RAM",  0,               height/2-30,  1.5708, "top"),
    ]:
        p.add_layout(Label(
            x=x, y=y, x_units="screen", y_units="screen",
            text=text, angle=angle,
            text_font_size="16px", text_font_style="bold",
            text_color="#ffffff", text_align="center", text_baseline=baseline,
            background_fill_color="#00000066", background_fill_alpha=0.6,
            border_line_color=None, padding=6, visible=True,
        ))

    # ---- Name label (zoom overlay) ----
    lbl_name = Label(
        x=0, y=0, x_units="data", y_units="data",
        text="",
        text_font_size="14px", text_font_style="bold",
        text_color="#f0f0f0",
        text_align="center", text_baseline="middle",
        background_fill_color="#222244", background_fill_alpha=0.9,
        border_line_color="#888888", border_line_alpha=0.7,
        padding=3, visible=False,
    )
    p.add_layout(lbl_name)

    if points_file is None:
        # ---- Si die HoverTool ----
        p.add_tools(HoverTool(renderers=[die_glyph], tooltips=[
            ("Quadrant",    "@qname"),
            ("Si detector", "@label-@si_idx"),
            ("LEF",         "@lef"),
            ("Die BL",      "(@x_bl{0.0000}, @y_bl{0.0000})"),
            ("Die BR",      "(@x_br{0.0000}, @y_br{0.0000})"),
            ("Die TR",      "(@x_tr{0.0000}, @y_tr{0.0000})"),
            ("Die TL",      "(@x_tl{0.0000}, @y_tl{0.0000})"),
            ("Active BL",   "(@ax_bl_x{0.0000}, @ax_bl_y{0.0000})"),
            ("Active BR",   "(@ax_br_x{0.0000}, @ax_br_y{0.0000})"),
            ("Active TR",   "(@ax_tr_x{0.0000}, @ax_tr_y{0.0000})"),
            ("Active TL",   "(@ax_tl_x{0.0000}, @ax_tl_y{0.0000})"),
        ]))

        # ---- Corner zoom labels ----
        NUDGE_PX_AA  = 80
        NUDGE_PX_DIE = 50
        zoom_label_cfg = [
            ("left",  "bottom", ( 1, -1), NUDGE_PX_AA,  "#ffffffdd"),
            ("right", "bottom", (-1, -1), NUDGE_PX_AA,  "#ffffffdd"),
            ("right", "top",    (-1,  1), NUDGE_PX_AA,  "#ffffffdd"),
            ("left",  "top",    ( 1,  1), NUDGE_PX_AA,  "#ffffffdd"),
            ("left",  "bottom", ( 1, -1), NUDGE_PX_DIE, "#dd5100dd"),
            ("right", "bottom", (-1, -1), NUDGE_PX_DIE, "#dd5100dd"),
            ("right", "top",    (-1,  1), NUDGE_PX_DIE, "#dd5100dd"),
            ("left",  "top",    ( 1,  1), NUDGE_PX_DIE, "#dd5100dd"),
        ]
        corner_labels = []
        for align, baseline, nudge_dir, px, bg in zoom_label_cfg:
            ox = nudge_dir[0] * px * (_cos if ROTATION_DEG != 0 else 1)
            oy = nudge_dir[1] * px * (_sin if ROTATION_DEG != 0 else 1)
            lbl_obj = Label(
                x=0, y=0, x_units="data", y_units="data",
                x_offset=ox, y_offset=oy, text="",
                text_font_size="11px", text_color="#111111",
                text_align=align, text_baseline=baseline,
                background_fill_color=bg, background_fill_alpha=0.9,
                border_line_color="#888888", border_line_alpha=0.7,
                padding=3, visible=False,
            )
            p.add_layout(lbl_obj)
            corner_labels.append(lbl_obj)

        zoom_labels = [lbl_name] + corner_labels

        tap_cb = CustomJS(args=dict(
            source=die_source,
            x_range=p.x_range, y_range=p.y_range,
            full_x_start=full_x_start, full_x_end=full_x_end,
            full_y_start=full_y_start, full_y_end=full_y_end,
            margin=ZOOM_MARGIN,
            lbl_name=zoom_labels[0],
            lbl_bl=zoom_labels[1],     lbl_br=zoom_labels[2],
            lbl_tr=zoom_labels[3],     lbl_tl=zoom_labels[4],
            lbl_die_bl=zoom_labels[5], lbl_die_br=zoom_labels[6],
            lbl_die_tr=zoom_labels[7], lbl_die_tl=zoom_labels[8],
            ql_labels=ql_overlay_labels,
        ), code="""
            function fmt(v) { return v.toFixed(4); }
            function coord(x, y) { return "(" + fmt(x) + ", " + fmt(y) + ")"; }
            const zoom_lbls = [lbl_name, lbl_bl, lbl_br, lbl_tr, lbl_tl,
                               lbl_die_bl, lbl_die_br, lbl_die_tr, lbl_die_tl];
            const inds = source.selected.indices;
            if (inds.length === 0) {
                x_range.start = full_x_start; x_range.end = full_x_end;
                y_range.start = full_y_start; y_range.end = full_y_end;
                zoom_lbls.forEach(l => l.visible = false);
                ql_labels.forEach(l => l.visible = true);
                return;
            }
            ql_labels.forEach(l => l.visible = false);
            const i = inds[0];
            const d = source.data;
            const cx = d['die_cx'][i], cy = d['die_cy'][i];
            x_range.start = d['bbox_xmin'][i] - margin; x_range.end = d['bbox_xmax'][i] + margin;
            y_range.start = d['bbox_ymax'][i] + margin; y_range.end = d['bbox_ymin'][i] - margin;
            lbl_name.x = cx; lbl_name.y = cy;
            lbl_name.text = d['qname'][i] + "  " + d['label'][i] + "-" + d['si_idx'][i] + " " + d['lef'][i];
            lbl_name.visible = true;
            const corners = [
                [lbl_bl,     'ax_bl_x','ax_bl_y'],
                [lbl_br,     'ax_br_x','ax_br_y'],
                [lbl_tr,     'ax_tr_x','ax_tr_y'],
                [lbl_tl,     'ax_tl_x','ax_tl_y'],
                [lbl_die_bl, 'x_bl',   'y_bl'   ],
                [lbl_die_br, 'x_br',   'y_br'   ],
                [lbl_die_tr, 'x_tr',   'y_tr'   ],
                [lbl_die_tl, 'x_tl',   'y_tl'   ],
            ];
            for (const [lbl, kx, ky] of corners) {
                lbl.x = d[kx][i]; lbl.y = d[ky][i];
                lbl.text = coord(d[kx][i], d[ky][i]);
                lbl.visible = true;
            }
        """)

    else:
        tap_cb = CustomJS(args=dict(
            source=die_source,
            x_range=p.x_range, y_range=p.y_range,
            full_x_start=full_x_start, full_x_end=full_x_end,
            full_y_start=full_y_start, full_y_end=full_y_end,
            margin=ZOOM_MARGIN,
            lbl_name=lbl_name,
            ql_labels=ql_overlay_labels,
        ), code="""
            const inds = source.selected.indices;
            if (inds.length === 0) {
                x_range.start = full_x_start; x_range.end = full_x_end;
                y_range.start = full_y_start; y_range.end = full_y_end;
                lbl_name.visible = false;
                ql_labels.forEach(l => l.visible = true);
                return;
            }
            ql_labels.forEach(l => l.visible = false);
            const i = inds[0];
            const d = source.data;
            x_range.start = d['bbox_xmin'][i] - margin; x_range.end = d['bbox_xmax'][i] + margin;
            y_range.start = d['bbox_ymax'][i] + margin; y_range.end = d['bbox_ymin'][i] - margin;
            lbl_name.x = d['die_cx'][i]; lbl_name.y = d['die_cy'][i];
            lbl_name.text = d['qname'][i] + "  " + d['label'][i] + "-" + d['si_idx'][i] + " " + d['lef'][i];
            lbl_name.visible = true;
        """)

    die_source.selected.js_on_change("indices", tap_cb)

    # ---- Axis arrows (captured for toggle) ----
    SCREEN_ORIGIN_X = 20
    SCREEN_ORIGIN_Y = 100
    SCREEN_LENGTH   = 50

    arr_x = Arrow(x_start=SCREEN_ORIGIN_X, y_start=SCREEN_ORIGIN_Y,
                  x_end=SCREEN_ORIGIN_X + SCREEN_LENGTH, y_end=SCREEN_ORIGIN_Y,
                  start_units='screen', end_units='screen',
                  end=OpenHead(size=10, line_color="#ff0000"),
                  line_color="#ff0000", line_width=3, level='overlay')
    arr_y = Arrow(x_start=SCREEN_ORIGIN_X, y_start=SCREEN_ORIGIN_Y,
                  x_end=SCREEN_ORIGIN_X, y_end=SCREEN_ORIGIN_Y - SCREEN_LENGTH,
                  start_units='screen', end_units='screen',
                  end=OpenHead(size=10, line_color="#ff0000"),
                  line_color="#ff0000", line_width=3, level='overlay')
    txt_x = Label(x=SCREEN_ORIGIN_X + SCREEN_LENGTH + 5, y=SCREEN_ORIGIN_Y,
                  x_units='screen', y_units='screen',
                  text="Y", text_font_size="10pt", text_color="#ff0000",
                  text_baseline="middle")
    txt_y = Label(x=SCREEN_ORIGIN_X, y=SCREEN_ORIGIN_Y - SCREEN_LENGTH - 15,
                  x_units='screen', y_units='screen',
                  text="X", text_font_size="10pt", text_color="#ff0000",
                  text_align="center")
    p.add_layout(arr_x); p.add_layout(arr_y)
    p.add_layout(txt_x); p.add_layout(txt_y)
    axis_renderers = [arr_x, arr_y, txt_x, txt_y]

    # ---- Helper: build a points overlay ----
    def _make_points_overlay(pts_list, hits_list_raw, fill_color, hover_label):
        """Returns (renderers_list, idx_list, hits_str_list)."""
        if not pts_list:
            return [], [], []

        px_list  = [r[0] for r in pts_list]
        py_list  = [r[1] for r in pts_list]
        idx_list = [str(i) for i in range(1, len(pts_list) + 1)]

        # hits_list_raw: list of [layer, idx, set_or_str]
        hits_by_idx = {entry[1]: entry[2] for entry in hits_list_raw}
        hits_str_list = [
            _safe_hits_str(hits_by_idx.get(i, set()))
            for i in range(1, len(pts_list) + 1)
        ]

        src = ColumnDataSource(dict(
            x=px_list, y=py_list,
            idx=idx_list,
            hits=hits_str_list,
        ))

        r_scatter = p.scatter(x="x", y="y", source=src,
                              marker="circle", size=8,
                              fill_color=fill_color, fill_alpha=0.9,
                              line_color="#333300", line_width=1,
                              visible=False)
        r_small = p.text(x="x", y="y", text="idx", source=src,
                         text_font_size="8pt", text_font_style="bold",
                         text_color="#000000",
                         text_align="left", text_baseline="bottom",
                         x_offset=5, y_offset=5, visible=False)
        r_large = p.text(x="x", y="y", text="idx", source=src,
                         text_font_size="18pt", text_font_style="bold",
                         text_color="#000000",
                         text_align="left", text_baseline="bottom",
                         x_offset=5, y_offset=5, visible=False)

        zoom_cb = CustomJS(args=dict(
            x_range=p.x_range, small=r_small, large=r_large,
            full_width=full_x_end - full_x_start,
        ), code="""
            const zoomed_in = Math.abs(x_range.end - x_range.start) < full_width * 0.3;
            if (small.visible || large.visible) {
                small.visible = !zoomed_in;
                large.visible =  zoomed_in;
            }
        """)
        p.x_range.js_on_change("start", zoom_cb)

        p.add_tools(HoverTool(renderers=[r_scatter], tooltips=[
            (hover_label, "@idx"),
            ("Hits",      "@hits"),
        ]))

        return [r_scatter, r_small, r_large], idx_list, hits_str_list

    # ---- TB Points overlay ----
    points_renderers, tb_idx_list, tb_hits_str_list = \
        _make_points_overlay(points, TB_hits, "#ffff00", "TB Point")

    # ---- Cupola TB Points overlay ----
    cupola_points_renderers, cupola_idx_list, cupola_hits_str_list = \
        _make_points_overlay(cupola_points, TB_hits_cupola, "#ff5500", "Cupola TB Point")

    # ---- Toggle groups ----
    toggle_groups = {
        "QL labels":        ql_overlay_labels,
        "LEF boxes":        [lb_renderer] + lb_text_renderers,
        "0 strip markers":  strip_renderers,
        "Axis arrows":      axis_renderers,
        "TB Points":        points_renderers,
        "Cupola TB Points": cupola_points_renderers,
    }

    return (p, toggle_groups,
            cupola_idx_list, cupola_hits_str_list,
            tb_idx_list,     tb_hits_str_list)


# ---------------------------------------------------------------------------
# Widget factories
# ---------------------------------------------------------------------------

def make_points_dropdown(idx_list, hits_list, width=400, title="Select TB Point", label="TB Point"):
    if not idx_list:
        return None, None

    options = [("", title)] + [(idx, f"{label} {idx}") for idx in idx_list]

    select = Select(value="", options=options, width=width)

    hits_div = Div(
        text=f"<i>Select a {label} to see LEF hits</i>",
        width=width,
        styles={"padding": "6px", "border": "1px solid #cccccc",
                "border-radius": "4px", "background": "#f9f9f9",
                "font-size": "13px"},
    )

    hits_map = {idx: hits for idx, hits in zip(idx_list, hits_list)}

    cb = CustomJS(args=dict(div=hits_div, hits_map=hits_map, label=label), code="""
        const idx = cb_obj.value;
        if (!idx) { div.text = "<i>Select a " + label + " to see LEF hits</i>"; return; }
        const hits = hits_map[idx] || "NO LEF";
        div.text = "<b>" + label + " " + idx + " LEF hits:</b><br>" + hits;
    """)
    select.js_on_change("value", cb)
    return select, hits_div


def make_checkbox(toggle_groups, _is_inline=True):
    labels        = list(toggle_groups.keys())
    all_renderers = list(toggle_groups.values())

    cb = CheckboxGroup(
        labels=labels,
        active=[i for i in range(len(labels))
                if labels[i] not in ("TB Points", "Cupola TB Points")],
        width=750,
        inline=_is_inline,
        align='center',
    )

    tb_idx      = labels.index("TB Points")        if "TB Points"        in labels else -1
    tb_rend     = toggle_groups.get("TB Points",        [])
    tb_scatter  = tb_rend[0] if len(tb_rend) > 0 else None
    tb_small    = tb_rend[1] if len(tb_rend) > 1 else None
    tb_large    = tb_rend[2] if len(tb_rend) > 2 else None

    cup_idx     = labels.index("Cupola TB Points") if "Cupola TB Points" in labels else -1
    cup_rend    = toggle_groups.get("Cupola TB Points", [])
    cup_scatter = cup_rend[0] if len(cup_rend) > 0 else None
    cup_small   = cup_rend[1] if len(cup_rend) > 1 else None
    cup_large   = cup_rend[2] if len(cup_rend) > 2 else None

    cb_callback = CustomJS(
        args=dict(
            cb=cb, groups=all_renderers,
            tb_idx=tb_idx,
            tb_scatter=tb_scatter, tb_small=tb_small, tb_large=tb_large,
            cup_idx=cup_idx,
            cup_scatter=cup_scatter, cup_small=cup_small, cup_large=cup_large,
        ),
        code="""
        for (let g = 0; g < groups.length; g++) {
            const visible = cb.active.includes(g);
            if (g === tb_idx) {
                if (tb_scatter) tb_scatter.visible = visible;
                if (tb_small)   tb_small.visible   = visible;
                if (tb_large)   tb_large.visible   = false;
            } else if (g === cup_idx) {
                if (cup_scatter) cup_scatter.visible = visible;
                if (cup_small)   cup_small.visible   = visible;
                if (cup_large)   cup_large.visible   = false;
            } else {
                for (const r of groups[g]) { r.visible = visible; }
            }
        }
    """)
    cb.js_on_change("active", cb_callback)
    return cb


def make_file_download_button(filename, title):
    btn = Button(label=f"Download {title}", button_type="warning", width=400)
    btn.js_on_click(CustomJS(args=dict(file=filename), code="""
        const a = document.createElement('a');
        a.href = file; a.download = file;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
    """))
    return btn


def make_open_page_button(link, title):
    btn = Button(label=f"Open {title}", button_type="warning", width=400)
    btn.js_on_click(CustomJS(args=dict(file=link), code="window.open(file, '_blank');"))
    return btn


def _inject_favicon(html_file, favicon_tag):
    with open(html_file, 'r+') as f:
        content = f.readlines()
        for i, line in enumerate(content):
            if '</head>' in line:
                content.insert(i, favicon_tag)
                break
        f.seek(0); f.writelines(content); f.truncate()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    favicon_tag = '<link rel="icon" type="image/png" href="favicon.png">'

    # ---- U and Y panels with TB points ----
    p_u_pts, tg_u_pts, cup_idx_u, cup_hits_u, tb_idx_u, tb_hits_u = make_detector_panel(
        CFG_U, width=850, height=850,
        points_file="Targets_U_XYAdjusted.csv",
        cupola_points_file="Targets_U_Cupola_XYAdjusted.csv")

    p_y_pts, tg_y_pts, cup_idx_y, cup_hits_y, tb_idx_y, tb_hits_y = make_detector_panel(
        CFG_Y, width=850, height=850,
        points_file="Targets_Y_XYAdjusted.csv",
        cupola_points_file="Targets_Y_Cupola_XYAdjusted.csv")

    # Dropdowns
    dropdown_tb_u,  hits_div_tb_u  = make_points_dropdown(tb_idx_u,  tb_hits_u,  label="TB Point")
    dropdown_tb_y,  hits_div_tb_y  = make_points_dropdown(tb_idx_y,  tb_hits_y,  label="TB Point")
    dropdown_cup_u, hits_div_cup_u = make_points_dropdown(cup_idx_u, cup_hits_u, title="Select Cupola Point", label="Cupola TB Point")
    dropdown_cup_y, hits_div_cup_y = make_points_dropdown(cup_idx_y, cup_hits_y, title="Select Cupola Point", label="Cupola TB Point")

    btn_file_U        = make_file_download_button("U_TB_hits.csv",        "U hits list with LEF")
    btn_file_cupola_U = make_file_download_button("U_Cupola_TB_hits.csv", "U Cupola hits list with LEF")
    btn_file_Y        = make_file_download_button("Y_TB_hits.csv",        "Y hits list with LEF")
    btn_file_cupola_Y = make_file_download_button("Y_Cupola_TB_hits.csv", "Y Cupola hits list with LEF")

    cb_u_pts = make_checkbox(tg_u_pts, False)
    cb_y_pts = make_checkbox(tg_y_pts, False)

    def build_sidebar(cb, btn1, btn2, dd_tb, div_tb, dd_cup, div_cup):
        children = [cb, btn1, btn2, Spacer(width=400, height=10)]
        if dd_tb:
            children += [dd_tb, div_tb]
        if dd_cup:
            children += [Spacer(width=400, height=10), dd_cup, div_cup]
        return column(*children)

    sidebar_u = build_sidebar(cb_u_pts, btn_file_U, btn_file_cupola_U,
                               dropdown_tb_u, hits_div_tb_u,
                               dropdown_cup_u, hits_div_cup_u)
    sidebar_y = build_sidebar(cb_y_pts, btn_file_Y, btn_file_cupola_Y,
                               dropdown_tb_y, hits_div_tb_y,
                               dropdown_cup_y, hits_div_cup_y)

    output_file("AMS_L0_detector_layout_U.html", title="AMS-L0 Detector Layout U")
    save(row(p_u_pts, sidebar_u))
    _inject_favicon("AMS_L0_detector_layout_U.html", favicon_tag)

    output_file("AMS_L0_detector_layout_Y.html", title="AMS-L0 Detector Layout Y")
    save(row(p_y_pts, sidebar_y))
    _inject_favicon("AMS_L0_detector_layout_Y.html", favicon_tag)

    # ---- Main overview panel (no TB points) ----
    p_u, tg_u, _, _, _, _ = make_detector_panel(CFG_U, width=850, height=850)
    p_y, tg_y, _, _, _, _ = make_detector_panel(CFG_Y, width=850, height=850)

    tg_u.pop("TB Points"); tg_u.pop("Cupola TB Points")
    tg_y.pop("TB Points"); tg_y.pop("Cupola TB Points")

    cb_u = make_checkbox(tg_u)
    cb_y = make_checkbox(tg_y)

    btn_open_U         = make_open_page_button("AMS_L0_detector_layout_U.html", "AMS-L0 Detector Layout U")
    btn_open_positions_U = make_file_download_button("U_nominal_positions.csv", "Nominal positions U")
    btn_open_Y         = make_open_page_button("AMS_L0_detector_layout_Y.html", "AMS-L0 Detector Layout Y")
    btn_open_positions_Y = make_file_download_button("Y_nominal_positions.csv", "Nominal positions Y")

    def centered_under(plot, *widgets):
        rows = []
        for w in widgets:
            if hasattr(w, 'width') and w.width is not None:
                w_width = w.width
            elif hasattr(w, 'children'):
                w_width = sum(b.width for b in w.children
                              if hasattr(b, 'width') and b.width is not None)
            else:
                w_width = 0
            pad = max(0, (plot.width - w_width) // 2)
            rows.append(row(Spacer(width=pad), w))
        return column(plot, *rows)

    output_file("AMS_L0_detector_layout.html", title="AMS-L0 Detector Layout")
    save(row(
        centered_under(p_u, cb_u, row(btn_open_U, btn_open_positions_U)),
        centered_under(p_y, cb_y, row(btn_open_Y, btn_open_positions_Y)),
    ))
    _inject_favicon("AMS_L0_detector_layout.html", favicon_tag)