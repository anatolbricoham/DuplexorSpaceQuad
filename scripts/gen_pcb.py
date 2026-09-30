#!/usr/bin/env python3
"""Genera la PCB del diplexor 2m/70cm (KiCad 7) en variante SMA o BNC.

Uso: python3 scripts/gen_pcb.py SMA|BNC <carpeta_salida>
Requiere KiCad 7 (modulo pcbnew) y KICAD7_FOOTPRINT_DIR apuntando a las huellas oficiales.
"""
import sys, os, math, pcbnew
from pcbnew import FromMM as MM, VECTOR2I

VAR = sys.argv[1]            # 'SMA' | 'BNC'
OUT = sys.argv[2]
LIB = os.environ.get('KICAD7_FOOTPRINT_DIR', '/usr/share/kicad/footprints').rstrip('/') + '/'
os.makedirs(OUT, exist_ok=True)
name = f'diplexor_2m70cm_{VAR}'
pcb_path = os.path.join(OUT, name + '.kicad_pcb')

W_RF = 1.40      # ancho pista 50 ohm (CPWG, FR4 1.6 mm, gap 0.25)
GAP = 0.25
ORG = (100.0, 100.0)  # origen en el lienzo de KiCad

def P(x, y): return VECTOR2I(MM(ORG[0] + x), MM(ORG[1] + y))

board = pcbnew.NewBoard(pcb_path)
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(MM(1.6))
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(MM(0.2)); nc.SetTrackWidth(MM(W_RF))
nc.SetViaDiameter(MM(0.8)); nc.SetViaDrill(MM(0.4))
ds.m_MinClearance = MM(0.15); ds.m_TrackMinWidth = MM(0.2)
ds.m_ViasMinSize = MM(0.6); ds.m_MinThroughDrill = MM(0.3)
ds.m_CopperEdgeClearance = MM(0.3)

nets = {}
def net(n):
    if n not in nets:
        ni = pcbnew.NETINFO_ITEM(board, n); board.Add(ni); nets[n] = ni
    return nets[n]
for n in ['GND', 'RADIO', 'N1', 'N2', 'OUT_2M', 'N3', 'N4', 'OUT_70CM']: net(n)

def place(lib, fpname, ref, value, x, y, rot, padnets):
    fp = pcbnew.FootprintLoad(LIB + lib + '.pretty', fpname)
    fp.SetReference(ref); fp.SetValue(value)
    fp.SetPosition(P(x, y)); fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        n = padnets.get(p.GetNumber())
        if n: p.SetNet(net(n))
    fp.SetFPID(pcbnew.LIB_ID(lib, fpname))
    if ref[0] in 'HJ': fp.Reference().SetVisible(False)
    board.Add(fp)
    return fp

def pad_pos(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == num:
            v = p.GetPosition(); return (pcbnew.ToMM(v.x) - ORG[0], pcbnew.ToMM(v.y) - ORG[1])

tracks = []
def track(pts, n, w=W_RF, layer=pcbnew.F_Cu):
    for a, b in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(P(*a)); t.SetEnd(P(*b)); t.SetWidth(MM(w))
        t.SetLayer(layer); t.SetNet(net(n)); board.Add(t)
        tracks.append((a, b, w))

vias = []
def via(x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(P(x, y)); v.SetWidth(MM(0.8)); v.SetDrill(MM(0.4))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(net('GND')); board.Add(v)
    vias.append((x, y))

# ---------------------------------------------------------------- geometria
if VAR == 'SMA':
    BW, BH = 37.0, 23.0
    yT, yB = 5.5, 17.5
    x0 = 9.4                          # primer componente
    jx = 6.4                          # nodo de union comun
    J = dict(lib='Connector_Coaxial', fp='SMA_Amphenol_132289_EdgeMount',
             val='SMA edge 1.6mm (Amphenol 132289)')
    j1 = (2.54, (yT + yB) / 2, 180)
    j2 = (BW - 2.54, yT, 0)
    j3 = (BW - 2.54, yB, 0)
    holes = [(x0 + 5.0, (yT + yB) / 2), (x0 + 15.0, (yT + yB) / 2)]
else:
    BW, BH = 55.5, 33.0
    yT, yB = 8.0, 25.0
    x0 = 17.8
    jx = 15.4
    J = dict(lib='Connector_Coaxial', fp='BNC_Amphenol_B6252HB-NPP3G-50_Horizontal',
             val='BNC R/A PCB (Amphenol B6252HB-NPP3G-50)')
    j1 = (12.7, (yT + yB) / 2, 90)
    j2 = (BW - 12.7, yT, 270)
    j3 = (BW - 12.7, yB, 270)
    holes = [(x0 + 5.0, (yT + yB) / 2), (x0 + 15.0, (yT + yB) / 2)]

J1 = place(J['lib'], J['fp'], 'J1', J['val'], *j1, {'1': 'RADIO', '2': 'GND'})
J2 = place(J['lib'], J['fp'], 'J2', J['val'], *j2, {'1': 'OUT_2M', '2': 'GND'})
J3 = place(J['lib'], J['fp'], 'J3', J['val'], *j3, {'1': 'OUT_70CM', '2': 'GND'})

CFP = ('Capacitor_SMD', 'C_0805_2012Metric_Pad1.18x1.45mm_HandSolder')
LFP = ('Inductor_SMD', 'L_0805_2012Metric_Pad1.15x1.40mm_HandSolder')
PITCH = 5.0
xs = [x0 + i * PITCH for i in range(5)]
# rama 2 m (paso bajo)  -- shunt hacia arriba (lejos de la otra rama)
L1 = place(*LFP, 'L1', '68nH',  xs[0], yT, 0, {'1': 'RADIO', '2': 'N1'})
C1 = place(*CFP, 'C1', '18pF',  xs[1], yT - 1.04, 90, {'1': 'N1', '2': 'GND'})
L2 = place(*LFP, 'L2', '100nH', xs[2], yT, 0, {'1': 'N1', '2': 'N2'})
C2 = place(*CFP, 'C2', '18pF',  xs[3], yT - 1.04, 90, {'1': 'N2', '2': 'GND'})
L3 = place(*LFP, 'L3', '68nH',  xs[4], yT, 0, {'1': 'N2', '2': 'OUT_2M'})
# rama 70 cm (paso alto) -- shunt hacia abajo
C3 = place(*CFP, 'C3', '4.7pF', xs[0], yB, 0, {'1': 'RADIO', '2': 'N3'})
L4 = place(*LFP, 'L4', '15nH',  xs[1], yB + 1.02, 270, {'1': 'N3', '2': 'GND'})
C4 = place(*CFP, 'C4', '2.7pF', xs[2], yB, 0, {'1': 'N3', '2': 'N4'})
L5 = place(*LFP, 'L5', '15nH',  xs[3], yB + 1.02, 270, {'1': 'N4', '2': 'GND'})
C5 = place(*CFP, 'C5', '4.7pF', xs[4], yB, 0, {'1': 'N4', '2': 'OUT_70CM'})

for i, (hx, hy) in enumerate(holes):
    place('MountingHole', 'MountingHole_2.2mm_M2_Pad_Via', f'H{i+1}', 'M2', hx, hy, 0, {'1': 'GND'})

if VAR == 'SMA':
    for fp in (J1, J2, J3):
        for p in fp.Pads():
            sz = p.GetSize()                      # local: 1.5 x 5.08 rotado 90
            p.SetSize(VECTOR2I(sz.x, sz.y - MM(0.35)))
            off = p.GetOffset()
            # desplazar hacia dentro de la placa (local -x en el footprint)
            p.SetOffset(VECTOR2I(off.x, off.y))
            lp = p.GetPos0() if hasattr(p, 'GetPos0') else None
    # desplazamos el pad en coordenadas de placa
    for fp, sgn in ((J1, 1), (J2, -1), (J3, -1)):
        for p in fp.Pads():
            v = p.GetPosition(); p.SetPosition(VECTOR2I(v.x + sgn * MM(0.175), v.y))
_rm = []
for fp in (J1, J2, J3):
    items = [g for g in fp.GraphicalItems()]
    for g in items:
        if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            bb = g.GetBoundingBox()
            if VAR == 'SMA' or pcbnew.ToMM(bb.GetLeft()) - ORG[0] < 0.3 or pcbnew.ToMM(bb.GetRight()) - ORG[0] > BW - 0.3:
                _rm.append((fp, g))
for fp, g in _rm:
    fp.Remove(g)

# ---------------------------------------------------------------- pistas RF
j1p = pad_pos(J1, '1'); ym = j1p[1]
track([j1p, (jx, ym)], 'RADIO')
track([(jx, ym), (jx, yT), pad_pos(L1, '1')], 'RADIO')
track([(jx, ym), (jx, yB), pad_pos(C3, '1')], 'RADIO')
chainT = [(L1, 'N1', C1, L2), (L2, 'N2', C2, L3)]
track([pad_pos(L1, '2'), pad_pos(C1, '1'), pad_pos(L2, '1')], 'N1')
track([pad_pos(L2, '2'), pad_pos(C2, '1'), pad_pos(L3, '1')], 'N2')
track([pad_pos(L3, '2'), pad_pos(J2, '1')], 'OUT_2M')
track([pad_pos(C3, '2'), pad_pos(L4, '1'), pad_pos(C4, '1')], 'N3')
track([pad_pos(C4, '2'), pad_pos(L5, '1'), pad_pos(C5, '1')], 'N4')
track([pad_pos(C5, '2'), pad_pos(J3, '1')], 'OUT_70CM')

# vias de masa junto a cada componente a masa (2 por pad)
for fp in (C1, C2, L4, L5):
    gx, gy = pad_pos(fp, '2')
    s = -1 if gy < yT + 1 else 1  # hacia fuera de la pista
    for dx in (-0.9, 0.9):
        via(gx + dx, gy + s * 1.35)

# ---------------------------------------------------------------- contorno
def edge(pts):
    for a, b in zip(pts, pts[1:]):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(P(*a)); s.SetEnd(P(*b)); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1)); board.Add(s)
edge([(0, 0), (BW, 0), (BW, BH), (0, BH), (0, 0)])

# ---------------------------------------------------------------- planos GND
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net('GND'))
    o = z.Outline(); o.NewOutline()
    for x, y in [(0, 0), (BW, 0), (BW, BH), (0, BH)]:
        o.Append(MM(ORG[0] + x), MM(ORG[1] + y))
    z.SetLocalClearance(MM(GAP)); z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(MM(0.3)); z.SetThermalReliefSpokeWidth(MM(0.6))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z)

KEEP = []
# ---------------------------------------------------------------- serigrafia
def text(s, x, y, size=1.2, layer=pcbnew.F_SilkS, rot=0, thick=0.18):
    t = pcbnew.PCB_TEXT(board); t.SetText(s); t.SetPosition(P(x, y))
    t.SetLayer(layer); t.SetTextSize(VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(thick)); t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    board.Add(t)
    w = len(s) * size * 0.85; h = size * 1.7
    KEEP.append((x - w/2 - 0.8, y - h/2 - 0.8, x + w/2 + 0.8, y + h/2 + 0.8))

xm = (xs[0] + xs[4]) / 2; ym_ = (yT + yB) / 2
text('2m', xm, yT + 2.6, 0.9, thick=0.15)
text('70cm', xm, yB - 3.4, 0.9, thick=0.15)
text('v1.1', xm, ym_, 0.8, thick=0.15)
text(f'DIPLEXOR 2m/70cm {VAR} v1.1', xm, yT + 2.6, 0.8, layer=pcbnew.B_SilkS, thick=0.15)
text('50R CPWG W1.4 G0.25 FR4 1.6', xm, yB - 2.6, 0.8, layer=pcbnew.B_SilkS, thick=0.15)

# ---------------------------------------------------------------- vias de cosido
def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay; L2_ = dx * dx + dy * dy
    t = 0 if L2_ == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2_))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

obst = []   # (xmin,ymin,xmax,ymax) de pads y agujeros no-GND o cualquiera
for fp in board.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        obst.append((pcbnew.ToMM(bb.GetLeft()) - ORG[0], pcbnew.ToMM(bb.GetTop()) - ORG[1],
                     pcbnew.ToMM(bb.GetRight()) - ORG[0], pcbnew.ToMM(bb.GetBottom()) - ORG[1],
                     p.GetNetname() == 'GND'))
def ok(x, y):
    if x < 1.2 or y < 1.2 or x > BW - 1.2 or y > BH - 1.2: return False
    for a, b, w in tracks:
        if seg_dist((x, y), a, b) < w / 2 + GAP + 0.4 + 0.35: return False
    for (x1, y1, x2, y2, g) in obst:
        m = 0.3 if g else 0.4 + GAP + 0.3
        if x1 - m < x < x2 + m and y1 - m < y < y2 + m: return False
    for (kx1, ky1, kx2, ky2) in KEEP:
        if kx1 < x < kx2 and ky1 < y < ky2: return False
    for vx, vy in vias:
        if math.hypot(x - vx, y - vy) < 1.6: return False
    return True
# valla a lo largo de las pistas (paso 2 mm, a 1.3 mm del borde de pista)
for a, b, w in list(tracks):
    L = math.dist(a, b)
    if L < 0.1: continue
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx, ny = -uy, ux
    n = int(L // 2.0)
    for i in range(n + 1):
        t = (i + 0.5) * L / (n + 1) if n else L / 2
        for s in (-1, 1):
            off = w / 2 + GAP + 0.4 + 0.45
            x, y = a[0] + ux * t + s * nx * off, a[1] + uy * t + s * ny * off
            if ok(x, y): via(x, y)
# rejilla de cosido general (3 mm)
gy = 1.5
while gy < BH:
    gx = 1.5
    while gx < BW:
        if ok(gx, gy): via(gx, gy)
        gx += 3.0
    gy += 3.0

# ---------------------------------------------------------------- rellenar y guardar
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.Save(pcb_path)
pcbnew.WriteDRCReport(board, os.path.join(OUT, name + '_drc.rpt'), pcbnew.EDA_UNITS_MILLIMETRES, True)
import json
geo = dict(variant=VAR, board=[BW, BH], thickness=1.6,
           holes=[list(h) for h in holes],
           connectors=[dict(ref='J1', x=j1[0], y=j1[1], side='left', label='RADIO'),
                       dict(ref='J2', x=j2[0], y=j2[1], side='right', label='2m'),
                       dict(ref='J3', x=j3[0], y=j3[1], side='right', label='70cm')])
json.dump(geo, open(os.path.join(OUT, 'board_geometry.json'), 'w'), indent=1)
print('OK', pcb_path, 'vias:', len(vias))
