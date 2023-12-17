RELEASE_VERSION=$(shell date +%Y-%m-%d)
MATERIAL ?= clear-resin
OG?=2.1
OD?=2.6
RESOLUTION?=40
SOURCE=lens.py lens-cnc.py goggles.py utils.py Makefile constants.py mg2.py
SCAD_TARGET=lens-clip.scad lens-OG-concave.scad lens-OD-concave.scad lens-OG-convex.scad lens-OD-convex.scad shell.scad top-mold.scad bottom-mold.scad back-clip.scad
SVG_TARGET=lens.svg
STL_TARGET=$(addsuffix .stl, $(basename $(SCAD_TARGET)))

PREVIEW_TARGET=$(SCAD_TARGET) $(SVG_TARGET)
RELEASE_TARGET=$(STL_TARGET) $(SVG_TARGET)


all: preview

preview: RESOLUTION=40
release: RESOLUTION=400

preview: $(PREVIEW_TARGET)

release: goggles-$(RELEASE_VERSION).zip

goggles-$(RELEASE_VERSION).zip: goggles-$(RELEASE_VERSION)
	zip -r $@ $^
goggles-$(RELEASE_VERSION): $(RELEASE_TARGET)
	mkdir -p goggles-$(RELEASE_VERSION)
	cp $^ goggles-$(RELEASE_VERSION)

lens-clip.scad lens.svg: $(SOURCE)
	./lens.py -r 40
back-clip.scad: $(SOURCE)
	./back-clip.py -r 40
shell.scad: $(SOURCE)
	./shell.py -r $(RESOLUTION) --top-hole=2
lens-%-convex.scad: $(SOURCE)
	./lens-cnc.py -o $(basename $@) --material=$(MATERIAL) --myopia-diopters $($*) --type=convex -r $(RESOLUTION)
lens-%-concave.scad: $(SOURCE)
	./lens-cnc.py -o $(basename $@) --material=$(MATERIAL) --myopia-diopters $($*) --type=concave -r $(RESOLUTION)
#	./lens-cnc.py -o lens-og --material=pmma --myopia-diopters 2 --astigmatism-diopters 1.5 --astigmatism-angle=5 --type=convex

lens-stls: lens-OG-convex.stl lens-OD-convex.stl lens-OG-concave.stl lens-OD-concave.stl

skirt.scad goggles.scad top-mold.scad bottom-mold.scad: $(SOURCE)
	./goggles.py -r $(RESOLUTION)

%.stl: %.scad
	/usr/bin/openscad -o $@ $^

clean:
	rm -f *.scad
	rm -f *.stl
	rm -f *~
