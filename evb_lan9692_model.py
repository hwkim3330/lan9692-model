#!/usr/bin/env python3
"""
EVB-LAN9692-LM 3D Board Model Generator v4 (High Quality)
Detailed and realistic model based on Hardware User's Guide (DS50003848B)
Board: 214 x 150 mm, 4-layer PCB, 1.535mm thick

Improvements in v4:
- Red standoff spacers at mounting holes
- PCB edge layer stack (FR4 laminate visible)
- Much denser passive components
- PCB vias (copper dots)
- Copper pour/ground plane areas
- More small support ICs
- QSPI Flash Program Header
- Temperature sensor header
- Better silkscreen detail
- Board corner chamfers
"""

import trimesh
import numpy as np
from trimesh.creation import box, cylinder


# ── Color Palette ──
C_PCB_TOP     = [0, 85, 30, 255]       # Dark green solder mask
C_PCB_SIDE    = [180, 170, 120, 255]   # FR4 fiberglass edge (tan/khaki)
C_PCB_BOTTOM  = [0, 78, 28, 255]
C_COPPER      = [180, 155, 80, 255]    # Exposed copper/ENIG gold
C_COPPER_DARK = [160, 140, 70, 255]    # Darker copper (ground pour)
C_SILK        = [240, 240, 230, 255]   # White silkscreen
C_IC          = [25, 25, 28, 255]      # IC package matte black
C_IC_MARK     = [55, 55, 58, 255]      # IC top marking
C_METAL       = [195, 200, 205, 255]   # Connector metal shell
C_METAL_DARK  = [140, 145, 150, 255]   # Darker metal
C_PLASTIC_BLK = [35, 35, 38, 255]     # Black plastic housing
C_PLASTIC_GRY = [90, 92, 95, 255]     # Gray plastic
C_GOLD        = [210, 175, 55, 255]    # Gold pins/SMA
C_SMA_GOLD    = [200, 165, 40, 255]
C_LED_GREEN   = [30, 220, 50, 230]
C_LED_ORANGE  = [240, 160, 20, 230]
C_LED_YELLOW  = [240, 230, 30, 230]
C_LED_RED     = [220, 40, 30, 230]
C_RED_SW      = [180, 40, 35, 255]    # Red DIP switch / button
C_RED_STANDOFF = [190, 50, 45, 255]   # Red nylon standoff
C_USB_METAL   = [200, 200, 205, 255]
C_CAP_BROWN   = [100, 70, 40, 255]    # MLCC capacitor
C_CAP_GRAY    = [75, 75, 78, 255]     # Tantalum cap
C_INDUCTOR    = [50, 50, 52, 255]     # Power inductor
C_HOLE_PAD    = [180, 160, 90, 255]   # Mounting hole pad
C_BARREL      = [45, 45, 48, 255]     # Barrel jack
C_VIA         = [170, 150, 75, 255]   # Via copper
C_COPPER_POUR = [0, 75, 28, 200]      # Copper pour (slightly lighter green)
C_FERRITE     = [40, 38, 36, 255]     # Ferrite bead
C_RESISTOR    = [20, 20, 22, 255]     # Chip resistor


def cbox(w, h, d, color, pos=(0, 0, 0)):
    """Create colored box at center position"""
    m = box(extents=[w, h, d])
    m.apply_translation(pos)
    m.visual.face_colors = color
    return m


def ccyl(r, h, color, pos=(0, 0, 0), sec=24):
    """Create colored cylinder at position"""
    m = cylinder(radius=r, height=h, sections=sec)
    m.apply_translation(pos)
    m.visual.face_colors = color
    return m


def hollow_box(outer_w, outer_h, outer_d, wall, color, pos=(0, 0, 0)):
    """Create a hollow box (shell) - approximated with 5 faces"""
    parts = []
    ow, oh, od = outer_w, outer_h, outer_d
    x, y, z = pos
    # Top
    parts.append(cbox(ow, oh, wall, color, (x, y, z + od/2 - wall/2)))
    # Bottom
    parts.append(cbox(ow, oh, wall, color, (x, y, z - od/2 + wall/2)))
    # Left
    parts.append(cbox(wall, oh, od, color, (x - ow/2 + wall/2, y, z)))
    # Right
    parts.append(cbox(wall, oh, od, color, (x + ow/2 - wall/2, y, z)))
    # Back
    parts.append(cbox(ow, wall, od, color, (x, y + oh/2 - wall/2, z)))
    return parts


def build_board():
    meshes = []

    # ── Board constants ──
    BW, BH, BT = 214.0, 150.0, 1.535
    Z0 = BT / 2  # top surface Z
    ZB = -BT / 2  # bottom surface Z

    # Z-offsets to prevent z-fighting
    ZS = Z0 + 0.2    # silkscreen Z (well above PCB)
    ZC = Z0 + 0.12   # copper pad Z

    # ════════════════════════════════════════════
    # 1. PCB BASE (multi-layer appearance)
    # ════════════════════════════════════════════
    # Main PCB body
    pcb = cbox(BW, BH, BT, C_PCB_TOP, (BW/2, BH/2, 0))
    meshes.append(pcb)

    # PCB bottom (slightly different shade)
    meshes.append(cbox(BW - 0.1, BH - 0.1, 0.15, C_PCB_BOTTOM, (BW/2, BH/2, ZB - 0.1)))

    # PCB edge strips (FR4 fiberglass visible on all 4 edges)
    edge_h = BT + 0.3
    # Front edge
    meshes.append(cbox(BW, 0.3, edge_h, C_PCB_SIDE, (BW/2, -0.15, 0)))
    # Rear edge
    meshes.append(cbox(BW, 0.3, edge_h, C_PCB_SIDE, (BW/2, BH + 0.15, 0)))
    # Left edge
    meshes.append(cbox(0.3, BH, edge_h, C_PCB_SIDE, (-0.15, BH/2, 0)))
    # Right edge
    meshes.append(cbox(0.3, BH, edge_h, C_PCB_SIDE, (BW + 0.15, BH/2, 0)))

    # Internal copper layer traces (visible at edge as thin lines)
    for layer_z in [-0.3, -0.1, 0.1, 0.3]:
        meshes.append(cbox(BW + 0.1, 0.1, 0.05, C_COPPER_DARK, (BW/2, -0.2, layer_z)))
        meshes.append(cbox(BW + 0.1, 0.1, 0.05, C_COPPER_DARK, (BW/2, BH + 0.2, layer_z)))
        meshes.append(cbox(0.1, BH + 0.1, 0.05, C_COPPER_DARK, (-0.2, BH/2, layer_z)))
        meshes.append(cbox(0.1, BH + 0.1, 0.05, C_COPPER_DARK, (BW + 0.2, BH/2, layer_z)))

    # Board corner chamfers (small 45-degree cuts at corners)
    chamfer = 2.5
    for cx_, cy_ in [(0, 0), (BW, 0), (0, BH), (BW, BH)]:
        sx = 1 if cx_ == 0 else -1
        sy = 1 if cy_ == 0 else -1
        meshes.append(cbox(chamfer, chamfer, BT + 0.5, C_PCB_SIDE,
                          (cx_ + sx * chamfer * 0.3, cy_ + sy * chamfer * 0.3, 0)))

    # ════════════════════════════════════════════
    # 2. MOUNTING HOLES with RED STANDOFF SPACERS
    # ════════════════════════════════════════════
    hole_inset = 5.0
    for hx, hy in [(hole_inset, hole_inset), (BW - hole_inset, hole_inset),
                    (hole_inset, BH - hole_inset), (BW - hole_inset, BH - hole_inset)]:
        # Copper annular ring
        meshes.append(ccyl(3.5, 0.15, C_HOLE_PAD, (hx, hy, Z0 + 0.1)))
        # Red nylon standoff (clearly visible in board photos)
        meshes.append(ccyl(3.0, 8.0, C_RED_STANDOFF, (hx, hy, Z0 + 4.0)))
        # Standoff top
        meshes.append(ccyl(3.2, 0.4, [170, 45, 40, 255], (hx, hy, Z0 + 8.2)))
        # Screw hole (dark center)
        meshes.append(ccyl(1.6, 8.5, [20, 20, 20, 255], (hx, hy, Z0 + 4.25)))
        # Bottom annular ring
        meshes.append(ccyl(3.5, 0.15, C_HOLE_PAD, (hx, hy, ZB - 0.1)))

    # ════════════════════════════════════════════
    # 3. LAN9692 MAIN IC (center, FCBGA 17x17mm)
    # ════════════════════════════════════════════
    cx, cy = BW * 0.42, BH * 0.52
    # BGA pad array (visible around edges)
    meshes.append(cbox(18, 18, 0.1, C_COPPER, (cx, cy, Z0 + 0.08)))
    # Package body
    meshes.append(cbox(17, 17, 1.8, C_IC, (cx, cy, Z0 + 1.0)))
    # Top marking area
    meshes.append(cbox(14, 14, 0.15, C_IC_MARK, (cx, cy, Z0 + 1.95)))
    # Pin-1 dot
    meshes.append(ccyl(0.7, 0.2, C_SILK, (cx - 6.5, cy + 6.5, Z0 + 2.1), 16))
    # Text labels (3 lines of text on IC)
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy + 3, Z0 + 2.1)))
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy - 1, Z0 + 2.1)))
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy - 5, Z0 + 2.1)))
    # Microchip logo on IC
    meshes.append(cbox(4, 1.2, 0.15, [50, 50, 53, 255], (cx - 3, cy + 5.5, Z0 + 2.1)))

    # Decoupling caps around main IC (dense ring)
    for angle in np.linspace(0, 2 * np.pi, 24, endpoint=False):
        dx = cx + 12 * np.cos(angle)
        dy = cy + 12 * np.sin(angle)
        if 15 < dx < BW - 5 and 15 < dy < BH - 5:
            size = np.random.choice([0.6, 0.8, 1.0])
            meshes.append(cbox(size, size * 0.5, size * 0.4, C_CAP_BROWN,
                              (dx, dy, Z0 + size * 0.2)))

    # ════════════════════════════════════════════
    # 4. SILKSCREEN - Microchip logo area
    # ════════════════════════════════════════════
    meshes.append(cbox(30, 6, 0.1, C_SILK, (32, BH - 18, ZS)))
    meshes.append(cbox(22, 3, 0.1, C_SILK, (32, BH - 24, ZS)))
    # Board name
    meshes.append(cbox(25, 2.5, 0.1, C_SILK, (32, BH - 29, ZS)))
    # Revision
    meshes.append(cbox(12, 1.5, 0.1, C_SILK, (32, BH - 32, ZS)))
    # DS number
    meshes.append(cbox(18, 1.2, 0.1, C_SILK, (32, BH - 35, ZS)))

    # ════════════════════════════════════════════
    # 5. 7x MATEnet CONNECTORS (front/bottom edge)
    # ════════════════════════════════════════════
    matenet_w = 11.5
    matenet_d = 9.5
    matenet_h = 8.5
    matenet_spacing = 19.0
    matenet_x0 = 15.0
    C_MATENET = [160, 162, 158, 255]
    C_MATENET_DARK = [120, 122, 118, 255]

    for i in range(7):
        mx = matenet_x0 + i * matenet_spacing
        my = matenet_d / 2 - 2

        # Main body
        meshes.append(cbox(matenet_w, matenet_d, matenet_h, C_MATENET,
                          (mx, my, Z0 + matenet_h/2)))

        # Front face: cable entry slot
        slot_w = 5.0
        slot_h = 4.5
        meshes.append(cbox(slot_w, 1.8, slot_h, [30, 30, 32, 255],
                          (mx, my - matenet_d/2 + 0.5, Z0 + matenet_h/2 - 0.5)))

        # Front face frame
        meshes.append(cbox(matenet_w - 1, 0.6, 1.0, C_MATENET_DARK,
                          (mx, my - matenet_d/2 + 0.3, Z0 + matenet_h - 1.0)))
        meshes.append(cbox(matenet_w - 1, 0.6, 0.8, C_MATENET_DARK,
                          (mx, my - matenet_d/2 + 0.3, Z0 + 1.5)))
        for sx in [-1, 1]:
            meshes.append(cbox(1.5, 0.6, matenet_h - 2, C_MATENET_DARK,
                              (mx + sx * (matenet_w/2 - 1.5), my - matenet_d/2 + 0.3, Z0 + matenet_h/2)))

        # Top latch
        meshes.append(cbox(6, matenet_d - 2, 1.2, [140, 142, 138, 255],
                          (mx, my + 0.5, Z0 + matenet_h + 0.3)))
        meshes.append(cbox(4, 1.5, 0.6, [130, 132, 128, 255],
                          (mx, my - matenet_d/4, Z0 + matenet_h + 0.9)))

        # Side ribs
        for sx in [-1, 1]:
            for r in range(3):
                meshes.append(cbox(0.4, matenet_d - 3, 0.8, [145, 147, 143, 255],
                                  (mx + sx * (matenet_w/2 + 0.15), my + 0.5, Z0 + 2.5 + r * 2.5)))

        # Internal contact pins
        meshes.append(cbox(0.6, 1.0, 3.0, C_GOLD,
                          (mx - 1.0, my - matenet_d/2 + 1, Z0 + matenet_h/2 - 0.5)))
        meshes.append(cbox(0.6, 1.0, 3.0, C_GOLD,
                          (mx + 1.0, my - matenet_d/2 + 1, Z0 + matenet_h/2 - 0.5)))

        # PCB footprint pads
        for px_off in [-4, -2, 0, 2, 4]:
            meshes.append(cbox(1.0, 0.6, 0.2, C_COPPER,
                              (mx + px_off, matenet_d + 1.5, Z0 + 0.15)))

        # SMD shield/anchor pads
        for sx in [-1, 1]:
            meshes.append(cbox(2.0, 1.5, 0.15, C_COPPER,
                              (mx + sx * 6, matenet_d + 0.5, Z0 + 0.12)))

        # Port number silkscreen (J1-J7)
        meshes.append(cbox(3.5, 1.8, 0.08, C_SILK, (mx, matenet_d + 3, ZS)))

        # Status LEDs
        led_y = matenet_d + 5.5
        meshes.append(cbox(1.6, 0.8, 1.0, C_LED_GREEN,
                          (mx - 3.5, led_y, Z0 + 0.5)))
        meshes.append(cbox(1.6, 0.8, 1.0, C_LED_ORANGE,
                          (mx + 3.5, led_y, Z0 + 0.5)))
        # LED silkscreen labels
        meshes.append(cbox(2.0, 0.8, 0.08, C_SILK, (mx - 3.5, led_y + 1.5, ZS)))
        meshes.append(cbox(2.0, 0.8, 0.08, C_SILK, (mx + 3.5, led_y + 1.5, ZS)))

    # ════════════════════════════════════════════
    # 6. 4x SFP+ CAGES (front/bottom edge, right)
    # ════════════════════════════════════════════
    sfp_w = 14.2
    sfp_d = 58.0
    sfp_h = 13.5
    sfp_wall = 0.4
    sfp_spacing = 17.5
    sfp_x0 = 155.0

    for i in range(4):
        sx = sfp_x0 + i * sfp_spacing
        sy = sfp_d / 2 - 4
        sz = Z0 + sfp_h / 2

        # Outer cage shell
        meshes.append(cbox(sfp_w, sfp_d, sfp_wall, C_METAL, (sx, sy, sz + sfp_h/2 - sfp_wall/2)))
        meshes.append(cbox(sfp_w, sfp_d, sfp_wall, C_METAL, (sx, sy, Z0 + sfp_wall/2)))
        meshes.append(cbox(sfp_wall, sfp_d, sfp_h, C_METAL, (sx - sfp_w/2 + sfp_wall/2, sy, sz)))
        meshes.append(cbox(sfp_wall, sfp_d, sfp_h, C_METAL, (sx + sfp_w/2 - sfp_wall/2, sy, sz)))
        meshes.append(cbox(sfp_w, sfp_wall, sfp_h, C_METAL_DARK, (sx, sy + sfp_d/2, sz)))

        # Front bezel
        meshes.append(cbox(sfp_w + 1, 2.0, sfp_h + 1, C_METAL, (sx, -3, sz)))
        # Port opening
        meshes.append(cbox(sfp_w - 2, 2.5, sfp_h - 3, [15, 15, 15, 255], (sx, -3, sz)))

        # Internal guide rails
        meshes.append(cbox(sfp_w - 2, sfp_d - 8, 0.5, C_METAL_DARK,
                          (sx, sy, Z0 + sfp_h * 0.3)))
        meshes.append(cbox(sfp_w - 2, sfp_d - 8, 0.5, C_METAL_DARK,
                          (sx, sy, Z0 + sfp_h * 0.7)))

        # Cage ventilation slots
        for j in range(5):
            meshes.append(cbox(sfp_w - 4, 1.5, 0.4, [170, 175, 180, 255],
                              (sx, sy - sfp_d/4 + j * 8, sz + sfp_h/2 + 0.4)))

        # EMI spring fingers
        for j in range(6):
            meshes.append(cbox(1.0, 0.3, 0.8, C_METAL_DARK,
                              (sx - sfp_w/3 + j * (sfp_w * 0.6 / 5), -2, sz + sfp_h/2 + 0.6)))

        # SFP LED
        meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN,
                          (sx, sfp_d - 2, Z0 + 0.5)))
        # LED label
        meshes.append(cbox(3, 0.8, 0.08, C_SILK, (sx, sfp_d - 0.5, ZS)))

        # SFP port label (S6-S9)
        meshes.append(cbox(4, 1.5, 0.08, C_SILK, (sx, sfp_d + 1.5, ZS)))

    # ════════════════════════════════════════════
    # 7. RJ45 MANAGEMENT PORT (rear/top edge)
    # ════════════════════════════════════════════
    rj_w, rj_h, rj_d = 16.0, 13.5, 21.5
    rj_x = BW - 28
    rj_y = BH - rj_h/2 + 4

    meshes.append(cbox(rj_w, rj_h, rj_d, C_METAL, (rj_x, rj_y, Z0 + rj_d/2)))
    meshes.append(cbox(rj_w + 0.5, 0.5, rj_d, [175, 180, 185, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + rj_d/2)))
    meshes.append(cbox(12, 3, 10, [15, 15, 15, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + 8)))
    meshes.append(cbox(8, 1, 2, [25, 25, 25, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + 14)))
    # RJ45 LEDs
    meshes.append(cbox(3, 2, 3, C_LED_GREEN,
                      (rj_x - 5.5, rj_y + rj_h/2, Z0 + rj_d - 2.5)))
    meshes.append(cbox(3, 2, 3, C_LED_YELLOW,
                      (rj_x + 5.5, rj_y + rj_h/2, Z0 + rj_d - 2.5)))
    # RJ45 shield tabs
    for tab_x in [-1, 1]:
        meshes.append(cbox(1.5, 1.0, rj_d, [165, 170, 175, 255],
                          (rj_x + tab_x * 8.5, rj_y - rj_h/2, Z0 + rj_d/2)))

    # ════════════════════════════════════════════
    # 8. USB-C SERIAL PORT (rear edge)
    # ════════════════════════════════════════════
    usbc_x = BW * 0.45
    usbc_y = BH + 1

    meshes.append(cbox(9.0, 7.5, 3.2, C_USB_METAL, (usbc_x, usbc_y, Z0 + 1.6)))
    meshes.append(cbox(7.5, 2.0, 2.4, [20, 20, 22, 255], (usbc_x, BH + 4, Z0 + 1.6)))
    meshes.append(ccyl(1.1, 2.0, [20, 20, 22, 255], (usbc_x - 3.2, BH + 4, Z0 + 1.6), 12))
    meshes.append(ccyl(1.1, 2.0, [20, 20, 22, 255], (usbc_x + 3.2, BH + 4, Z0 + 1.6), 12))
    # USB shield tabs
    meshes.append(cbox(2, 1, 3.2, C_USB_METAL, (usbc_x - 5, usbc_y - 3, Z0 + 1.6)))
    meshes.append(cbox(2, 1, 3.2, C_USB_METAL, (usbc_x + 5, usbc_y - 3, Z0 + 1.6)))
    # USB TX/RX LEDs
    meshes.append(cbox(1.2, 0.6, 0.8, C_LED_GREEN,
                      (usbc_x - 6, BH - 3, Z0 + 0.4)))
    meshes.append(cbox(1.2, 0.6, 0.8, C_LED_GREEN,
                      (usbc_x + 6, BH - 3, Z0 + 0.4)))
    # USB labels
    meshes.append(cbox(5, 1.2, 0.08, C_SILK, (usbc_x, BH - 5, ZS)))
    meshes.append(cbox(2, 0.8, 0.08, C_SILK, (usbc_x - 6, BH - 4.5, ZS)))
    meshes.append(cbox(2, 0.8, 0.08, C_SILK, (usbc_x + 6, BH - 4.5, ZS)))

    # ════════════════════════════════════════════
    # 9. 12V DC BARREL JACK (rear edge, far right)
    # ════════════════════════════════════════════
    bj_x = BW - 8
    bj_y = BH + 2
    bj_z = Z0 + 5.5

    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
    barrel = cylinder(radius=5.5, height=14.0, sections=24)
    barrel.apply_transform(rot_x)
    barrel.apply_translation([bj_x, bj_y + 5, bj_z])
    barrel.visual.face_colors = C_BARREL
    meshes.append(barrel)

    barrel_hole = cylinder(radius=2.5, height=12.0, sections=16)
    barrel_hole.apply_transform(rot_x)
    barrel_hole.apply_translation([bj_x, bj_y + 8, bj_z])
    barrel_hole.visual.face_colors = [15, 15, 15, 255]
    meshes.append(barrel_hole)

    barrel_pin = cylinder(radius=1.0, height=8, sections=12)
    barrel_pin.apply_transform(rot_x)
    barrel_pin.apply_translation([bj_x, bj_y + 7, bj_z])
    barrel_pin.visual.face_colors = C_GOLD
    meshes.append(barrel_pin)

    meshes.append(cbox(12, 4, 8, C_BARREL, (bj_x, bj_y - 2, bj_z)))
    # Barrel jack label
    meshes.append(cbox(6, 1.5, 0.08, C_SILK, (bj_x, BH - 5, ZS)))

    # ════════════════════════════════════════════
    # 10. POWER SWITCH (slide switch, rear)
    # ════════════════════════════════════════════
    psw_x = BW - 22
    psw_y = BH - 2

    meshes.append(cbox(10, 5, 5, C_PLASTIC_BLK, (psw_x, psw_y, Z0 + 2.5)))
    meshes.append(cbox(3.5, 2.5, 3, [200, 200, 205, 255], (psw_x + 2, psw_y, Z0 + 5.2)))
    # Switch label
    meshes.append(cbox(6, 1.2, 0.08, C_SILK, (psw_x, psw_y - 4, ZS)))

    # Power LEDs
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (psw_x - 7, psw_y, Z0 + 0.5)))
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_RED, (psw_x - 10, psw_y, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 11. SMA CONNECTORS (1PPS IN/OUT, rear)
    # ════════════════════════════════════════════
    for sma_x, label in [(BW - 42, "OUT"), (BW - 54, "IN")]:
        sma = cylinder(radius=3.2, height=9.5, sections=6)
        sma.apply_transform(rot_x)
        sma.apply_translation([sma_x, BH + 4, Z0 + 5])
        sma.visual.face_colors = C_SMA_GOLD
        meshes.append(sma)

        sma_pin = cylinder(radius=0.65, height=5, sections=12)
        sma_pin.apply_transform(rot_x)
        sma_pin.apply_translation([sma_x, BH + 9, Z0 + 5])
        sma_pin.visual.face_colors = C_GOLD
        meshes.append(sma_pin)

        sma_ins = cylinder(radius=2.0, height=1.5, sections=16)
        sma_ins.apply_transform(rot_x)
        sma_ins.apply_translation([sma_x, BH + 6, Z0 + 5])
        sma_ins.visual.face_colors = [240, 240, 240, 255]
        meshes.append(sma_ins)

        meshes.append(cbox(8, 3, 8, C_PCB_TOP, (sma_x, BH - 1, Z0 + 4)))
        meshes.append(cbox(5, 1.5, 0.1, C_SILK, (sma_x, BH - 5, ZS)))

    # ════════════════════════════════════════════
    # 12. PCIe 2.0 OCuLink CONNECTOR (rear)
    # ════════════════════════════════════════════
    oc_x = 68
    oc_y = BH - 2

    meshes.append(cbox(26, 8, 6, C_PLASTIC_BLK, (oc_x, oc_y, Z0 + 3)))
    meshes.append(cbox(22, 2, 4, [60, 60, 63, 255], (oc_x, oc_y + 4, Z0 + 3)))
    meshes.append(cbox(6, 1, 2, C_METAL_DARK, (oc_x, oc_y + 5, Z0 + 6)))
    # OCuLink label
    meshes.append(cbox(8, 1.5, 0.08, C_SILK, (oc_x, oc_y - 6, ZS)))
    # Shield pads
    for sx in [-1, 1]:
        meshes.append(cbox(2, 2, 0.15, C_COPPER, (oc_x + sx * 14, oc_y, Z0 + 0.12)))

    # ════════════════════════════════════════════
    # 13. RESET BUTTON (rear area)
    # ════════════════════════════════════════════
    rst_x = BW * 0.55
    rst_y = BH - 5

    meshes.append(cbox(4.5, 4.5, 2.5, C_PLASTIC_BLK, (rst_x, rst_y, Z0 + 1.25)))
    meshes.append(ccyl(1.5, 2, C_LED_RED, (rst_x, rst_y, Z0 + 3.2), 16))
    # Reset label
    meshes.append(cbox(5, 1.2, 0.08, C_SILK, (rst_x, rst_y - 4, ZS)))

    # ════════════════════════════════════════════
    # 14. DIP SWITCH (4-pin, boot mode)
    # ════════════════════════════════════════════
    dip_x = 48
    dip_y = BH - 38

    meshes.append(cbox(11, 5.2, 3.5, C_RED_SW, (dip_x, dip_y, Z0 + 1.75)))
    for i in range(4):
        meshes.append(cbox(1.8, 2.0, 1.5, [230, 230, 235, 255],
                          (dip_x - 4 + i * 2.54, dip_y, Z0 + 3.6)))
    # DIP label "SW1"
    meshes.append(cbox(8, 1, 0.1, C_SILK, (dip_x, dip_y - 4, ZS)))
    # VCORE labels
    meshes.append(cbox(5, 0.8, 0.08, C_SILK, (dip_x, dip_y + 4, ZS)))

    # ════════════════════════════════════════════
    # 15. EXPANSION HEADER (2x20, RPi compatible)
    # ════════════════════════════════════════════
    exp_x = BW - 52
    exp_y = BH - 48

    meshes.append(cbox(51, 5.1, 8.5, C_PLASTIC_BLK, (exp_x, exp_y, Z0 + 4.25)))
    for i in range(20):
        for j in range(2):
            meshes.append(cbox(0.5, 0.5, 11, C_GOLD,
                              (exp_x - 24 + i * 2.54, exp_y - 1.27 + j * 2.54, Z0 + 2)))
    # Header label "J4"
    meshes.append(cbox(4, 1.5, 0.08, C_SILK, (exp_x - 28, exp_y, ZS)))

    # ════════════════════════════════════════════
    # 16. JTAG HEADER (10-pin, 0.05" pitch)
    # ════════════════════════════════════════════
    jtag_x = BW - 25
    jtag_y = BH - 62

    meshes.append(cbox(13.5, 5.1, 6, C_PLASTIC_BLK, (jtag_x, jtag_y, Z0 + 3)))
    for i in range(5):
        for j in range(2):
            meshes.append(cbox(0.4, 0.4, 8, C_GOLD,
                              (jtag_x - 5 + i * 2.54, jtag_y - 1.27 + j * 2.54, Z0 + 1.5)))
    # JTAG label
    meshes.append(cbox(5, 1.2, 0.08, C_SILK, (jtag_x, jtag_y - 4.5, ZS)))

    # ════════════════════════════════════════════
    # 17. QSPI FLASH PROGRAM HEADER (6-pin, 1.8V)
    # ════════════════════════════════════════════
    qspi_x = cx - 30
    qspi_y = cy + 20

    meshes.append(cbox(7.62, 5.1, 6, C_PLASTIC_BLK, (qspi_x, qspi_y, Z0 + 3)))
    for i in range(3):
        for j in range(2):
            meshes.append(cbox(0.5, 0.5, 8, C_GOLD,
                              (qspi_x - 2.54 + i * 2.54, qspi_y - 1.27 + j * 2.54, Z0 + 1.5)))
    meshes.append(cbox(5, 1.0, 0.08, C_SILK, (qspi_x, qspi_y - 4, ZS)))

    # ════════════════════════════════════════════
    # 18. TEMPERATURE SENSOR HEADER (2-pin)
    # ════════════════════════════════════════════
    tmp_x = cx + 25
    tmp_y = cy + 20

    meshes.append(cbox(5.08, 2.54, 6, C_PLASTIC_BLK, (tmp_x, tmp_y, Z0 + 3)))
    for i in range(2):
        meshes.append(cbox(0.5, 0.5, 8, C_GOLD,
                          (tmp_x - 1.27 + i * 2.54, tmp_y, Z0 + 1.5)))

    # ════════════════════════════════════════════
    # 19. LAN8870 PHY CHIPS (7x, QFN packages)
    # ════════════════════════════════════════════
    for i in range(7):
        px = matenet_x0 + i * matenet_spacing
        py = 32

        # QFN exposed pad
        meshes.append(cbox(5, 5, 0.1, C_COPPER, (px, py, Z0 + 0.08)))
        # QFN package
        meshes.append(cbox(7, 7, 0.9, C_IC, (px, py, Z0 + 0.55)))
        # Pin-1 mark
        meshes.append(ccyl(0.4, 0.2, C_SILK, (px - 2.8, py + 2.8, Z0 + 1.1), 12))
        # Text label on IC
        meshes.append(cbox(4, 0.4, 0.1, C_IC_MARK, (px, py, Z0 + 1.1)))

        # Per-PHY decoupling caps (4 per PHY)
        for dx, dy in [(-5, -2), (-5, 2), (5, -2), (5, 2)]:
            meshes.append(cbox(1.0, 0.5, 0.5, C_CAP_BROWN,
                              (px + dx, py + dy, Z0 + 0.25)))

        # Ferrite beads near each PHY
        meshes.append(cbox(1.6, 0.8, 0.6, C_FERRITE,
                          (px, py + 5.5, Z0 + 0.3)))

    # ════════════════════════════════════════════
    # 20. LAN8840 PHY (management port, QFN)
    # ════════════════════════════════════════════
    lan8840_x = BW - 30
    lan8840_y = BH - 22
    meshes.append(cbox(5, 5, 0.1, C_COPPER, (lan8840_x, lan8840_y, Z0 + 0.08)))
    meshes.append(cbox(6, 6, 0.9, C_IC, (lan8840_x, lan8840_y, Z0 + 0.55)))
    meshes.append(ccyl(0.35, 0.2, C_SILK, (lan8840_x - 2.5, lan8840_y + 2.5, Z0 + 1.1), 12))
    # LAN8840 decoupling
    for dx, dy in [(-4.5, 0), (4.5, 0), (0, -4.5), (0, 4.5)]:
        meshes.append(cbox(0.8, 0.5, 0.4, C_CAP_BROWN,
                          (lan8840_x + dx, lan8840_y + dy, Z0 + 0.2)))

    # ════════════════════════════════════════════
    # 21. MEMORY: QSPI NOR Flash + eMMC footprint
    # ════════════════════════════════════════════
    # NOR Flash (SOIC-8)
    meshes.append(cbox(5, 4, 1.2, C_IC, (cx - 22, cy + 12, Z0 + 0.7)))
    meshes.append(cbox(3.5, 2.5, 0.15, C_IC_MARK, (cx - 22, cy + 12, Z0 + 1.35)))
    # NOR Flash pins (visible gull-wing leads)
    for i in range(4):
        meshes.append(cbox(0.4, 0.8, 0.2, C_GOLD,
                          (cx - 22 - 2.5, cy + 10.5 + i * 1.27, Z0 + 0.15)))
        meshes.append(cbox(0.4, 0.8, 0.2, C_GOLD,
                          (cx - 22 + 2.5, cy + 10.5 + i * 1.27, Z0 + 0.15)))

    # eMMC NAND footprint (not populated) - empty pads
    meshes.append(cbox(11, 15, 0.15, C_COPPER, (cx - 24, cy - 3, Z0 + 0.12)))
    # "DNP" silkscreen
    meshes.append(cbox(4, 1.5, 0.08, C_SILK, (cx - 24, cy - 3, ZS)))

    # ════════════════════════════════════════════
    # 22. CLOCK OSCILLATORS
    # ════════════════════════════════════════════
    # 156.25 MHz (SerDes ref clock)
    meshes.append(cbox(5, 3.2, 1.5, C_METAL, (cx + 22, cy + 12, Z0 + 0.85)))
    meshes.append(cbox(3.5, 1.5, 0.15, [220, 220, 225, 255], (cx + 22, cy + 12, Z0 + 1.7)))
    meshes.append(cbox(1, 0.3, 0.1, C_SILK, (cx + 22, cy + 14, ZS + 0.5)))

    # 25 MHz (PHY ref clock)
    meshes.append(cbox(5, 3.2, 1.5, C_METAL, (cx + 22, cy - 10, Z0 + 0.85)))
    meshes.append(cbox(3.5, 1.5, 0.15, [220, 220, 225, 255], (cx + 22, cy - 10, Z0 + 1.7)))
    meshes.append(cbox(1, 0.3, 0.1, C_SILK, (cx + 22, cy - 12, ZS + 0.5)))

    # ════════════════════════════════════════════
    # 23. DC/DC CONVERTERS & INDUCTORS (power section)
    # ════════════════════════════════════════════
    inductor_pos = [
        (18, BH - 14, 6.5, 6.5, 4.0),
        (32, BH - 14, 6.5, 6.5, 4.0),
        (50, BH - 14, 5.5, 5.5, 3.5),
        (18, BH - 28, 5.5, 5.5, 3.5),
        (35, BH - 28, 4.5, 4.5, 3.0),
        (68, BH - 14, 4.5, 4.5, 3.0),
    ]
    for ix, iy, iw, ih, id_ in inductor_pos:
        meshes.append(cbox(iw, ih, id_, C_INDUCTOR, (ix, iy, Z0 + id_/2)))
        meshes.append(cbox(iw - 1, ih - 1, 0.2, [70, 70, 73, 255], (ix, iy, Z0 + id_ + 0.15)))
        # Inductor pads
        meshes.append(cbox(iw, 1.5, 0.15, C_COPPER, (ix, iy - ih/2 - 0.5, Z0 + 0.12)))
        meshes.append(cbox(iw, 1.5, 0.15, C_COPPER, (ix, iy + ih/2 + 0.5, Z0 + 0.12)))

    # DC/DC converter ICs
    dcdc_pos = [(25, BH - 21), (45, BH - 21), (58, BH - 21)]
    for dx, dy in dcdc_pos:
        meshes.append(cbox(3.5, 3.5, 0.1, C_COPPER, (dx, dy, Z0 + 0.08)))
        meshes.append(cbox(5, 4, 0.9, C_IC, (dx, dy, Z0 + 0.55)))
        # DC/DC decoupling
        meshes.append(cbox(1.0, 0.6, 0.5, C_CAP_BROWN, (dx + 4, dy, Z0 + 0.25)))
        meshes.append(cbox(1.0, 0.6, 0.5, C_CAP_BROWN, (dx - 4, dy, Z0 + 0.25)))

    # ════════════════════════════════════════════
    # 24. CAPACITORS (dense distribution)
    # ════════════════════════════════════════════
    np.random.seed(42)
    cap_positions = []

    # Define exclusion zones
    def in_exclusion_zone(px, py):
        if abs(px - cx) < 14 and abs(py - cy) < 14:  # Main IC
            return True
        if py < 15 and px < 150:  # MATEnet area
            return True
        if py < sfp_d and px > 148:  # SFP area
            return True
        if py > BH - 5:  # Rear edge
            return True
        if abs(px - exp_x) < 28 and abs(py - exp_y) < 5:  # Expansion header
            return True
        return False

    # Generate more capacitor positions
    for _ in range(120):
        cx_ = np.random.uniform(8, BW - 8)
        cy_ = np.random.uniform(18, BH - 6)
        if not in_exclusion_zone(cx_, cy_):
            cap_positions.append((cx_, cy_))

    for cx_, cy_ in cap_positions[:80]:
        size = np.random.choice([0.4, 0.6, 0.8, 1.0, 1.6, 2.0])
        h = size * 0.45
        color = C_CAP_BROWN if np.random.random() > 0.25 else C_CAP_GRAY
        meshes.append(cbox(size, size * 0.55, h, color, (cx_, cy_, Z0 + h/2)))

    # Larger electrolytic / tantalum caps near power
    for ex, ey in [(12, BH - 8), (BW - 15, BH - 15), (85, BH - 10),
                    (12, BH - 35), (BW - 12, BH - 30)]:
        meshes.append(cbox(3.5, 3, 2.5, [40, 35, 30, 255], (ex, ey, Z0 + 1.25)))
        meshes.append(cbox(3.5, 0.5, 2.5, [180, 160, 100, 255], (ex, ey + 1.5, Z0 + 1.25)))

    # ════════════════════════════════════════════
    # 25. RESISTORS (dense distribution)
    # ════════════════════════════════════════════
    np.random.seed(99)
    for _ in range(50):
        rx = np.random.uniform(12, BW - 12)
        ry = np.random.uniform(20, BH - 8)
        if not in_exclusion_zone(rx, ry):
            size = np.random.choice([0.4, 0.6, 1.0])
            meshes.append(cbox(size, size * 0.5, size * 0.3, C_RESISTOR,
                              (rx, ry, Z0 + size * 0.15)))

    # ════════════════════════════════════════════
    # 26. RESISTOR ARRAYS & SMALL ICs
    # ════════════════════════════════════════════
    for rx, ry in [(cx + 12, cy + 20), (cx - 12, cy + 20),
                    (cx + 15, cy - 18), (cx - 15, cy - 15),
                    (cx + 8, cy + 15), (cx - 8, cy - 12)]:
        meshes.append(cbox(3.2, 1.6, 0.6, C_IC, (rx, ry, Z0 + 0.3)))

    # ZL40241 Clock buffer
    meshes.append(cbox(5, 5, 0.9, C_IC, (cx + 30, cy - 2, Z0 + 0.55)))
    meshes.append(ccyl(0.3, 0.15, C_SILK, (cx + 27.5, cy + 0.5, Z0 + 1.05), 10))

    # MCP2200 UART-to-USB
    meshes.append(cbox(5, 5, 0.9, C_IC, (usbc_x, BH - 12, Z0 + 0.55)))
    meshes.append(ccyl(0.3, 0.15, C_SILK, (usbc_x - 2, BH - 9.5, Z0 + 1.05), 10))

    # MCP9015 voltage supervisor (near reset)
    meshes.append(cbox(3, 3, 0.8, C_IC, (rst_x + 8, rst_y + 2, Z0 + 0.5)))

    # ESD protection ICs (near connectors)
    esd_positions = [(usbc_x - 8, BH - 8), (usbc_x + 8, BH - 8),
                      (oc_x - 16, BH - 5), (oc_x + 16, BH - 5)]
    for ex, ey in esd_positions:
        meshes.append(cbox(2.5, 1.5, 0.6, C_IC, (ex, ey, Z0 + 0.3)))

    # Level shifters near expansion header
    meshes.append(cbox(4, 3, 0.8, C_IC, (exp_x - 30, exp_y + 5, Z0 + 0.5)))
    meshes.append(cbox(4, 3, 0.8, C_IC, (exp_x + 30, exp_y + 5, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 27. POWER STATUS LEDs (5x green)
    # ════════════════════════════════════════════
    for i, label in enumerate(["0.9V", "1.1V", "1.8V", "3.3V", "5V"]):
        lx = BW - 50 + i * 6
        ly = BH - 10
        meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (lx, ly, Z0 + 0.5)))
        meshes.append(cbox(3, 1, 0.1, C_SILK, (lx, ly - 2, ZS)))
        # Resistor near each LED
        meshes.append(cbox(0.6, 0.3, 0.3, C_RESISTOR, (lx + 2, ly, Z0 + 0.15)))

    # Board status LEDs
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (rst_x - 8, rst_y, Z0 + 0.5)))
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_YELLOW, (rst_x - 11, rst_y, Z0 + 0.5)))
    meshes.append(cbox(2, 0.8, 0.08, C_SILK, (rst_x - 8, rst_y - 2, ZS)))
    meshes.append(cbox(2, 0.8, 0.08, C_SILK, (rst_x - 11, rst_y - 2, ZS)))

    # ════════════════════════════════════════════
    # 28. SILKSCREEN DETAILS
    # ════════════════════════════════════════════
    # Component outlines near PHY chips
    for i in range(7):
        px = matenet_x0 + i * matenet_spacing
        meshes.append(cbox(8, 0.15, 0.1, C_SILK, (px, 28, ZS)))
        meshes.append(cbox(8, 0.15, 0.1, C_SILK, (px, 36, ZS)))
        meshes.append(cbox(0.15, 8, 0.1, C_SILK, (px - 4, 32, ZS)))
        meshes.append(cbox(0.15, 8, 0.1, C_SILK, (px + 4, 32, ZS)))

    # Board outline marking
    meshes.append(cbox(BW - 20, 0.2, 0.1, C_SILK, (BW/2, 12, ZS)))
    meshes.append(cbox(0.2, 30, 0.1, C_SILK, (10, BH/2, ZS)))
    meshes.append(cbox(0.2, 30, 0.1, C_SILK, (BW - 10, BH/2, ZS)))

    # IC outline for main LAN9692
    for dx in [-9, 9]:
        meshes.append(cbox(0.2, 18, 0.1, C_SILK, (cx + dx, cy, ZS)))
    for dy in [-9, 9]:
        meshes.append(cbox(18, 0.2, 0.1, C_SILK, (cx, cy + dy, ZS)))

    # Connector reference designators scattered
    ref_labels = [
        (15, BH - 42, 3, 1),    # Near DIP
        (88, BH - 5, 4, 1.2),   # Near USB
        (BW - 55, BH - 5, 3, 1),  # Near SMA
        (BW - 40, BH - 28, 4, 1.2),  # Near power
        (120, 45, 3, 1),
        (85, 65, 3, 1),
    ]
    for lx, ly, lw, lh in ref_labels:
        meshes.append(cbox(lw, lh, 0.08, C_SILK, (lx, ly, ZS)))

    # ════════════════════════════════════════════
    # 29. TEST POINTS (scattered copper dots)
    # ════════════════════════════════════════════
    tp_positions = [(30, 50), (55, 65), (80, 45), (100, 90), (130, 70),
                    (150, 100), (170, 85), (100, 120), (130, 115),
                    (45, 80), (65, 100), (110, 60), (140, 95),
                    (175, 55), (190, 75), (95, 42)]
    for tx, ty in tp_positions:
        meshes.append(ccyl(0.8, 0.2, C_COPPER, (tx, ty, Z0 + 0.3), 12))
        # TP label
        meshes.append(cbox(1.5, 0.6, 0.08, C_SILK, (tx + 1.5, ty, ZS)))

    # ════════════════════════════════════════════
    # 30. PCB VIAS (small copper dots throughout)
    # ════════════════════════════════════════════
    np.random.seed(77)
    for _ in range(150):
        vx = np.random.uniform(4, BW - 4)
        vy = np.random.uniform(4, BH - 4)
        if not in_exclusion_zone(vx, vy):
            meshes.append(ccyl(0.25, 0.15, C_VIA, (vx, vy, Z0 + 0.12), 8))

    # Dense via stitching around SFP area
    for i in range(20):
        for j in range(5):
            vx = 145 + i * 3.5
            vy = 10 + j * 8
            if vx < BW - 3:
                meshes.append(ccyl(0.2, 0.12, C_VIA, (vx, vy, Z0 + 0.11), 8))

    # ════════════════════════════════════════════
    # 31. COPPER POUR / GROUND PLANE AREAS
    # ════════════════════════════════════════════
    # Under SFP area (large ground plane)
    meshes.append(cbox(70, 45, 0.08, C_COPPER_POUR, (BW - 42, 32, Z0 + 0.06)))

    # Under power section
    meshes.append(cbox(60, 30, 0.08, C_COPPER_POUR, (40, BH - 20, Z0 + 0.06)))

    # Under main IC
    meshes.append(cbox(25, 25, 0.08, C_COPPER_POUR, (cx, cy, Z0 + 0.06)))

    # ════════════════════════════════════════════
    # 32. FERRITE BEADS & EMI COMPONENTS
    # ════════════════════════════════════════════
    ferrite_positions = [
        (12, 45), (12, 55), (12, 65),    # Left edge power filtering
        (BW - 12, 45), (BW - 12, 55),    # Right edge
        (100, BH - 15), (110, BH - 15),  # Near USB
    ]
    for fx, fy in ferrite_positions:
        meshes.append(cbox(1.6, 0.8, 0.8, C_FERRITE, (fx, fy, Z0 + 0.4)))

    # ════════════════════════════════════════════
    # 33. BOTTOM SIDE COMPONENTS (visible when tilted)
    # ════════════════════════════════════════════
    # Bottom side has some components too
    np.random.seed(55)
    for _ in range(30):
        bx = np.random.uniform(15, BW - 15)
        by = np.random.uniform(15, BH - 15)
        if not in_exclusion_zone(bx, by):
            size = np.random.choice([0.6, 0.8, 1.0])
            meshes.append(cbox(size, size * 0.5, size * 0.35, C_CAP_BROWN,
                              (bx, by, ZB - size * 0.175)))

    return meshes


def main():
    print("Building EVB-LAN9692-LM 3D model v4 (High Quality)...")
    meshes = build_board()
    print(f"  Total mesh parts: {len(meshes)}")

    # ── Convert Z-up (trimesh) → Y-up (GLTF/GLB standard) ──
    rot_to_yup = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    for m in meshes:
        m.apply_transform(rot_to_yup)

    scene = trimesh.Scene()
    for i, m in enumerate(meshes):
        scene.add_geometry(m, node_name=f"p{i:03d}")

    out = "/home/kim/lan9692-model/EVB-LAN9692-LM.glb"
    scene.export(out, file_type='glb')
    print(f"  Exported: {out}")

    import os
    size = os.path.getsize(out)
    print(f"  File size: {size / 1024:.0f} KB")
    print(f"  Board: 214 x 150 x 1.535 mm")
    print(f"  Components: 7x MATEnet, 4x SFP+, RJ45, USB-C, DC jack, 2x SMA")
    print(f"  New: Red standoffs, PCB vias, dense passives, edge layers")
    print("  Done!")


if __name__ == "__main__":
    main()
