RELEASE_VERSION=$(shell date +%Y-%m-%d)
SOURCE=lens.py lens-cnc.py goggles.py utils.py Makefile constants.py mg2.py
SCAD_TARGET=lens-clip.scad lens-og.scad lens-od.scad shell.scad top-mold.scad bottom-mold.scad back-clip.scad
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
lens-og.scad: $(SOURCE)
	./lens-cnc.py -o lens-og --material=pmma --myopia-diopters 2.1
#	./lens-cnc.py -o lens-og --material=pmma --myopia-diopters 2 --astigmatism-diopters 1.5 --astigmatism-angle=5
lens-od.scad: $(SOURCE)
	./lens-cnc.py -o lens-od --material=pmma --myopia-diopters 2.6
#	./lens-cnc.py -o lens-og --material=pmma --myopia-diopters 2 --astigmatism-diopters 1.5 --astigmatism-angle=5

shell.scad back-clip.scad skirt.scad goggles.scad top-mold.scad bottom-mold.scad: $(SOURCE)
	./goggles.py -r $(RESOLUTION)

%.stl: %.scad
	/usr/bin/openscad -o $@ $^

clean:
	rm -f *.scad
	rm -f *.stl
	rm -f *~
