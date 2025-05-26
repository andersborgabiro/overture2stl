# Overture2Stl

A Python application that converts Overture map data to a cohesive STL model.

![IMG_20250511_093003-s](https://github.com/user-attachments/assets/c81e3633-2c0e-4e5e-a607-4f73b2dcbaba)

## Usage

This is working code, that has generated consistent results for me, but still early such, so expect some rough edges.

Use https://boundingbox.klokantech.com/ to select the area to generate an STL for. Select CSV for the output, that is then entered into Overture2Stl.

It uses https://docs.overturemaps.org/getting-data/overturemaps-py/ to download map data, so it needs to be accessible from where you run Overture2Stl. If nothing else works, copy overturemaps.exe there.

Downloading data takes a rather long time, but once downloaded for a certain area (based on the name you give it) the files will be re-used unless you delete them.

You adjust what types of data are included by adding to or removing from the default Overture types list. Of note, segment contains all roads, paths etc.

Generating an aligned base is still work in progress, so you need to add your own for now (use e.g. TinkerCAD or the slicer). There's code in there that attempts to support it, but it doesn't work right now.

Some areas contain lots of points that Overture2Stl will render as small cylinders. To avoid them set the point-related dimensions to 0.

Be aware that STLs are dimension-less. Overture2Stl uses meters that all (?) slicers will treat as millimeters. Often that's good enough, but expect to have to scale down larger areas. Take that into account when you select road widths and heights.

Experiment :)!

More will be added later.
