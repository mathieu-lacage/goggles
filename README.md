# Diving goggles

What is special about these goggles ?

1. They are a practical way to freedive
2. You can make them yourself
3. You can make corrective lenses to match your eyesight

Here is a short comparison chart that illustrates alternatives

|                |  Max depth |  Ear Equalization       | Eye equalization | Field of view | Optical deformations |
|----------------|------------|-------------------------|------------------|---------------|----------------------|
| Diving goggles |  Unknown   |  Hands free (nose clip) | Not needed       | ++            | -                    |
| Normal goggles |  10m       |  Hands free (nose clip) | Impossible       | +++           | -                    |
| Fluid goggles  |  None      |  Hands free (nose clip) | Not needed       | +             | ---                  |
| Diving mask    |  None      |  BTV, Valsava, etc.     | Air from lungs   | +++           | -                    |


# How they work

These are freediving goggles, not swimming goggles. You could conceivably use these
goggles to swim but if you want swimming goggles, I recommend the most cost-effective
and practical solution: go buy a pair from your closest sports store.

The basics of how these goggles work is described in the USPTO patent
[20170203159A1](https://patents.google.com/patent/US20170203159A1/en)
and in the presentation of the indiegogo campaign for 
[Hektometer](https://www.indiegogo.com/projects/hektometer-revolutionary-freediving-goggles#/)
goggles.

Because the patent is abandoned, and, Hektometer goggles have not been available 
for sale since 2020, this project documents how I made a pair for myself using
hardware from my local FabLab, [SoFAB](https://www.sofab.tv/). Even though the principles
of operation are similar, the design is fairly different, to adapt to the production
tools that were available to me and potentially other makers.

# How to make one yourself

## What you need

1. For the inner flexible skirt:
   - A resin 3D printer for the mold. I used a [Formlab Form 3B+](https://formlabs.com/3d-printers/form-3b/).
   - Resin for the mold. I used [Grey Pro](https://formlabs.com/fr/boutique/materials/grey-pro-resin/).
   - 12 5x20 threaded screws to hold together the aluminium overmold
   - 10mm thick aluminium plates for the overmold. I bought 2 10x100x500 plates from [Blockenstock](https://www.blockenstock.fr/)
   - Something to cut 10mm tick aluminium plates. I used the services from [Decouplaser](https://www.decouplaser.fr/), a local metal shop
   - A drill press with drill bits (diameter 6) for aluminium.
   - Threading bits for aluminium. Kindly provided by a maker, Guy Mausy.
   - A plastic  injection machine. I used a [Holipress](https://holimaker.fr/holipress/) from [Holimaker](https://holimaker.fr/)
   - TPU Plastic pellets. I used [SEBS 90A](https://boutique.3dadvance.fr/fablab/1199-granules-de-sebs-shore-90a-holimaker), the recommended flex pellets from the machine builder.

2. For the outer rigid shell
   - A resin 3D printer. I used a [Formlab Form 3B+](https://formlabs.com/3d-printers/form-3b/).
   - Resin for rigid parts. I used [Grey Pro](https://formlabs.com/fr/boutique/materials/grey-pro-resin/).

3. For the lenses:
   - Transparent Acrylic/PMMA/Plexiglas sheets (5mm thick).
   - A router. I used an [Origin](https://www.shapertools.com/en-de/origin-overview). A manual router should work too 
     but it might be challenging to make accurate guides for the lens shapes.
   - A grover. I made one with sheets of wood, screws, and a dremel.

4. For the lens clip assembly:
   - A simple extrusion 3D printer. I used a [Prusa MK3](https://www.prusa3d.com/product/original-prusa-i3-mk3s-3d-printer-3/)
   - PETG or PLA filament
 
5. For assembly:
   - A silicon band to attach the left and right side of the goggles. I spent 4 EUR on
     [swedish-style swim goggles](https://malmsten.com/en/products/p/swim-goggles/swedish-goggles/swedish-goggles-classic/2168/2357/1710021)
     to reuse the band that came with them. You should be able to find a similar-looking pair in any swim store online. 
     [Replacement bands](https://malmsten.com/en/products/p/swim-goggles/swedish-goggles/swedish-goggles-spare-part-kit/2168/2357/1750001) 
     can often be bought separately.

6. For the lens correction:
   - A CNC if you can afford it for precision. I used a [Roland MDX-50](https://www.rolanddga.com/products/3d/mdx-50-benchtop-cnc-mill).
     Alternatively, if your correction prescription is limited to small-scale myopia, great care and 
     patience will replace the CNC if you are willing to live with
     imperfect corrective lenses. 
   - Sand paper, for wet use, grit sizes 150, 180, 240, 320, 400, 600, 800, 1000, 2000, 2500, 3000, 4000, 5000
   - Polishing paste. I recommend a car headlight polishing kit as they are cheap, and are commonly available.

## Get the models

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

## Print The shell

![Shell model viewed in OpenSCAD](/doc/assets/shell.png)

I have printed the shell successfully both on the 
[SoFAB](https://www.sofab.tv/)'s Formlab resin printer with both 
[Draft](https://formlabs.com/materials/standard/#draft-resin) and 
[Grey Pro](https://formlabs.com/materials/standard/#grey-pro-resin) resin.
The quality difference between the two resins is not visible but I picked
Grey Pro to avoid potential problems with part durabilityy.

I used the Formlab's slicer ([Preform](https://formlabs.com/fr/software/#preform)) 
with its default "magic wand" tool for orientation and support.

## Print the lens clip and assembly clip

![Lens clip model viewed in OpenSCAD](/doc/assets/lens-clip.png)
![Assembly clip model viewed in OpenSCAD](/doc/assets/back-clip.png)

The lens clip, and the back clip can be printed without special care on 
your FDM printer of choice. I recommend PETG for durability

## Cut and groove the lens

The starting point is a 6mm acrylic sheet that needs to be cut to produce


The lens.svg file contains two paths which should be cut at different depths
to produce a basic lens that will then be grooved to insert the lens clip
for assembly.


1. The inner path should be used as a guide to cut OUTSIDE of the ellipsis.
   The depth should be 5.2mm.
2. The outer path should be used as a guide to cut OUTSIDE of the ellipsis again.
   The depth should match that of the acrylic sheet. Theoreticaly, 6mm but
   I observed significant variability in the thickness of acrylic sheets 
   (+/- 0.2mm) so, you will have to adjust until you can separate your part
   from the sheet.



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

### Cut lenses

![Lens model viewed in OpenSCAD](/doc/assets/lens.png)

The lens is made out of Acrylic (AKA PMMA, Plexiglas). I could program my Lab's CNC
to use its 4th rotating axis to mill the sides of a single sheet of 6mm acrylic but 
that would be a bit complicated so, instead, I chose to make these lenses out of two
parts cut from sheets of 3mm acrylic, that are later glued together.

![Lens top and bottom viewed in OpenSCAD](/doc/assets/lens-top-bottom.png)

The `lens.svg` included in the release contains paths that can be loaded into an Origin
router and then used to cut acrylic sheets:

1. Cut inside the grey area, at the depth specified on the svg
2. Cut outsitde the grey area, at the depth of the acrylic sheet thickness minus a
   small tolerance (say, 3-0.2=2.8mm)
3. Separate the cut parts from the sheet by gently pushing them to break the 0.2mm
   connectors
4. Use a knife and sanding paper to clean gently the sides of the parts

### Assembly

### Making corrective lenses

## Other builds

If, by chance, you decide to make your own based on these instructions, please drop
me a note to let me know how it worked and what you had to change to have a working
pair of goggles.

## How to modify the design

## History
