.PHONY: all sim clean
all:            ## Regenera PCB, Gerber, STL e imágenes
	bash scripts/build_all.sh
sim:            ## Simulación del filtro
	python3 scripts/sim_diplexer.py
clean:
	rm -rf fabrication enclosure/stl enclosure/gen
