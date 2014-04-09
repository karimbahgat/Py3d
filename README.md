# Documentation for Py3d
v0.1

## Introduction
A pure Python 3d ray-tracer renderer with a focus on being user-friendly :)
Allows the user to build a scene of 3d geometries and render it to an image file.
Obviously it is not as fast or powerful as heavier more hardcore 3d libraries,
but it is small, light, and can create some neat stuff in a portable environment.

## Requires:
PIL or Pillow - used for rendering the final image, but shouldn't be too difficult to remove that dependency in the future.

## Status:
Still early alpha development.
Several things aren't working correctly.
Main things to fix:

- add more geometry primitives (eg fix the rectangle, add box, add cyllinder)
- add texture for all geometries
- fix the camera behavior and viewing angle problems
- maybe allow for reflections and/or transparent glass-like surfaces

## License:
Contributors are wanted and needed, so this code is free to share, use, reuse, and modify according to the MIT license, see license.txt

## Credits:
Karim Bahgat (2014)
However, the majority of the code incl the main ray tracing engine and geometry types was taken directly from an online script by an unknown author at http://pastebin.com/f8f5ghjz
The main differences in Py3d are:

- Made it more userfriendly and provided documentation.
- Added the possibility to add texture surfaces (for now only for spheres)

## Contributors
I really need and want contributors for this project as I am no 3d guru (see the list of things to fix in the Status section).
Some learning/reference resources that can be used:

- another good one alternative at http://www.hxa.name/minilight/
- some more equations for getting intersection with other 3d geometries, https://www.cl.cam.ac.uk/teaching/1999/AGraphHCI/SMAG/node2.html#SECTION00023200000000000000
- understanding more, http://www.povray.org/documentation/view/3.7.0/246/
- and relfect and refract algos http://www.gamedev.net/topic/486265-raytracing---refraction-algorithm/
- and http://www.flipcode.com/archives/Raytracing_Topics_Techniques-Part_3_Refractions_and_Beers_Law.shtml
- and REALLY good https://www.cs.unc.edu/~rademach/xroads-RT/RTarticle.html
- also good lecture http://www.cs.utexas.edu/~fussell/courses/cs384g/lectures/lecture20-Z_buffer_pipeline.pdf


## Contents

### py3d.AnimatedObject(...) --> class object
  An animation object that contains how a geometry looks at each timeframe in its animation.
  
  - objs: any number of unnamed geometry objects as arguments
  
  Example:
          fallingball = AnimatedObject(Sphere( Vector(-2, -2, 20), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                       Sphere( Vector(-2, -2, 15), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                       Sphere( Vector(-2, -2, 9), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.7,0.3,0)),
                                       Sphere( Vector(-2, -2, 5), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.4,0.6,0)),
                                       Sphere( Vector(-2, -2, 1), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.1,0.9,0)) )

  - #### .reverse(...):
    - no documentation for this method

### py3d.Camera(...) --> class object
  The camera that views the scene. Always required.
  
  - cameraPos: A vector instance indicating the position of the camera
  - *zoom: a nr indicating the zoom level (WARNING, does not work properly yet)
  - *xangle: a nr indicating the x-axis viewing angle (WARNING, does not work properly yet)
  - *yangle: a nr indicating the y-axis viewing angle (WARNING, does not work properly yet)

### py3d.Color(...) --> class object
  Use this to create colors that can be manipulated by the raytracer. Subclassed from Vector.
  
  - create with 3 RGB integer color argments: r, g, and b. 

  - #### .cross(...):
    - no documentation for this method

  - #### .dot(...):
    - no documentation for this method

  - #### .magnitude(...):
    - no documentation for this method

  - #### .normal(...):
    - no documentation for this method

### py3d.Intersection(...) --> class object
  - no documentation for this class

### py3d.LightSource(...) --> class object
  A Lightsource instance. Creating multiple lightsources has no effect
  since you can only pass one to you rendering function.
  For now shines light in all directions, not focused on any particular spot.
  
  - takes x, y, and z coordinates as arguments for the location of the lightsource. 

  - #### .cross(...):
    - no documentation for this method

  - #### .dot(...):
    - no documentation for this method

  - #### .magnitude(...):
    - no documentation for this method

  - #### .normal(...):
    - no documentation for this method

### py3d.Plane(...) --> class object
  An infinite flat surface with no endings.
  
  - point: a vector of the centerpoint of the surface
  - normal: a vector towards which the plane centerpoint should be facing
  - color: a color instance

  - #### .getcolor(...):
    - no documentation for this method

  - #### .intersection(...):
    - no documentation for this method

### py3d.Ray(...) --> class object
  - no documentation for this class

### py3d.Rectangle(...) --> class object
  Works, but not working properly. Like a plane, but is limited to the shape of a defined rectangle. 
  Testing of whether inside limits is simplistic, wrong, and produces odd shapes.
  
  - width/height: makes no difference, only uses width to create equisquare
  - spin: currently not being used

  - #### .getcolor(...):
    - no documentation for this method

  - #### .intersection(...):
    - no documentation for this method

### py3d.Sphere(...) --> class object
  A ball-looking object, the 3d equivalent of a circle.
  
  - center: a vector of the center of the sphere
  - radius: the radius of the sphere measured in the same coordinate system as the vectors
  - color: a color instance (only matters if you don't give the sphere a texture
  - texture: the filepath to an imagefile to use as a texture (to wrap around the sphere). For now only takes gif files.
  - spintop: a vector indicating the "north" top of the sphere around which the sphere may spin, which impacts how and where the texture will be mapped.
  - facing: a vector indicating towards which direction its spin should be facing. Ccurrently not working properly bc have to fix normalization, so it is up to the user to make sure this argument is at right angles with the spintop/"north", ie pointing to somewhere along "the equator".

  - #### .addtexture(...):
    - no documentation for this method

  - #### .getcolor(...):
    - no documentation for this method

  - #### .intersection(...):
    - no documentation for this method

  - #### .normal(...):
    - no documentation for this method

### py3d.Vector(...) --> class object
  The basic building block indicating a 3D point coordinate position. It is a vector/arrow only in the sense that it starts at the zeropoint 0,0,0 and moves to the coordinates given.
  
  - x/y/z: the xyz coordinates of the point.

  - #### .cross(...):
    - no documentation for this method

  - #### .dot(...):
    - no documentation for this method

  - #### .magnitude(...):
    - no documentation for this method

  - #### .normal(...):
    - no documentation for this method

### py3d.gammaCorrection(...):
  - no documentation for this function

### py3d.renderAnimation(...):
  Renders the scene, given the following:
  
  - a camera instance
  - a lightsource instance
  - a list of *static* geometry object instances (ie those that will not be moving)
  - a list of animated object instances (ie that will change for every picture frame)
  - image dimensions
  - the savepath (with filename but without file extension) of where to save the rendered image
  - the image format extension to use when saving (should have a dot, eg ".png")

### py3d.renderScene(...):
  Renders the scene, given the following:
  
  - a camera instance
  - a lightsource instance
  - a list of geometry object instances
  - image dimensions
  - and the savepath with file extension of where to save the rendered image

### py3d.testRay(...):
  - no documentation for this function

### py3d.trace(...):
  - no documentation for this function

