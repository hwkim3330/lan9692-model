#!/usr/bin/env python3
"""
EVB-LAN9692-LM 3D Board Model Generator
Generates a GLB model based on the Hardware User's Guide (DS50003848B)
Board: 214 x 150 mm, 4-layer PCB, 1.535mm thick
"""

import trimesh
import numpy as np

def create_box(width, height, depth, color, position=(0, 0, 0)):
    """Create a colored box at position (center-based)"""
    mesh = trimesh.creation.box(extents=[width, height, depth])
    mesh.apply_translation(position)
    mesh.visual.face_colors = color
    return mesh

def create_cylinder(radius, height, color, position=(0, 0, 0), sections=32):
    """Create a colored cylinder at position"""
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation(position)
    mesh.visual.face_colors = color
    return mesh

def create_mounting_hole(radius, height, position):
    """Create a mounting hole ring"""
    outer = trimesh.creation.cylinder(radius=radius + 0.8, height=height + 0.1, sections=32)
    inner = trimesh.creation.cylinder(radius=radius, height=height + 0.5, sections=32)
    ring = outer.difference(inner) if hasattr(outer, 'difference') else outer
    ring.apply_translation(position)
    ring.visual.face_colors = [192, 192, 192, 255]  # Silver
    return ring

def build_board():
    meshes = []

    # === Board dimensions (mm) ===
    BW = 214.0   # width (X)
    BH = 150.0   # height (Y)
    BT = 1.535    # thickness (Z)

    # PCB base - green
    pcb = create_box(BW, BH, BT, [0, 100, 0, 255], position=(BW/2, BH/2, 0))
    meshes.append(pcb)

    # PCB top copper layer hint (slightly darker green)
    pcb_top = create_box(BW - 1, BH - 1, 0.05, [0, 80, 0, 255], position=(BW/2, BH/2, BT/2 + 0.025))
    meshes.append(pcb_top)

    # Silkscreen area (white text area - Microchip logo region)
    silk = create_box(35, 12, 0.05, [255, 255, 255, 200], position=(35, BH - 20, BT/2 + 0.06))
    meshes.append(silk)

    # === Mounting holes (4 corners) ===
    hole_r = 1.6
    hole_offset = 5.0
    hole_positions = [
        (hole_offset, hole_offset, 0),
        (BW - hole_offset, hole_offset, 0),
        (hole_offset, BH - hole_offset, 0),
        (BW - hole_offset, BH - hole_offset, 0),
    ]
    for pos in hole_positions:
        pad = create_cylinder(3.0, BT + 0.1, [192, 192, 192, 255], pos)
        meshes.append(pad)
        hole = create_cylinder(hole_r, BT + 0.3, [40, 40, 40, 255], pos)
        meshes.append(hole)

    # === LAN9692 Main IC (FCBGA 17x17mm, center of board) ===
    chip_x = BW * 0.42
    chip_y = BH * 0.55
    chip_z = BT/2 + 1.0
    # BGA package
    lan9692 = create_box(17, 17, 2.0, [30, 30, 30, 255], position=(chip_x, chip_y, chip_z))
    meshes.append(lan9692)
    # Chip top marking
    chip_label = create_box(12, 12, 0.05, [60, 60, 60, 255], position=(chip_x, chip_y, chip_z + 1.025))
    meshes.append(chip_label)
    # Die dot
    chip_dot = create_cylinder(0.8, 0.1, [255, 255, 255, 200], (chip_x - 5, chip_y + 5, chip_z + 1.06))
    meshes.append(chip_dot)

    # === 7x MATEnet connectors (front bottom edge, left 2/3) ===
    # MATEnet (1000BASE-T1) - automotive single-pair connectors
    matenet_w = 14.0
    matenet_h = 12.0
    matenet_d = 10.0
    matenet_spacing = 20.5
    matenet_start_x = 18.0
    matenet_y = -matenet_h/2 + 2  # overhanging front edge

    for i in range(7):
        x = matenet_start_x + i * matenet_spacing
        z = BT/2 + matenet_d/2
        # Connector housing (dark gray plastic)
        conn = create_box(matenet_w, matenet_h, matenet_d, [50, 50, 50, 255],
                         position=(x, matenet_y, z))
        meshes.append(conn)
        # Metal shell top
        shell = create_box(matenet_w + 0.5, 0.3, matenet_d, [180, 180, 180, 255],
                          position=(x, matenet_y + matenet_h/2, z))
        meshes.append(shell)
        # Port opening
        opening = create_box(matenet_w - 4, 2, matenet_d - 3, [20, 20, 20, 255],
                            position=(x, matenet_y - matenet_h/2 + 1, z))
        meshes.append(opening)
        # Status LEDs behind each connector (green + orange)
        led_z = BT/2 + 1.0
        led_g = create_box(1.5, 1.0, 1.5, [0, 255, 0, 200],
                          position=(x - 3, matenet_y + matenet_h/2 + 3, led_z))
        meshes.append(led_g)
        led_o = create_box(1.5, 1.0, 1.5, [255, 165, 0, 200],
                          position=(x + 3, matenet_y + matenet_h/2 + 3, led_z))
        meshes.append(led_o)

    # === 4x SFP+ cages (front bottom edge, right 1/3) ===
    sfp_w = 14.5
    sfp_h = 14.0
    sfp_d = 56.0  # SFP+ cages are deep
    sfp_spacing = 18.5
    sfp_start_x = 162.0

    for i in range(4):
        x = sfp_start_x + i * sfp_spacing
        z = BT/2 + sfp_d/2
        # SFP+ metal cage
        cage = create_box(sfp_w, sfp_h, sfp_d, [190, 190, 190, 255],
                         position=(x, -sfp_h/2 + 2, z - 15))
        meshes.append(cage)
        # Cage opening (front)
        cage_open = create_box(sfp_w - 2, sfp_h - 2, 3, [40, 40, 40, 255],
                              position=(x, -sfp_h/2 + 1, -sfp_h/2 + 5))
        meshes.append(cage_open)
        # Cage top detail lines
        for j in range(3):
            line = create_box(sfp_w - 1, 0.3, 0.3, [160, 160, 160, 255],
                             position=(x, -sfp_h/2 + 2 + sfp_h/2, z - 15 + j * 8))
            meshes.append(line)
        # SFP LED (bi-color)
        led = create_box(1.5, 1.0, 1.5, [0, 255, 0, 200],
                        position=(x, sfp_h/2 + 4, BT/2 + 1.0))
        meshes.append(led)

    # === RJ45 Management Port (rear side, right area) ===
    rj45_w = 16.0
    rj45_h = 13.5
    rj45_d = 22.0
    rj45_x = BW - 30
    rj45_y = BH + rj45_h/2 - 3
    rj45_z = BT/2 + rj45_d/2

    # RJ45 metal shield
    rj45 = create_box(rj45_w, rj45_h, rj45_d, [190, 190, 190, 255],
                     position=(rj45_x, rj45_y, rj45_z))
    meshes.append(rj45)
    # RJ45 port opening
    rj45_open = create_box(rj45_w - 4, 4, rj45_d - 6, [20, 20, 20, 255],
                          position=(rj45_x, rj45_y + rj45_h/2, rj45_z - 3))
    meshes.append(rj45_open)
    # RJ45 LEDs (green + yellow)
    rj45_led1 = create_box(2.5, 2.5, 2.5, [0, 255, 0, 180],
                          position=(rj45_x - 6, rj45_y + rj45_h/2, rj45_z + rj45_d/2 - 3))
    meshes.append(rj45_led1)
    rj45_led2 = create_box(2.5, 2.5, 2.5, [255, 255, 0, 180],
                          position=(rj45_x + 6, rj45_y + rj45_h/2, rj45_z + rj45_d/2 - 3))
    meshes.append(rj45_led2)

    # === USB-C connector (rear side) ===
    usbc_w = 9.0
    usbc_h = 7.5
    usbc_d = 3.2
    usbc_x = BW - 65
    usbc_y = BH + usbc_h/2 - 2
    usbc_z = BT/2 + usbc_d/2

    usbc = create_box(usbc_w, usbc_h, usbc_d, [190, 190, 190, 255],
                     position=(usbc_x, usbc_y, usbc_z))
    meshes.append(usbc)
    # USB-C opening
    usbc_open = create_box(usbc_w - 2, 2, usbc_d - 0.5, [30, 30, 30, 255],
                          position=(usbc_x, usbc_y + usbc_h/2, usbc_z))
    meshes.append(usbc_open)

    # === 12V DC Barrel Jack (rear side, right) ===
    jack_r = 5.5
    jack_h = 14.0
    jack_x = BW - 10
    jack_y = BH + 4
    jack_z = BT/2 + jack_r

    jack_body = create_cylinder(jack_r, jack_h, [30, 30, 30, 255],
                               position=(jack_x, jack_y, jack_z))
    # Rotate to point outward (along Y)
    rot = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
    jack_body.apply_transform(rot)
    jack_body.apply_translation([jack_x, jack_y, jack_z])
    meshes.append(jack_body)

    # Jack metal ring
    jack_ring = create_cylinder(jack_r + 0.5, 2, [180, 180, 180, 255])
    jack_ring.apply_transform(rot)
    jack_ring.apply_translation([jack_x, jack_y + jack_h/2, jack_z])
    meshes.append(jack_ring)

    # === Power Switch (rear side) ===
    sw_x = BW - 18
    sw_y = BH + 2
    sw_z = BT/2 + 3
    pwr_sw = create_box(8, 4, 6, [200, 50, 50, 255], position=(sw_x, sw_y, sw_z))
    meshes.append(pwr_sw)
    # Switch toggle
    toggle = create_box(3, 2, 3, [60, 60, 60, 255], position=(sw_x + 1, sw_y + 2.5, sw_z + 1))
    meshes.append(toggle)

    # === 2x SMA connectors (rear side, for 1PPS) ===
    for i, offset_x in enumerate([BW - 45, BW - 55]):
        sma_body = create_cylinder(3.2, 8, [218, 165, 32, 255])  # Gold
        sma_rot = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
        sma_body.apply_transform(sma_rot)
        sma_body.apply_translation([offset_x, BH + 4, BT/2 + 5])
        meshes.append(sma_body)
        # SMA center pin
        sma_pin = create_cylinder(0.6, 4, [255, 215, 0, 255])
        sma_pin.apply_transform(sma_rot)
        sma_pin.apply_translation([offset_x, BH + 8, BT/2 + 5])
        meshes.append(sma_pin)

    # === PCIe OCuLink connector (rear side) ===
    oculink = create_box(22, 8, 5, [40, 40, 40, 255],
                        position=(70, BH + 2, BT/2 + 2.5))
    meshes.append(oculink)
    # Connector face
    oculink_face = create_box(18, 2, 3, [80, 80, 80, 255],
                             position=(70, BH + 5, BT/2 + 2.5))
    meshes.append(oculink_face)

    # === Reset Button (rear side) ===
    reset_btn = create_box(4, 4, 3, [200, 200, 200, 255],
                          position=(BW - 80, BH + 1, BT/2 + 1.5))
    meshes.append(reset_btn)
    reset_cap = create_cylinder(1.5, 2, [255, 50, 50, 255],
                               position=(BW - 80, BH + 1, BT/2 + 3.5))
    meshes.append(reset_cap)

    # === DIP Switch (boot mode, 4-pin) ===
    dip = create_box(10, 5, 4, [255, 50, 50, 255],
                    position=(45, BH - 35, BT/2 + 2))
    meshes.append(dip)
    # DIP individual switches
    for i in range(4):
        sw = create_box(1.5, 2, 1.5, [255, 255, 255, 255],
                       position=(42 + i * 2.2, BH - 35, BT/2 + 4.2))
        meshes.append(sw)

    # === Expansion Header (RPi compatible, right side) ===
    exp_w = 52.0
    exp_h = 5.0
    exp_d = 8.5
    exp = create_box(exp_w, exp_h, exp_d, [30, 30, 30, 255],
                    position=(BW - 50, BH - 45, BT/2 + exp_d/2))
    meshes.append(exp)
    # Header pins (gold)
    for i in range(20):
        for j in range(2):
            pin = create_box(0.6, 0.6, 8.5, [218, 165, 32, 255],
                            position=(BW - 74 + i * 2.54, BH - 46 + j * 2.54, BT/2 + exp_d/2))
            meshes.append(pin)

    # === JTAG Header (10-pin) ===
    jtag = create_box(13, 5, 8, [30, 30, 30, 255],
                     position=(BW - 30, BH - 55, BT/2 + 4))
    meshes.append(jtag)

    # === LAN8870 PHY chips (7x, one per T1 port) ===
    for i in range(7):
        x = 18.0 + i * 20.5
        y = 35
        phy = create_box(8, 8, 1.2, [30, 30, 30, 255],
                        position=(x, y, BT/2 + 0.6))
        meshes.append(phy)

    # === LAN8840 PHY chip (management port) ===
    lan8840 = create_box(7, 7, 1.0, [30, 30, 30, 255],
                        position=(BW - 30, BH - 25, BT/2 + 0.5))
    meshes.append(lan8840)

    # === DC/DC converters and inductors ===
    # Large inductors
    inductor_positions = [
        (20, BH - 15), (40, BH - 15), (60, BH - 15),
        (20, BH - 30), (40, BH - 30),
    ]
    for (ix, iy) in inductor_positions:
        ind = create_box(6, 6, 3, [50, 50, 50, 255],
                        position=(ix, iy, BT/2 + 1.5))
        meshes.append(ind)

    # === Capacitors and small SMD components (decorative) ===
    np.random.seed(42)
    for _ in range(40):
        cx = np.random.uniform(15, BW - 15)
        cy = np.random.uniform(25, BH - 10)
        # Avoid main chip area
        if abs(cx - chip_x) < 15 and abs(cy - chip_y) < 15:
            continue
        cw = np.random.uniform(1.0, 2.5)
        ch = np.random.uniform(0.8, 1.5)
        cap = create_box(cw, ch, 0.8, [80, 60, 40, 255],
                        position=(cx, cy, BT/2 + 0.4))
        meshes.append(cap)

    # === Crystal oscillators ===
    # 156.25 MHz osc
    osc1 = create_box(5, 3.2, 1.5, [190, 190, 190, 255],
                     position=(chip_x + 20, chip_y + 10, BT/2 + 0.75))
    meshes.append(osc1)
    # 25 MHz osc
    osc2 = create_box(5, 3.2, 1.5, [190, 190, 190, 255],
                     position=(chip_x + 20, chip_y - 10, BT/2 + 0.75))
    meshes.append(osc2)

    # === QSPI NOR Flash (8MB) ===
    nor_flash = create_box(6, 5, 1.2, [30, 30, 30, 255],
                          position=(chip_x - 25, chip_y + 10, BT/2 + 0.6))
    meshes.append(nor_flash)

    # === eMMC NAND (4GB) ===
    emmc = create_box(12, 16, 1.4, [30, 30, 30, 255],
                     position=(chip_x - 25, chip_y - 5, BT/2 + 0.7))
    meshes.append(emmc)

    # === Power status LEDs (rear side, near power switch) ===
    led_colors = [
        [0, 255, 0, 200],    # 5V green
        [0, 255, 0, 200],    # 3.3V green
        [0, 255, 0, 200],    # 1.8V green
        [0, 255, 0, 200],    # 1.1V green
        [0, 255, 0, 200],    # 0.9V green
    ]
    for i, color in enumerate(led_colors):
        led = create_box(1.5, 0.8, 1.0, color,
                        position=(BW - 25 + i * 4, BH - 10, BT/2 + 0.5))
        meshes.append(led)

    # === Board status LEDs ===
    status_led1 = create_box(1.5, 0.8, 1.0, [0, 255, 0, 200],
                            position=(BW - 85, BH - 5, BT/2 + 0.5))
    meshes.append(status_led1)
    status_led2 = create_box(1.5, 0.8, 1.0, [255, 255, 0, 200],
                            position=(BW - 88, BH - 5, BT/2 + 0.5))
    meshes.append(status_led2)

    # === Ground shield (copper area under SFP+) ===
    shield = create_box(75, 50, 0.1, [180, 160, 100, 100],
                       position=(BW - 45, 30, BT/2 + 0.06))
    meshes.append(shield)

    return meshes


def main():
    print("Building EVB-LAN9692-LM 3D model...")
    meshes = build_board()

    print(f"  Total meshes: {len(meshes)}")

    # Combine all meshes
    scene = trimesh.Scene()
    for i, mesh in enumerate(meshes):
        scene.add_geometry(mesh, node_name=f"part_{i:03d}")

    # Export as GLB
    output_path = "/home/kim/EVB-LAN9692-LM.glb"
    scene.export(output_path, file_type='glb')
    print(f"  Exported to: {output_path}")

    # Also export as GLTF for inspection
    gltf_path = "/home/kim/EVB-LAN9692-LM.gltf"
    scene.export(gltf_path, file_type='gltf')
    print(f"  Exported to: {gltf_path}")

    # Print board summary
    print("\n=== EVB-LAN9692-LM Board Summary ===")
    print("  Dimensions: 214 x 150 x 1.535 mm")
    print("  Main IC: LAN9692 (356-ball FCBGA, 17x17mm)")
    print("  Front ports: 7x MATEnet (1000BASE-T1) + 4x SFP+ (10G)")
    print("  Rear: RJ45, USB-C, DC jack, OCuLink, 2x SMA, Reset")
    print("  Done!")


if __name__ == "__main__":
    main()
