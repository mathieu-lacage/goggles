RELEASE_VERSION=$(shell date +%Y-%m-%d)
SOURCE=lens.py lens-cnc.py goggles.py utils.py Makefile
GENERATED=stl-40/lens-clip.stl lens.svg lens-og.stl lens-od.stl stl-40/lens-clip.scad lens-og.scad lens-od.scad

release: goggles-$(RELEASE_VERSION).zip

goggles-$(RELEASE_VERSION).zip: goggles-$(RELEASE_VERSION)
	zip -r $@ $^
goggles-$(RELEASE_VERSION): stl-40/lens-clip.stl lens.svg lens-og.stl lens-od.stl
	mkdir -p goggles-$(RELEASE_VERSION)
	cp $^ goggles-$(RELEASE_VERSION)

stl-40/lens-clip.scad lens.svg: $(SOURCE)
	./lens.py -r 40
lens-og.scad: $(SOURCE)
	./lens-cnc.py -o lens-og --material=pmma --myopia-diopters 2.1
lens-od.scad: $(SOURCE)
	./lens-cnc.py -o lens-od --material=pmma --myopia-diopters 2.6

stl-40/%.stl: %.scad
	/usr/bin/openscad -o $@ $^
%.stl: %.scad
	/usr/bin/openscad -o $@ $^

clean:
	rm -f $(GENERATED)
