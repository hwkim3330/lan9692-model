#!/usr/bin/env python3
"""
EVB-LAN9692-LM 3D Board Model Generator v2
More detailed and realistic model based on Hardware User's Guide (DS50003848B)
Board: 214 x 150 mm, 4-layer PCB, 1.535mm thick
"""

import trimesh
import numpy as np
from trimesh.creation import box, cylinder


# ── Color Palette ──
C_PCB_TOP     = [0, 85, 30, 255]       # Dark green solder mask
C_PCB_SIDE    = [0, 70, 25, 255]       # PCB edge (slightly darker)
C_PCB_BOTTOM  = [0, 75, 28, 255]
C_COPPER      = [180, 155, 80, 255]    # Exposed copper/ENIG gold
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
C_USB_METAL   = [200, 200, 205, 255]
C_CAP_BROWN   = [100, 70, 40, 255]    # MLCC capacitor
C_CAP_GRAY    = [75, 75, 78, 255]     # Tantalum cap
C_INDUCTOR    = [50, 50, 52, 255]     # Power inductor
C_HOLE_PAD    = [180, 160, 90, 255]   # Mounting hole pad
C_BARREL      = [45, 45, 48, 255]     # Barrel jack


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

    # Z-offsets to prevent z-fighting: generous separation from PCB surface
    ZS = Z0 + 0.2    # silkscreen Z (well above PCB)
    ZC = Z0 + 0.12   # copper pad Z

    # ════════════════════════════════════════════
    # 1. PCB BASE
    # ════════════════════════════════════════════
    pcb = cbox(BW, BH, BT, C_PCB_TOP, (BW/2, BH/2, 0))
    meshes.append(pcb)

    # ════════════════════════════════════════════
    # 2. MOUNTING HOLES (4 corners)
    # ════════════════════════════════════════════
    hole_inset = 5.0
    for hx, hy in [(hole_inset, hole_inset), (BW - hole_inset, hole_inset),
                    (hole_inset, BH - hole_inset), (BW - hole_inset, BH - hole_inset)]:
        # Copper annular ring - raised above PCB
        meshes.append(ccyl(3.5, 0.15, C_HOLE_PAD, (hx, hy, Z0 + 0.1)))
        # Hole (dark) - raised to avoid z-fight
        meshes.append(ccyl(1.6, 0.3, [20, 20, 20, 255], (hx, hy, Z0 + 0.15)))

    # ════════════════════════════════════════════
    # 3. LAN9692 MAIN IC (center, FCBGA 17x17mm)
    # ════════════════════════════════════════════
    cx, cy = BW * 0.42, BH * 0.52
    # Package body
    meshes.append(cbox(17, 17, 1.8, C_IC, (cx, cy, Z0 + 0.9)))
    # Top marking area (lighter) - single combined layer, no stacking
    meshes.append(cbox(14, 14, 0.15, C_IC_MARK, (cx, cy, Z0 + 1.85)))
    # Pin-1 dot
    meshes.append(ccyl(0.7, 0.2, C_SILK, (cx - 6.5, cy + 6.5, Z0 + 2.0), 16))
    # Text labels (raised above marking)
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy + 3, Z0 + 2.0)))
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy - 1, Z0 + 2.0)))
    meshes.append(cbox(10, 0.6, 0.15, [45, 45, 48, 255], (cx, cy - 5, Z0 + 2.0)))

    # ════════════════════════════════════════════
    # 4. SILKSCREEN - Microchip logo area
    # ════════════════════════════════════════════
    meshes.append(cbox(30, 6, 0.1, C_SILK, (32, BH - 18, ZS)))
    meshes.append(cbox(22, 3, 0.1, C_SILK, (32, BH - 24, ZS)))
    # Board name
    meshes.append(cbox(25, 2.5, 0.1, C_SILK, (32, BH - 29, ZS)))

    # ════════════════════════════════════════════
    # 5. 7x MATEnet CONNECTORS (front/bottom edge)
    #    TE Connectivity MATEnet, automotive single-pair 1000BASE-T1
    #    Compact gray housing with top latch, narrow cable slot
    # ════════════════════════════════════════════
    matenet_w = 11.5    # connector body width
    matenet_d = 9.5     # depth (front-to-back)
    matenet_h = 8.5     # height above PCB
    matenet_spacing = 19.0
    matenet_x0 = 15.0
    C_MATENET = [160, 162, 158, 255]      # Light warm gray (MATEnet housing)
    C_MATENET_DARK = [120, 122, 118, 255] # Slightly darker for recesses

    for i in range(7):
        mx = matenet_x0 + i * matenet_spacing
        my = matenet_d / 2 - 2  # overhangs front edge

        # ── Main body (light gray plastic) ──
        meshes.append(cbox(matenet_w, matenet_d, matenet_h, C_MATENET,
                          (mx, my, Z0 + matenet_h/2)))

        # ── Front face: recessed cable entry slot ──
        slot_w = 5.0   # narrow slot
        slot_h = 4.5
        meshes.append(cbox(slot_w, 1.8, slot_h, [30, 30, 32, 255],
                          (mx, my - matenet_d/2 + 0.5, Z0 + matenet_h/2 - 0.5)))

        # ── Front face frame (raised border around slot) ──
        # Top bar
        meshes.append(cbox(matenet_w - 1, 0.6, 1.0, C_MATENET_DARK,
                          (mx, my - matenet_d/2 + 0.3, Z0 + matenet_h - 1.0)))
        # Bottom bar
        meshes.append(cbox(matenet_w - 1, 0.6, 0.8, C_MATENET_DARK,
                          (mx, my - matenet_d/2 + 0.3, Z0 + 1.5)))
        # Side pillars
        for sx in [-1, 1]:
            meshes.append(cbox(1.5, 0.6, matenet_h - 2, C_MATENET_DARK,
                              (mx + sx * (matenet_w/2 - 1.5), my - matenet_d/2 + 0.3, Z0 + matenet_h/2)))

        # ── Top latch (characteristic MATEnet feature) ──
        meshes.append(cbox(6, matenet_d - 2, 1.2, [140, 142, 138, 255],
                          (mx, my + 0.5, Z0 + matenet_h + 0.3)))
        # Latch ridge
        meshes.append(cbox(4, 1.5, 0.6, [130, 132, 128, 255],
                          (mx, my - matenet_d/4, Z0 + matenet_h + 0.9)))

        # ── Side ribs (grip texture) ──
        for sx in [-1, 1]:
            for r in range(3):
                meshes.append(cbox(0.4, matenet_d - 3, 0.8, [145, 147, 143, 255],
                                  (mx + sx * (matenet_w/2 + 0.15), my + 0.5, Z0 + 2.5 + r * 2.5)))

        # ── Internal contact pins visible in slot ──
        meshes.append(cbox(0.6, 1.0, 3.0, C_GOLD,
                          (mx - 1.0, my - matenet_d/2 + 1, Z0 + matenet_h/2 - 0.5)))
        meshes.append(cbox(0.6, 1.0, 3.0, C_GOLD,
                          (mx + 1.0, my - matenet_d/2 + 1, Z0 + matenet_h/2 - 0.5)))

        # ── PCB footprint pads (behind connector, visible) ──
        for px_off in [-4, -2, 0, 2, 4]:
            meshes.append(cbox(1.0, 0.6, 0.2, C_COPPER,
                              (mx + px_off, matenet_d + 1.5, Z0 + 0.15)))

        # ── Port number silkscreen ──
        meshes.append(cbox(3, 1.5, 0.08, C_SILK, (mx, matenet_d + 3, ZS)))

        # ── Status LEDs (1G green + 100M orange) behind connector ──
        led_y = matenet_d + 5.5
        meshes.append(cbox(1.6, 0.8, 1.0, C_LED_GREEN,
                          (mx - 3.5, led_y, Z0 + 0.5)))
        meshes.append(cbox(1.6, 0.8, 1.0, C_LED_ORANGE,
                          (mx + 3.5, led_y, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 6. 4x SFP+ CAGES (front/bottom edge, right side)
    #    10GBASE-R optical/DAC
    # ════════════════════════════════════════════
    sfp_w = 14.2    # cage width
    sfp_d = 58.0    # cage depth (SFP+ module is long)
    sfp_h = 13.5    # cage height
    sfp_wall = 0.4
    sfp_spacing = 17.5
    sfp_x0 = 155.0

    for i in range(4):
        sx = sfp_x0 + i * sfp_spacing
        sy = sfp_d / 2 - 4  # extends back into board
        sz = Z0 + sfp_h / 2

        # Outer cage shell (stamped sheet metal)
        # Top
        meshes.append(cbox(sfp_w, sfp_d, sfp_wall, C_METAL, (sx, sy, sz + sfp_h/2 - sfp_wall/2)))
        # Bottom
        meshes.append(cbox(sfp_w, sfp_d, sfp_wall, C_METAL, (sx, sy, Z0 + sfp_wall/2)))
        # Left side
        meshes.append(cbox(sfp_wall, sfp_d, sfp_h, C_METAL, (sx - sfp_w/2 + sfp_wall/2, sy, sz)))
        # Right side
        meshes.append(cbox(sfp_wall, sfp_d, sfp_h, C_METAL, (sx + sfp_w/2 - sfp_wall/2, sy, sz)))
        # Back wall
        meshes.append(cbox(sfp_w, sfp_wall, sfp_h, C_METAL_DARK, (sx, sy + sfp_d/2, sz)))

        # Front bezel (thicker metal frame)
        meshes.append(cbox(sfp_w + 1, 2.0, sfp_h + 1, C_METAL, (sx, -3, sz)))
        # Port opening (dark void)
        meshes.append(cbox(sfp_w - 2, 2.5, sfp_h - 3, [15, 15, 15, 255], (sx, -3, sz)))

        # Internal guide rails (narrower than cage, clearly inside)
        meshes.append(cbox(sfp_w - 2, sfp_d - 8, 0.5, C_METAL_DARK,
                          (sx, sy, Z0 + sfp_h * 0.3)))
        meshes.append(cbox(sfp_w - 2, sfp_d - 8, 0.5, C_METAL_DARK,
                          (sx, sy, Z0 + sfp_h * 0.7)))

        # Cage ventilation slots on top (raised above cage top)
        for j in range(5):
            meshes.append(cbox(sfp_w - 4, 1.5, 0.4, [170, 175, 180, 255],
                              (sx, sy - sfp_d/4 + j * 8, sz + sfp_h/2 + 0.4)))

        # EMI spring fingers on front edge (raised above cage)
        for j in range(6):
            meshes.append(cbox(1.0, 0.3, 0.8, C_METAL_DARK,
                              (sx - sfp_w/3 + j * (sfp_w * 0.6 / 5), -2, sz + sfp_h/2 + 0.6)))

        # SFP LED (bi-color under cage)
        meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN,
                          (sx, sfp_d - 2, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 7. RJ45 MANAGEMENT PORT (rear/top edge, right)
    #    LAN8840, with integrated magnetics (ICM)
    # ════════════════════════════════════════════
    rj_w, rj_h, rj_d = 16.0, 13.5, 21.5
    rj_x = BW - 28
    rj_y = BH - rj_h/2 + 4  # overhangs rear edge

    # Metal shield
    meshes.append(cbox(rj_w, rj_h, rj_d, C_METAL, (rj_x, rj_y, Z0 + rj_d/2)))
    # Top edge band
    meshes.append(cbox(rj_w + 0.5, 0.5, rj_d, [175, 180, 185, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + rj_d/2)))
    # Port opening
    meshes.append(cbox(12, 3, 10, [15, 15, 15, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + 8)))
    # RJ45 clip slot
    meshes.append(cbox(8, 1, 2, [25, 25, 25, 255],
                      (rj_x, rj_y + rj_h/2, Z0 + 14)))
    # LEDs on RJ45 (green left, yellow right)
    meshes.append(cbox(3, 2, 3, C_LED_GREEN,
                      (rj_x - 5.5, rj_y + rj_h/2, Z0 + rj_d - 2.5)))
    meshes.append(cbox(3, 2, 3, C_LED_YELLOW,
                      (rj_x + 5.5, rj_y + rj_h/2, Z0 + rj_d - 2.5)))

    # ════════════════════════════════════════════
    # 8. USB-C SERIAL PORT (rear edge)
    # ════════════════════════════════════════════
    usbc_x = BW * 0.45
    usbc_y = BH + 1

    # USB-C receptacle body
    meshes.append(cbox(9.0, 7.5, 3.2, C_USB_METAL, (usbc_x, usbc_y, Z0 + 1.6)))
    # Opening (rounded look via stacked boxes)
    meshes.append(cbox(7.5, 2.0, 2.4, [20, 20, 22, 255], (usbc_x, BH + 4, Z0 + 1.6)))
    # Rounded ends of USB-C
    meshes.append(ccyl(1.1, 2.0, [20, 20, 22, 255], (usbc_x - 3.2, BH + 4, Z0 + 1.6), 12))
    meshes.append(ccyl(1.1, 2.0, [20, 20, 22, 255], (usbc_x + 3.2, BH + 4, Z0 + 1.6), 12))
    # USB TX/RX LEDs
    meshes.append(cbox(1.2, 0.6, 0.8, C_LED_GREEN,
                      (usbc_x - 6, BH - 3, Z0 + 0.4)))
    meshes.append(cbox(1.2, 0.6, 0.8, C_LED_GREEN,
                      (usbc_x + 6, BH - 3, Z0 + 0.4)))

    # ════════════════════════════════════════════
    # 9. 12V DC BARREL JACK (rear edge, far right)
    # ════════════════════════════════════════════
    bj_x = BW - 8
    bj_y = BH + 2
    bj_z = Z0 + 5.5

    # Barrel body (cylindrical, horizontal pointing rear)
    rot_x = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
    barrel = cylinder(radius=5.5, height=14.0, sections=24)
    barrel.apply_transform(rot_x)
    barrel.apply_translation([bj_x, bj_y + 5, bj_z])
    barrel.visual.face_colors = C_BARREL
    meshes.append(barrel)

    # Inner hole
    barrel_hole = cylinder(radius=2.5, height=12.0, sections=16)
    barrel_hole.apply_transform(rot_x)
    barrel_hole.apply_translation([bj_x, bj_y + 8, bj_z])
    barrel_hole.visual.face_colors = [15, 15, 15, 255]
    meshes.append(barrel_hole)

    # Center pin
    barrel_pin = cylinder(radius=1.0, height=8, sections=12)
    barrel_pin.apply_transform(rot_x)
    barrel_pin.apply_translation([bj_x, bj_y + 7, bj_z])
    barrel_pin.visual.face_colors = C_GOLD
    meshes.append(barrel_pin)

    # Mounting tabs
    meshes.append(cbox(12, 4, 8, C_BARREL, (bj_x, bj_y - 2, bj_z)))

    # ════════════════════════════════════════════
    # 10. POWER SWITCH (slide switch, rear)
    # ════════════════════════════════════════════
    psw_x = BW - 22
    psw_y = BH - 2

    meshes.append(cbox(10, 5, 5, C_PLASTIC_BLK, (psw_x, psw_y, Z0 + 2.5)))
    # Slider knob
    meshes.append(cbox(3.5, 2.5, 3, [200, 200, 205, 255], (psw_x + 2, psw_y, Z0 + 5.2)))

    # Power LEDs (green = OK, red = fault)
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (psw_x - 7, psw_y, Z0 + 0.5)))
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_RED, (psw_x - 10, psw_y, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 11. SMA CONNECTORS (1PPS IN/OUT, rear)
    # ════════════════════════════════════════════
    for sma_x, label in [(BW - 42, "OUT"), (BW - 54, "IN")]:
        # SMA body
        sma = cylinder(radius=3.2, height=9.5, sections=6)  # hex nut shape
        sma.apply_transform(rot_x)
        sma.apply_translation([sma_x, BH + 4, Z0 + 5])
        sma.visual.face_colors = C_SMA_GOLD
        meshes.append(sma)
        # Center conductor
        sma_pin = cylinder(radius=0.65, height=5, sections=12)
        sma_pin.apply_transform(rot_x)
        sma_pin.apply_translation([sma_x, BH + 9, Z0 + 5])
        sma_pin.visual.face_colors = C_GOLD
        meshes.append(sma_pin)
        # Insulator ring
        sma_ins = cylinder(radius=2.0, height=1.5, sections=16)
        sma_ins.apply_transform(rot_x)
        sma_ins.apply_translation([sma_x, BH + 6, Z0 + 5])
        sma_ins.visual.face_colors = [240, 240, 240, 255]  # White PTFE
        meshes.append(sma_ins)
        # Board-side flange
        meshes.append(cbox(8, 3, 8, C_PCB_TOP, (sma_x, BH - 1, Z0 + 4)))
        # Silkscreen label
        meshes.append(cbox(4, 1.5, 0.1, C_SILK, (sma_x, BH - 5, ZS)))

    # ════════════════════════════════════════════
    # 12. PCIe 2.0 OCuLink CONNECTOR (rear)
    # ════════════════════════════════════════════
    oc_x = 68
    oc_y = BH - 2

    meshes.append(cbox(26, 8, 6, C_PLASTIC_BLK, (oc_x, oc_y, Z0 + 3)))
    # Contact area
    meshes.append(cbox(22, 2, 4, [60, 60, 63, 255], (oc_x, oc_y + 4, Z0 + 3)))
    # Latch
    meshes.append(cbox(6, 1, 2, C_METAL_DARK, (oc_x, oc_y + 5, Z0 + 6)))

    # ════════════════════════════════════════════
    # 13. RESET BUTTON (rear area)
    # ════════════════════════════════════════════
    rst_x = BW * 0.55
    rst_y = BH - 5

    # Button base
    meshes.append(cbox(4.5, 4.5, 2.5, C_PLASTIC_BLK, (rst_x, rst_y, Z0 + 1.25)))
    # Button cap (red)
    meshes.append(ccyl(1.5, 2, C_LED_RED, (rst_x, rst_y, Z0 + 3.2), 16))

    # ════════════════════════════════════════════
    # 14. DIP SWITCH (4-pin, boot mode)
    # ════════════════════════════════════════════
    dip_x = 48
    dip_y = BH - 38

    # DIP body
    meshes.append(cbox(11, 5.2, 3.5, C_RED_SW, (dip_x, dip_y, Z0 + 1.75)))
    # Individual rockers
    for i in range(4):
        meshes.append(cbox(1.8, 2.0, 1.5, [230, 230, 235, 255],
                          (dip_x - 4 + i * 2.54, dip_y, Z0 + 3.6)))
    # Label
    meshes.append(cbox(8, 1, 0.1, C_SILK, (dip_x, dip_y - 4, ZS)))

    # ════════════════════════════════════════════
    # 15. EXPANSION HEADER (2x20, RPi compatible)
    # ════════════════════════════════════════════
    exp_x = BW - 52
    exp_y = BH - 48

    # Plastic housing
    meshes.append(cbox(51, 5.1, 8.5, C_PLASTIC_BLK, (exp_x, exp_y, Z0 + 4.25)))
    # Gold pins
    for i in range(20):
        for j in range(2):
            meshes.append(cbox(0.5, 0.5, 11, C_GOLD,
                              (exp_x - 24 + i * 2.54, exp_y - 1.27 + j * 2.54, Z0 + 8)))

    # ════════════════════════════════════════════
    # 16. JTAG HEADER (10-pin, 0.05" pitch)
    # ════════════════════════════════════════════
    jtag_x = BW - 25
    jtag_y = BH - 62

    meshes.append(cbox(13.5, 5.1, 6, C_PLASTIC_BLK, (jtag_x, jtag_y, Z0 + 3)))
    for i in range(5):
        for j in range(2):
            meshes.append(cbox(0.4, 0.4, 8, C_GOLD,
                              (jtag_x - 5 + i * 2.54, jtag_y - 1.27 + j * 2.54, Z0 + 6)))

    # ════════════════════════════════════════════
    # 17. LAN8870 PHY CHIPS (7x, QFN packages)
    # ════════════════════════════════════════════
    for i in range(7):
        px = matenet_x0 + i * matenet_spacing
        py = 32

        # QFN package
        meshes.append(cbox(7, 7, 0.9, C_IC, (px, py, Z0 + 0.45)))
        # Pin-1 mark (raised well above IC)
        meshes.append(ccyl(0.4, 0.2, C_SILK, (px - 2.8, py + 2.8, Z0 + 1.0), 12))

    # ════════════════════════════════════════════
    # 18. LAN8840 PHY (management port, QFN)
    # ════════════════════════════════════════════
    meshes.append(cbox(6, 6, 0.9, C_IC, (BW - 30, BH - 22, Z0 + 0.45)))
    meshes.append(ccyl(0.35, 0.06, C_SILK, (BW - 33, BH - 19, Z0 + 0.93), 12))

    # ════════════════════════════════════════════
    # 19. MEMORY: QSPI NOR Flash (8MB) + eMMC NAND (4GB)
    # ════════════════════════════════════════════
    # NOR Flash (SOIC-8 or similar)
    meshes.append(cbox(5, 4, 1.2, C_IC, (cx - 22, cy + 12, Z0 + 0.6)))
    meshes.append(cbox(3.5, 2.5, 0.15, C_IC_MARK, (cx - 22, cy + 12, Z0 + 1.3)))

    # eMMC NAND footprint (not populated on this board variant)
    # Just show empty pads
    meshes.append(cbox(11, 15, 0.15, C_COPPER, (cx - 24, cy - 3, Z0 + 0.12)))

    # ════════════════════════════════════════════
    # 20. CLOCK OSCILLATORS
    # ════════════════════════════════════════════
    # 156.25 MHz (SerDes ref clock)
    meshes.append(cbox(5, 3.2, 1.5, C_METAL, (cx + 22, cy + 12, Z0 + 0.75)))
    meshes.append(cbox(3.5, 1.5, 0.15, [220, 220, 225, 255], (cx + 22, cy + 12, Z0 + 1.6)))

    # 25 MHz (PHY ref clock)
    meshes.append(cbox(5, 3.2, 1.5, C_METAL, (cx + 22, cy - 10, Z0 + 0.75)))
    meshes.append(cbox(3.5, 1.5, 0.15, [220, 220, 225, 255], (cx + 22, cy - 10, Z0 + 1.6)))

    # ════════════════════════════════════════════
    # 21. DC/DC CONVERTERS & INDUCTORS
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
        # Ferrite top marking
        meshes.append(cbox(iw - 1, ih - 1, 0.2, [70, 70, 73, 255], (ix, iy, Z0 + id_ + 0.15)))

    # DC/DC converter ICs (near inductors)
    dcdc_pos = [(25, BH - 21), (45, BH - 21), (58, BH - 21)]
    for dx, dy in dcdc_pos:
        meshes.append(cbox(5, 4, 0.9, C_IC, (dx, dy, Z0 + 0.45)))

    # ════════════════════════════════════════════
    # 22. CAPACITORS (MLCCs, distributed)
    # ════════════════════════════════════════════
    np.random.seed(42)
    cap_positions = []
    for _ in range(60):
        cx_ = np.random.uniform(12, BW - 12)
        cy_ = np.random.uniform(20, BH - 8)
        # Avoid main IC, connectors, other components
        if abs(cx_ - cx) < 14 and abs(cy_ - cy) < 14:
            continue
        if cy_ < 15 and cx_ < 150:  # MATEnet area
            continue
        if cy_ < sfp_d and cx_ > 148:  # SFP area
            continue
        cap_positions.append((cx_, cy_))

    for cx_, cy_ in cap_positions[:45]:
        size = np.random.choice([0.6, 1.0, 1.6, 2.0])
        h = size * 0.5
        color = C_CAP_BROWN if np.random.random() > 0.3 else C_CAP_GRAY
        meshes.append(cbox(size, size * 0.6, h, color, (cx_, cy_, Z0 + h/2)))

    # Larger electrolytic / tantalum caps near power
    for ex, ey in [(12, BH - 8), (BW - 15, BH - 15), (85, BH - 10)]:
        meshes.append(cbox(3.5, 3, 2.5, [40, 35, 30, 255], (ex, ey, Z0 + 1.25)))
        # Polarity marking
        meshes.append(cbox(3.5, 0.5, 2.5, [180, 160, 100, 255], (ex, ey + 1.5, Z0 + 1.25)))

    # ════════════════════════════════════════════
    # 23. RESISTOR ARRAYS & SMALL ICs
    # ════════════════════════════════════════════
    for rx, ry in [(cx + 12, cy + 20), (cx - 12, cy + 20),
                    (cx + 15, cy - 18), (cx - 15, cy - 15)]:
        meshes.append(cbox(3.2, 1.6, 0.6, C_IC, (rx, ry, Z0 + 0.3)))

    # ZL40241 Clock buffer
    meshes.append(cbox(5, 5, 0.9, C_IC, (cx + 30, cy - 2, Z0 + 0.45)))

    # MCP2200 UART-to-USB
    meshes.append(cbox(5, 5, 0.9, C_IC, (usbc_x, BH - 12, Z0 + 0.45)))

    # ════════════════════════════════════════════
    # 24. POWER STATUS LEDs (5x green, near power area)
    # ════════════════════════════════════════════
    for i, label in enumerate(["0.9V", "1.1V", "1.8V", "3.3V", "5V"]):
        lx = BW - 50 + i * 6
        ly = BH - 10
        meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (lx, ly, Z0 + 0.5)))
        meshes.append(cbox(3, 1, 0.1, C_SILK, (lx, ly - 2, ZS)))

    # Board status LEDs (green + yellow)
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_GREEN, (rst_x - 8, rst_y, Z0 + 0.5)))
    meshes.append(cbox(1.5, 0.8, 1.0, C_LED_YELLOW, (rst_x - 11, rst_y, Z0 + 0.5)))

    # ════════════════════════════════════════════
    # 25. SILKSCREEN DETAILS (decorative)
    # ════════════════════════════════════════════
    # Component outlines near chips
    for i in range(7):
        px = matenet_x0 + i * matenet_spacing
        meshes.append(cbox(8, 0.15, 0.1, C_SILK, (px, 28, ZS)))
        meshes.append(cbox(8, 0.15, 0.1, C_SILK, (px, 36, ZS)))

    # Board outline marking
    meshes.append(cbox(BW - 20, 0.2, 0.1, C_SILK, (BW/2, 12, ZS)))
    meshes.append(cbox(0.2, 30, 0.1, C_SILK, (10, BH/2, ZS)))

    # Test points (scattered copper dots)
    tp_positions = [(30, 50), (55, 65), (80, 45), (100, 90), (130, 70),
                    (150, 100), (170, 85), (100, 120), (130, 115)]
    for tx, ty in tp_positions:
        meshes.append(ccyl(0.8, 0.2, C_COPPER, (tx, ty, Z0 + 0.3), 12))

    # ════════════════════════════════════════════
    # 26. GROUND SHIELD / COPPER POUR (under SFP area)
    # ════════════════════════════════════════════
    meshes.append(cbox(70, 45, 0.2, [0, 80, 32, 180],
                      (BW - 42, 32, Z0 + 0.25)))

    return meshes


def main():
    print("Building EVB-LAN9692-LM 3D model v3 (Y-up fix)...")
    meshes = build_board()
    print(f"  Total mesh parts: {len(meshes)}")

    # ── Convert Z-up (trimesh) → Y-up (GLTF/GLB standard) ──
    # Rotate -90° around X axis: (x, y, z) → (x, z, -y)
    # This makes:
    #   Board XY plane → XZ plane (horizontal in GLTF)
    #   Z (up) → Y (up in GLTF)
    #   Y=0 (front/MATEnet edge) → Z=0
    #   Y=150 (rear/RJ45 edge) → Z=-150
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
    print("  Done!")


if __name__ == "__main__":
    main()
