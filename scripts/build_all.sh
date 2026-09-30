#!/usr/bin/env bash
# Regenera TODO desde cero: PCB (KiCad 7), DRC, Gerber/taladros, BOM/pos,
# vistas previas, cajas 3D (STL) y renders.
# Requisitos: kicad 7 (kicad-cli + pcbnew python), gerbv, openscad, python3-numpy, python3-pil
set -euo pipefail
cd "$(dirname "$0")/.."
export KICAD7_FOOTPRINT_DIR=${KICAD7_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
OPENSCAD=${OPENSCAD:-openscad}

for v in SMA BNC; do
  hw=hardware/$v; fab=fabrication/$v; name=diplexor_2m70cm_$v
  rm -rf "$hw" "$fab"; mkdir -p "$hw" "$fab/gerber" docs/img
  python3 scripts/gen_pcb.py $v "$hw" 2>&1 | grep -v "memory leak" || true
  rm -f "$hw"/*.kicad_prl
  mv "$hw/${name}_drc.rpt" "$fab/"
  pcb="$hw/$name.kicad_pcb"
  kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
      --subtract-soldermask --no-x2 -o "$fab/gerber/" "$pcb" >/dev/null
  kicad-cli pcb export drill --format excellon --excellon-separate-th -o "$fab/gerber/" "$pcb" >/dev/null
  kicad-cli pcb export pos --format csv --units mm --side both -o "$fab/${name}_pos.csv" "$pcb" >/dev/null
  cp BOM/BOM_$v.csv "$fab/"
  (cd "$fab/gerber" && rm -f ../gerber_$name.zip && zip -q ../gerber_$name.zip *)
  g=$fab/gerber/$name
  gerbv -x png -D 600 -a -b "#0b3d1e" -o docs/img/pcb_${v}_top.png \
      -f "#ffffffff" $g-F_Silkscreen.gto -f "#000000ff" $g-PTH.drl -f "#000000ff" $g-NPTH.drl \
      -f "#40c0ffff" $g-F_Mask.gts -f "#d4a017b0" $g-F_Cu.gtl -f "#ffff00ff" $g-Edge_Cuts.gm1 2>/dev/null
  gerbv -x png -D 600 -a -b "#0b3d1e" -o docs/img/pcb_${v}_bottom.png \
      -f "#ffffffff" $g-B_Silkscreen.gbo -f "#000000ff" $g-PTH.drl -f "#40c0ffff" $g-B_Mask.gbs \
      -f "#d4a017b0" $g-B_Cu.gbl -f "#ffff00ff" $g-Edge_Cuts.gm1 2>/dev/null
  grep -E "Found" "$fab/${name}_drc.rpt" | sed "s/^/  [$v] /"
done

python3 scripts/gen_enclosure_inc.py
mkdir -p enclosure/stl docs/img
for v in SMA BNC; do
  lv=$(echo $v | tr A-Z a-z)
  for p in base tapa; do
    $OPENSCAD -q -D "VARIANT=\"$v\"" -D "PART=\"$p\"" -o enclosure/stl/caja_${lv}_${p}.stl enclosure/diplexor_caja.scad
  done
  xvfb-run -a $OPENSCAD -q -D "VARIANT=\"$v\"" -D 'PART="montaje"' --imgsize=1400,1000 \
      --camera=0,0,0,55,0,25,0 --viewall --autocenter --colorscheme=Tomorrow \
      -o docs/img/caja_${lv}_montaje.png enclosure/diplexor_caja.scad
done
echo "Build OK"
