# Overture2STL

A Python application that converts Overture map data to a cohesive STL model.

![IMG_20250511_093003-s](https://github.com/user-attachments/assets/c81e3633-2c0e-4e5e-a607-4f73b2dcbaba)

## Usage

This is working code, that has generated consistent results for me, but still early such, so expect some rough edges.

Install the dependencies listed in requirements.txt.

This is now optional, as data is accessed directly from the Overture Maps data store by embedding a slightly modified variant of the Overture Maps CLI source code:
~~Install https://docs.overturemaps.org/getting-data/overturemaps-py/ that is used to download map data from within the application, so it needs to be accessible from where you run Overture2STL. If nothing else works, copy overturemaps.exe (Windows) there.~~

Use https://boundingbox.klokantech.com/ to select the area to generate an STL for. Select CSV for the output, that is then entered into Overture2STL.

Downloading data takes a rather long time, but once downloaded for a certain area (based on the name you give it) the generated files will be re-used unless you delete them.

You adjust what types of data are included by adding to or removing from the default Overture types list. Of note, segment contains all roads, paths etc.

Some areas contain lots of more or less irrelevant points that Overture2Stl will render as small cylinders. To avoid them altogether set the point-related dimensions to 0.

Be aware that STLs are dimension-less. Overture2Stl uses meters that all (?) slicers will treat as millimeters. Often that's good enough, but expect to have to scale down larger areas. Take that into account when you set the different dimensions.

Experiment / Iterate :)!

## References

- [Overture Maps Foundation](https://overturemaps.org/)
- [Overture Maps Documentation](https://docs.overturemaps.org/)

