# Montaje

1. **Soldar el SMD** (0805): primero las bobinas y los condensadores en serie, después los que van a masa (C1, C2, L4 y L5).
   Los pads a masa están unidos al plano sin alivio térmico, así que necesitan más calor (punta ancha, unos 350 °C).
2. **Soldar los conectores:**
   - **SMA:** mete el canto de la PCB entre las patas del conector hasta que la brida toque el borde.
     Suelda el pin central al pad y las 4 patas de masa, por arriba y por abajo.
   - **BNC:** inserta el conector y suelda el pin central, el pin de masa y las dos patas de anclaje.
     Corta las patillas a 2.5 mm como máximo por debajo de la PCB.
3. **Probar** antes de cerrar la caja (ver [PRUEBAS.md](PRUEBAS.md)).
4. **Cerrar la caja:**
   1. Apoya la PCB sobre las dos columnas de la base. Los conectores quedan en los semicírculos de las paredes.
   2. Coloca la tapa encima. El labio la centra.
   3. Atornilla desde abajo con 2 tornillos M2 autorroscantes (SMA: M2×10, BNC: M2×12).
      Los tornillos atraviesan la base y la PCB y roscan en las columnas de la tapa.
   4. **SMA:** si quieres, pon la tuerca de panel de 1/4"-36 por fuera para reforzar la pared.
      No la aprietes en exceso.

## Parámetros de la caja (enclosure/diplexor_caja.scad)
| Parámetro | Valor por defecto | Qué es |
|---|---|---|
| `SMA_FL_W` / `SMA_FL_T` | 9.6 / 1.9 mm | Ancho y grosor de la brida del SMA |
| `SMA_AXIS` | PCB + 0.4 mm | Altura del eje del SMA |
| `SMA_HOLE` | 6.8 mm | Paso de la rosca de 1/4"-36 |
| `BNC_BODY_H` | 14.8 mm | Altura del cuerpo del BNC sobre la PCB |
| `BNC_AXIS` | PCB + 7.5 mm | Altura del eje del BNC |
| `BNC_HOLE` | 14.9 mm | Paso del frontal del BNC |
| `WALL` / `FLOOR` / `ROOF` | 2.0 / 2.0 / 1.6 mm | Grosor de las paredes |
| `FIT` | 0.15 mm | Holgura del labio de encaje (auméntala si la tapa entra justa) |

Para regenerar los STL después de cambiar parámetros, ejecuta `make` o:
`openscad -D 'VARIANT="SMA"' -D 'PART="base"' -o caja_sma_base.stl enclosure/diplexor_caja.scad`
