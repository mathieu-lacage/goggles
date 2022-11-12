# Diving goggles

What is special about these goggles ?

1. Both hands are free while swiming down
2. You can make them yourself
3. You can make corrective lenses to match your eyesight

## How they work

The basics of how these goggles work is described in the USPTO patent
[20170203159A1](https://patents.google.com/patent/US20170203159A1/en)
and in the presentation of the indiegogo campaign for 
[Hektometer](https://www.indiegogo.com/projects/hektometer-revolutionary-freediving-goggles#/)
goggles.

Because the patent is abandoned, and, Hektometer goggles have not been available 
for sale since 2020, this project documents how I made a pair for myself using
hardware from my local FabLab, [SoFAB](https://www.sofab.tv/).

## How to make one yourself

### What you need

1. For the inner flexible skirt:
   - A resin 3D printer. I used a [Formlab Form 3B+](https://formlabs.com/3d-printers/form-3b/).
   - Resin for flex parts. I used [Flexible 80A](https://formlabs.com/fr/materials/flexible-elastic/).

2. For the other 3D-printed parts:
   - A simple extrusion 3D printer
   - PETG or PLA filament

3. For the lenses:
   - Transparent Acrylic/PMMA/Plexiglas sheets (2mm and 3mm thick).
   - A router. I used an [Origin](https://www.shapertools.com/en-de/origin-overview). A manual router should work too 
     but it will be challenging to make accurate guides for the lens shapes.
   - Glue for acrylic sheets. I used [Acrifix 0192](https://www.plexiglas.de/files/plexiglas-content/pdf/technische-informationen/391-20-ACRIFIX-1R-0192-en.pdf)
   - a UV lamp to speed up the curing process for the acrylic glue I used. Alternatively, the sun is a fine replacement.

4. For assembly:
   - A silicon band to attach the left and right side of the goggles. I spent 4 EUR on
     [swedish-style swim goggles](https://malmsten.com/en/products/p/swim-goggles/swedish-goggles/swedish-goggles-classic/2168/2357/1710021)
     to reuse the band that came with them. You should be able to find a similar-looking pair in any swim store online. 
     [Replacement bands](https://malmsten.com/en/products/p/swim-goggles/swedish-goggles/swedish-goggles-spare-part-kit/2168/2357/1750001) 
     can often be bought separately.

5. For the lens correction:
   - A CNC if you can afford it for precision. I used a [Roland MDX-50](https://www.rolanddga.com/products/3d/mdx-50-benchtop-cnc-mill).
     Alternatively, if your correction prescription is limited to small-scale myopia, great care and 
     patience will replace the CNC if you are willing to live with
     imperfect corrective lenses. 
   - Sand paper, for wet use, grit sizes 150, 180, 240, 320, 400, 600, 800, 1000, 2000, 2500, 3000, 4000.
   - Polishing paste. I recommend a car headlight polishing kit as they are cheap, and are commonly available.

### Get the models

It is is easy to [download](https://github.com/mathieu-lacage/goggles/releases/download/v0.1/goggles-0.1.zip) 
all the STLs and SVGs from the project release page.

It is also possible to rebuild these models from the source Python code after you install 
[OpenSCAD](https://openscad.org/) and [SolidPython](https://github.com/SolidCode/SolidPython/):

```
$ sudo dnf install -y openscad
$ pip install SolidPython
$ ./goggles.py -r 400 -e
```

The resulting STLs will be located in the stl-400 subdirectory and the lens.svg file next to your goggles.py file.

### Print parts

#### The flex skirt

![Skirt model viewed in OpenSCAD](/doc/assets/skirt.png)

   - Make sure you have the latest version of the [Formlab slicing software]()
   - import the `skirt.stl` file, click on the MAGIC button to generate supports,
     slice the result, and upload the model to your printer
   - great care should be taken to remove supports from the print before wash
     and curing because the print is very fragile at this step.
   - I recommend curing longer (5 to 10 minutes) than required by the 
     Formlabs datasheets. For some reason, I have observed wide variance in the
     dimensional and elastic stability of the parts produced here so, be ready
     to print more than once.

#### The shell

![Shell model viewed in OpenSCAD](/doc/assets/shell.png)

I have printed the shell successfully both on the 
[SoFAB](https://www.sofab.tv/)'s Formlab resin printer with both 
[Draft](https://formlabs.com/materials/standard/#draft-resin) and 
[Grey Pro](https://formlabs.com/materials/standard/#grey-pro-resin) resin.
The quality difference between the two resins was not significant for 
this part.

I also printed a couple of versions with PETG and PLA filaments on
a [Prusa i3 MK3S](https://www.prusa3d.com/product/original-prusa-i3-mk3s-kit-3/). 
Functionally, the resulting parts are equivalent but they required extensive
post-processing to obtain nice-looking surface finishes. If you go down this path,
I recommend you to choose carefully the part orientation when you drop it in the 
slicer so that the supports are not created on the side of the shell that will be
in contact with the flex skirt (this will make it more likely your goggles do
not let water in).

#### Other parts

![Lens clip model viewed in OpenSCAD](/doc/assets/lens-clip.png)
![Lens alignment tool viewed in OpenSCAD](/doc/assets/lens-alignment.png)
![Back clip model viewed in OpenSCAD](/doc/assets/back-clip.png)

The lens clip, the lens alignment tool, and, if you decide you need it, the back clip
can be printed without special care on your printer of choice.

### Cut lenses

![Lens model viewed in OpenSCAD](/doc/assets/lens.png)

The lens is made out of Acrylic (AKA PMMA, Plexiglas). Ideally, we could make it 
out a single sheet of 6mm Acrylic and cut the right profile on the sides of this sheet
but this would require tools I do not have (and I am not even sure it is possible).

Instead, I chose to make these lenses out of two parts cut from sheets of 3mm Acrylic:

The svg included in the release contains paths that can be loaded into an Origin 
router and cut from Acrylic sheets:

### Assembly

### Making corrective lenses

## Other builds

If, by chance, you decide to make your own based on these instructions, please drop
me a note to let me know how it worked and what you had to change to have a working
pair of goggles.

## How to modify the design

## History
