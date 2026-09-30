#!/usr/bin/env python3
"""Convierte hardware/<VAR>/board_geometry.json en enclosure/gen/board_<VAR>.scad."""
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(root, 'enclosure', 'gen'), exist_ok=True)
for var in ('SMA', 'BNC'):
    g = json.load(open(os.path.join(root, 'hardware', var, 'board_geometry.json')))
    conn = ', '.join(f'["{c["ref"]}", {c["x"]:.3f}, {c["y"]:.3f}, "{c["side"]}", "{c["label"]}"]'
                     for c in g['connectors'])
    holes = ', '.join(f'[{x:.3f}, {y:.3f}]' for x, y in g['holes'])
    with open(os.path.join(root, 'enclosure', 'gen', f'board_{var}.scad'), 'w') as f:
        f.write(f'// GENERADO por scripts/gen_enclosure_inc.py - no editar a mano\n'
                f'{var}_BOARD = [{g["board"][0]}, {g["board"][1]}];\n'
                f'{var}_HOLES = [{holes}];\n'
                f'{var}_CONN  = [{conn}];   // [ref, x, y(KiCad), lado, etiqueta]\n')
    print('ok', var)
