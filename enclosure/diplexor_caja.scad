// =====================================================================
//  Caja imprimible 3D para el diplexor 2m/70cm (versiones SMA y BNC)
//  Diseño tipo "almeja": se parte a la altura del eje de los conectores,
//  así la PCB con los conectores soldados entra desde arriba.
//
//  Uso:
//    openscad -D 'VARIANT="SMA"' -D 'PART="base"' -o base.stl diplexor_caja.scad
//    VARIANT = "SMA" | "BNC"
//    PART    = "base" | "tapa" | "montaje"
//
//  Unidades: mm. Origen = esquina inferior-izquierda de la PCB, z = 0 en
//  la cara inferior de la PCB. La geometría de la PCB viene de
//  gen/board_<VARIANT>.scad (generado desde hardware/*/board_geometry.json).
// =====================================================================
VARIANT = "SMA";
PART    = "montaje";

include <gen/board_SMA.scad>   // define SMA_BOARD, SMA_HOLES, SMA_CONN
include <gen/board_BNC.scad>   // define BNC_BOARD, BNC_HOLES, BNC_CONN

$fn = 64;

// ---------------- parámetros generales ----------------
WALL   = 2.0;     // pared lateral
FLOOR  = 2.0;     // suelo (lleva el avellanado del tornillo)
ROOF   = 1.6;     // techo
CLR    = 0.3;     // holgura PCB-pared
FIT    = 0.15;    // holgura del labio de encaje
LIP_H  = 1.4;     // altura del labio base->tapa
LIP_T  = 1.0;     // grosor del labio
PCB_T  = 1.6;
POST_D = 5.0;     // columnas (base y tapa) sobre los agujeros M2
SCREW_CLR   = 2.4;   // paso M2
SCREW_PILOT = 1.7;   // rosca autorroscante M2 en PLA/PETG
HEAD_D = 4.4;  HEAD_H = 1.5;   // alojamiento cabeza M2 (DIN 7985 / ISO 7045)
TXT_DEPTH = 0.6;

// ---------------- parámetros por conector ----------------
// ¡Medir con calibre el conector real y ajustar si hace falta!
// SMA: Amphenol 132289 (end-launch bulkhead, rosca 1/4"-36)
SMA_AXIS   = PCB_T + 0.4;  // eje sobre la cara inferior de la PCB
SMA_FL_W   = 9.6;          // ancho/alto de la brida (cuadrada)
SMA_FL_T   = 1.9;          // espesor de la brida (queda dentro de la caja)
SMA_HOLE   = 6.8;          // taladro para la rosca 1/4"-36 (6.35 mm)
SMA_BELOW  = 3.0;          // espacio bajo la PCB (brida baja 2.8 mm)
SMA_ABOVE  = 4.8 + 0.4 + 0.3; // espacio sobre el eje (media brida + holgura)
// BNC: Amphenol B6252HB-NPP3G-50 (ángulo recto para PCB)
BNC_BODY_H = 14.8;         // altura del cuerpo sobre la PCB
BNC_AXIS   = PCB_T + 7.5;  // eje sobre la cara inferior de la PCB
BNC_HOLE   = 14.9;         // paso del frontal (casquillo + hexágono 12.7 e/c)
BNC_BELOW  = 3.0;          // patillas THT recortadas bajo la PCB
BNC_GAP    = 0.2;          // frontal del cuerpo -> pared interior

// ---------------- derivados ----------------
IS_SMA = VARIANT == "SMA";
BOARD  = IS_SMA ? SMA_BOARD : BNC_BOARD;
HOLES  = IS_SMA ? SMA_HOLES : BNC_HOLES;
CONN   = IS_SMA ? SMA_CONN  : BNC_CONN;
BW = BOARD[0]; BH = BOARD[1];
AXIS  = IS_SMA ? SMA_AXIS : BNC_AXIS;
HOLE  = IS_SMA ? SMA_HOLE : BNC_HOLE;
GAPX  = IS_SMA ? SMA_FL_T + 0.2 : BNC_GAP;       // hueco en las caras con conector
Z_IN_BOT = -(IS_SMA ? SMA_BELOW : BNC_BELOW);
Z_IN_TOP = IS_SMA ? AXIS + SMA_ABOVE : PCB_T + BNC_BODY_H + 0.5;
X0 = -GAPX;          X1 = BW + GAPX;       // interior
Y0 = -CLR;           Y1 = BH + CLR;
Z_SPLIT = AXIS;
OUT = [X1 - X0 + 2*WALL, Y1 - Y0 + 2*WALL];

function ky(y) = BH - y;       // KiCad (y hacia abajo) -> OpenSCAD

module rbox(p0, p1, r=1.2) {   // caja con aristas verticales redondeadas
    hull() for (x=[p0[0]+r, p1[0]-r], y=[p0[1]+r, p1[1]-r])
        translate([x, y, p0[2]]) cylinder(r=r, h=p1[2]-p0[2]);
}

module outer_shell(z0, z1) rbox([X0-WALL, Y0-WALL, z0], [X1+WALL, Y1+WALL, z1], 2.0);
module inner_space(z0, z1) rbox([X0, Y0, z0], [X1, Y1, z1], 0.8);

module conn_cuts() {
    for (c = CONN) {
        sx = c[3] == "left" ? X0 - WALL - 1 : X1 - 1;
        translate([sx, ky(c[2]), AXIS]) rotate([0, 90, 0])
            cylinder(d=HOLE, h=WALL + 2 + 1);
    }
}

module labels() {
    zt = Z_IN_TOP + ROOF;
    for (c = CONN) {
        left = c[3] == "left";
        tx = left ? X0 + 2.8 : X1 - 5;
        translate([tx, ky(c[2]), zt - TXT_DEPTH])
            linear_extrude(TXT_DEPTH + 0.1)
                rotate(left ? 90 : 0)
                text(c[4], size = IS_SMA ? 2.4 : 3.2, halign="center", valign="center",
                     font="Liberation Sans:style=Bold");
    }
    translate([(X0 + X1)/2, (Y0 + Y1)/2, zt - TXT_DEPTH])
        linear_extrude(TXT_DEPTH + 0.1)
            text("2m / 70cm", size = IS_SMA ? 2.8 : 4.0, halign="center", valign="center",
                 font="Liberation Sans:style=Bold");
}

module base() {
    difference() {
        union() {
            difference() {
                outer_shell(Z_IN_BOT - FLOOR, Z_SPLIT);
                inner_space(Z_IN_BOT, Z_SPLIT + 1);
            }
            // labio de centrado
            difference() {
                rbox([X0, Y0, Z_SPLIT - 0.01], [X1, Y1, Z_SPLIT + LIP_H], 0.8);
                rbox([X0 + LIP_T, Y0 + LIP_T, Z_SPLIT - 1], [X1 - LIP_T, Y1 - LIP_T, Z_SPLIT + LIP_H + 1], 0.5);
            }
            // columnas de apoyo de la PCB
            for (h = HOLES) translate([h[0], ky(h[1]), Z_IN_BOT - 0.01])
                cylinder(d=POST_D, h=-Z_IN_BOT + 0.01);
        }
        conn_cuts();
        conn_envelope();
        for (h = HOLES) translate([h[0], ky(h[1]), 0]) {
            translate([0, 0, Z_IN_BOT - FLOOR - 1]) cylinder(d=SCREW_CLR, h=50);
            translate([0, 0, Z_IN_BOT - FLOOR - 0.01]) cylinder(d=HEAD_D, h=HEAD_H);
        }
    }
}

module lid() {
    difference() {
        union() {
            difference() {
                outer_shell(Z_SPLIT, Z_IN_TOP + ROOF);
                inner_space(Z_SPLIT - 1, Z_IN_TOP);
            }
            // columnas que pisan la PCB
            for (h = HOLES) translate([h[0], ky(h[1]), PCB_T])
                cylinder(d=POST_D, h=Z_IN_TOP - PCB_T + 0.01);
        }
        // hueco para el labio de la base
        rbox([X0 - FIT, Y0 - FIT, Z_SPLIT - 1], [X1 + FIT, Y1 + FIT, Z_SPLIT + LIP_H + FIT], 0.8);
        conn_cuts();
        for (h = HOLES) translate([h[0], ky(h[1]), PCB_T - 0.01])
            cylinder(d=SCREW_PILOT, h=Z_IN_TOP - PCB_T - 0.6);
        labels();
    }
}

// volumen ocupado por cada conector dentro de la caja (se resta del labio)
module conn_envelope() {
    for (c = CONN) {
        left = c[3] == "left";
        if (IS_SMA) {
            e = SMA_FL_W/2 + 0.4;
            translate([left ? X0 - 0.1 : BW - 0.1, ky(c[2]) - e, AXIS - e])
                cube([GAPX + 0.2, 2*e, 2*e]);
        } else {
            translate([left ? X0 - 0.1 : BW - 14.9 - 0.3, ky(c[2]) - 7.35 - 0.4, PCB_T - 0.1])
                cube([14.9 + 0.3 + 0.2 + 0.1, 14.7 + 0.8, BNC_BODY_H + 0.6]);
        }
    }
}

// ---------- maquetas (solo para la vista de montaje) ----------
module pcb_mock() {
    color("darkgreen") difference() {
        cube([BW, BH, PCB_T]);
        for (h = HOLES) translate([h[0], ky(h[1]), -1]) cylinder(d=2.2, h=5);
    }
    for (c = CONN) {
        dir = c[3] == "left" ? -1 : 1;
        ex  = c[3] == "left" ? 0 : BW;
        if (IS_SMA) color("gold") translate([ex, ky(c[2]), AXIS]) {
            translate([dir > 0 ? 0 : -SMA_FL_T, -SMA_FL_W/2, -SMA_FL_W/2]) cube([SMA_FL_T, SMA_FL_W, SMA_FL_W]);
            rotate([0, 90*dir, 0]) cylinder(d=6.35, h=SMA_FL_T + 9.5);
        } else color("silver") translate([ex, ky(c[2]), PCB_T]) {
            translate([dir > 0 ? -14.9 : 0, -7.35, 0]) cube([14.9, 14.7, BNC_BODY_H]);
            translate([0, 0, AXIS - PCB_T]) rotate([0, 90*dir, 0]) cylinder(d=9.6, h=20.6);
        }
    }
}

if (PART == "base") base();
else if (PART == "tapa") translate([0, 0, Z_IN_TOP + ROOF]) rotate([180, 0, 0]) lid(); // boca abajo para imprimir
else if (PART == "check_base") intersection() { base(); translate([0,0,0.02]) pcb_mock(); }
else if (PART == "check_tapa") intersection() { lid(); translate([0,0,0.02]) pcb_mock(); }
else {
    color("SteelBlue", 0.9) base();
    pcb_mock();
    color("LightSteelBlue", 0.35) translate([0, 0, 12]) lid();   // tapa "explotada"
}

echo(str("CAJA ", VARIANT, ": exterior ", OUT[0], " x ", OUT[1], " x ",
         Z_IN_TOP + ROOF - (Z_IN_BOT - FLOOR), " mm"));
