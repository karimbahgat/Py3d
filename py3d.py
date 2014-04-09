"""
Py3d
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

"""

#IMPORTS
import math, os, sys
from math import sqrt, pow, pi
import time
import PIL,PIL.Image

#PYTHON VERSION CHECKING
PYTHON3 = int(sys.version[0]) == 3
if PYTHON3:
        xrange = range

#GEOMETRIES
class Vector( object ):
	"""
	The basic building block indicating a 3D point coordinate position. It is a vector/arrow only in the sense that it starts at the zeropoint 0,0,0 and moves to the coordinates given.

	- x/y/z: the xyz coordinates of the point.
	"""
	def __init__(self,x,y,z):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)
	
	def dot(self, b):
		return self.x*b.x + self.y*b.y + self.z*b.z
		
	def cross(self, b):
		return (self.y*b.z-self.z*b.y, self.z*b.x-self.x*b.z, self.x*b.y-self.y*b.x)
	   
	def magnitude(self):
		return sqrt(self.x**2+self.y**2+self.z**2)
		
	def normal(self):
		mag = self.magnitude()
		return Vector(self.x/mag,self.y/mag,self.z/mag)

	def __repr__(self):
		return str((self.x, self.y, self.z))
		
	def __add__(self, b):
		return Vector(self.x + b.x, self.y+b.y, self.z+b.z)
	
	def __sub__(self, b):
		return Vector(self.x-b.x, self.y-b.y, self.z-b.z)
		
	def __mul__(self, b):
		assert type(b) == float or type(b) == int
		return Vector(self.x*b, self.y*b, self.z*b)		
    
class Sphere( object ):
	"""
        A ball-looking object, the 3d equivalent of a circle.

        - center: a vector of the center of the sphere
        - radius: the radius of the sphere measured in the same coordinate system as the vectors
        - color: a color instance (only matters if you don't give the sphere a texture
        - texture: the filepath to an imagefile to use as a texture (to wrap around the sphere). For now only takes gif files.
        - spintop: a vector indicating the "north" top of the sphere around which the sphere may spin, which impacts how and where the texture will be mapped.
	- facing: a vector indicating towards which direction its spin should be facing. Ccurrently not working properly bc have to fix normalization, so it is up to the user to make sure this argument is at right angles with the spintop/"north", ie pointing to somewhere along "the equator".
	"""
	
	def __init__(self, center, radius, color, texture=None, spintop=Vector(0,0,1.0), facing="not specified"):
		self.c = center
		self.r = radius
		self.col = color
		self.spintop = spintop #if not specified looks upwards to z
		if facing == "not specified": self.facing = self.normal(spintop) #note, this one becomes normalized so makes error later on
		else: self.facing = facing
		if texture: self.addtexture(texture)
		else: self.texture = None
		
	def intersection(self, l):
		q = l.d.dot(l.o - self.c)**2 - (l.o - self.c).dot(l.o - self.c) + self.r**2
		if q < 0:
			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
		else:
			d = -l.d.dot(l.o - self.c)
			d1 = d - sqrt(q)
			d2 = d + sqrt(q)
			if 0 < d1 and ( d1 < d2 or d2 < 0):
				return Intersection(l.o+l.d*d1, d1, self.normal(l.o+l.d*d1), self)
			elif 0 < d2 and ( d2 < d1 or d1 < 0):
				return Intersection(l.o+l.d*d2, d2, self.normal(l.o+l.d*d2), self)
			else:
				return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)	
			
	def normal(self, b):
		return (b - self.c).normal()

	def getcolor(self, point):
		if self.texture:
			"based on this one, http://ray-tracer-concept.blogspot.no/2011/12/texture-mapping.html"
			center = self.c
			midx,midy,midz = center.x,center.y,center.z
			point = (point-center).normal()
			north = self.spintop.normal()
			phi = latitude = math.acos( -(north.dot(point)) )
			v = phi / math.pi
			equator = self.facing
			try: cosinput = point.dot(equator) / math.sin( phi )
			except ValueError:
				"floating point inaccuracy has made the 1 or -1 go out of bounds"
				if phi > 1:
					cosinput = point.dot(equator) / math.sin( 1 )
				elif phi < -1:
					cosinput = point.dot(equator) / math.sin( -1 )
			except ZeroDivisionError:
				cosinput = point.dot(equator) / 0.0000001
			try: theta = longitude = ( math.acos( cosinput ) ) / ( 2 * math.pi)
			except ValueError:
				"floating point inaccuracy has made the 1 or -1 go out of bounds"
				if cosinput > 1:
					theta = longitude = ( math.acos( 1 ) ) / ( 2 * math.pi)
				elif cosinput < -1:
					theta = longitude = ( math.acos( -1 ) ) / ( 2 * math.pi)
			#determine north or south
			if Vector(*north.cross(equator)).dot(point) > 0:
				u = theta 
			else:
				u = 1 - theta
			imgwidth,imgheight = self.texture.width()-1, self.texture.height()-1
			pixeltoget = (int(u*imgwidth), int(v*imgheight))
			color = map(int,self.texture.get(*pixeltoget).split())
			return Vector(*color)
		else:
			return self.col

	def addtexture(self, imgpath):
		import Tkinter as tk
		tempwin = tk.Tk()
		self.texture = tk.PhotoImage(file=imgpath)

##class Cylinder( object ):
##
##	"not done, just a copy of sphere, needs work. maybe see http://stackoverflow.com/questions/4078401/trying-to-optimize-line-vs-cylinder-intersection"
##	
##	def __init__(self, startpoint, endpoint, radius, color):
##		self.s = startpoint
##		self.e = endpoint
##		self.r = radius
##		self.col = color
##		
##	def intersection(self, l):
##		q = l.d.dot(l.o - self.c)**2 - (l.o - self.c).dot(l.o - self.c) + self.r**2
##		if q < 0:
##			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
##		else:
##			d = -l.d.dot(l.o - self.c)
##			d1 = d - sqrt(q)
##			d2 = d + sqrt(q)
##			if 0 < d1 and ( d1 < d2 or d2 < 0):
##				return Intersection(l.o+l.d*d1, d1, self.normal(l.o+l.d*d1), self)
##			elif 0 < d2 and ( d2 < d1 or d1 < 0):
##				return Intersection(l.o+l.d*d2, d2, self.normal(l.o+l.d*d2), self)
##			else:
##				return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)	
##			
##	def normal(self, b):
##		return (b - self.c).normal()
##
##class LightBulb( Sphere ):
##        pass

class Plane( object ):
	"""
        An infinite flat surface with no endings.

        - point: a vector of the centerpoint of the surface
        - normal: a vector towards which the plane centerpoint should be facing
        - color: a color instance
        """
	def __init__(self, point, normal, color):
		self.n = normal
		self.p = point
		self.col = color
		
	def intersection(self, ray):
		dotprod = ray.d.dot(self.n)
		if dotprod == 0:
			#a zero dotprod of two vectors means they are at right angles from each other
			#meaning destination and plane normal direction are at right angles from each other
			#meaning ray will travel along the surface of the plane and never hit it
			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
		else:
			hitanglevector = self.p - ray.o #the normal/perpendicular/diff vector bw hitorigin vector and the surface direction vector
			partdotprod = hitanglevector.dot(self.n) #the ray's hit impact on the plane given its angle?
			transferratio =  partdotprod / dotprod #how much impact at hitpoint vs original full ray power
			hitpoint = ray.d*transferratio #scale the ray backwards by the ratio to get the relative hitpoint
			worldhitpoint = ray.o+hitpoint #and back to absolute world coordinates
			return Intersection(worldhitpoint, transferratio, self.n, self)

	def getcolor(self, point):
		return self.col

class Rectangle( Plane ):
	"""
	Works, but not working properly. Like a plane, but is limited to the shape of a defined rectangle. 
	Testing of whether inside limits is simplistic, wrong, and produces odd shapes.
	
	- width/height: makes no difference, only uses width to create equisquare
	- spin: currently not being used
	"""
	def __init__(self, point, normal, width, height, color, spin="not specified"):
		self.n = normal
		self.p = point
		self.halfwidth = width/2.0
		self.halfheight = height/2.0
		if spin == "not specified": self.spin = Vector(0,0,1)
		else: self.spin = spin
		self.col = color
		
	def intersection(self, ray):
		dotprod = ray.d.dot(self.n)
		if dotprod == 0:
			#a zero dotprod of two vectors means they are at right angles from each other
			#meaning destination and plane normal direction are at right angles from each other
			#meaning ray will travel along the surface of the plane and never hit it
			return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)
		else:
			hitanglevector = self.p - ray.o #the normal/perpendicular/diff vector bw hitorigin vector and the surface direction vector
			partdotprod = hitanglevector.dot(self.n) #the ray's hit impact on the plane given its angle?
			transferratio =  partdotprod / dotprod #how much impact at hitpoint vs original full ray power
			hitpoint = ray.d*transferratio #scale the ray backwards by the ratio to get the relative hitpoint
			worldhitpoint = ray.o+hitpoint #and back to absolute world coordinates
			if worldhitpoint.x > self.p.x-self.halfwidth and worldhitpoint.x < self.p.x+self.halfwidth \
			   and worldhitpoint.y > self.p.y-self.halfwidth and worldhitpoint.y < self.p.y+self.halfwidth \
			   and worldhitpoint.z > self.p.z-self.halfwidth and worldhitpoint.z < self.p.z+self.halfwidth:
				return Intersection(worldhitpoint, transferratio, self.n, self)
			else:
				return Intersection( Vector(0,0,0), -1, Vector(0,0,0), self)

##class Box( object ):
##        "not done. consists of multiple rectangle objects as its sides"
##        pass

class AnimatedObject( object ):
        """
        An animation object that contains how a geometry looks at each timeframe in its animation.
        
        - objs: any number of unnamed geometry objects as arguments
        
        Example:
                fallingball = AnimatedObject(Sphere( Vector(-2, -2, 20), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                             Sphere( Vector(-2, -2, 15), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                             Sphere( Vector(-2, -2, 9), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.7,0.3,0)),
                                             Sphere( Vector(-2, -2, 5), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.4,0.6,0)),
                                             Sphere( Vector(-2, -2, 1), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.1,0.9,0)) )
        """
        def __init__(self, *objs):
                self.objs = objs

        def __iter__(self):
                for obj in self.objs:
                        yield obj

        def __getitem__(self, index):
                return self.objs[index]

        def reverse(self):
                self.objs = [each for each in reversed(self.objs)]
                return self


#RAY TRACING INTERNAL COMPONENTS
class Ray( object ):
	
	def __init__(self, origin, direction):
		self.o = origin
		self.d = direction
		
class Intersection( object ):
	#keeps a record of a known intersection bw ray and obj?
	def __init__(self, point, distance, normal, obj):
		self.p = point
		self.d = distance
		self.n = normal
		self.obj = obj
		
def testRay(ray, objects, ignore=None):
	intersect = Intersection( Vector(0,0,0), -1, Vector(0,0,0), None)
	
	for obj in objects:
		if obj is not ignore:
			currentIntersect = obj.intersection(ray)
			if currentIntersect.d > 0 and intersect.d < 0:
				intersect = currentIntersect
			elif 0 < currentIntersect.d < intersect.d:
				intersect = currentIntersect
	return intersect
	
def trace(ray, objects, light, maxRecur):
	if maxRecur < 0:
		return Color(0,0,0) # originally just a tuple, I made it a vector
	intersect = testRay(ray, objects)
	#hits nothing
	if intersect.d == -1:
		col = Color(AMBIENT,AMBIENT,AMBIENT)
	#camera sees shadow part of object (not hit by light)
	elif intersect.n.dot(light - intersect.p) < 0:
		col = intersect.obj.getcolor(intersect.p) * AMBIENT
	#camera sees obj in light
	else:
                #then main
		lightRay = Ray(intersect.p, (light-intersect.p).normal())
		if testRay(lightRay, objects, intersect.obj).d == -1:
			lightIntensity = 1000.0/(4*pi*(light-intersect.p).magnitude()**2)
			col = intersect.obj.getcolor(intersect.p) * max(intersect.n.normal().dot((light - intersect.p).normal()*lightIntensity), AMBIENT)
			
			#TRY REFLECT ONCE (see https://www.cs.unc.edu/~rademach/xroads-RT/RTarticle.html )
			#working but makes weird result...maybe missing the minus sign somehere...
##			def vectdot(v1,v2):
##				return Vector(v1.x*v2.x,v2.y*v1.y,v2.z*v1.z)
##			#def raymulti(ray,vect):
##			#	neworig = vectdot(ray.o,vect) *-1
##			#	newdest = vectdot(ray.d,vect)
##			#	return Ray(neworig,newdest)
##			dotprodnr = ray.d.dot(intersect.n) #raymulti(ray,intersect.n)
##			dotprodray = Vector(dotprodnr,dotprodnr,dotprodnr)
##			reflectdest = ray.d + (vectdot(vectdot(Vector(2.0,2.0,2.0),intersect.n),dotprodray)) #ray + (vectdot(intersect.n,Vector(2,2,2)))# * dotprodray )
##			reflect = Ray(intersect.p,reflectdest)
##			col = trace(reflect,objects,light,maxRecur-1)
##			#col = Vector(*gammaCorrection(col,AMBIENT))
		else:
			col = intersect.obj.getcolor(intersect.p) * AMBIENT
	return col
	
def gammaCorrection(color,factor):
	return (int(pow(color.x/255.0,factor)*255),
			int(pow(color.y/255.0,factor)*255),
			int(pow(color.z/255.0,factor)*255))


#USER FUNCTIONS
class Color(Vector):
	"""
	Use this to create colors that can be manipulated by the raytracer. Subclassed from Vector.

	- create with 3 RGB integer color argments: r, g, and b. 
	"""
	pass

class LightSource(Vector):
	"""
	A Lightsource instance. Creating multiple lightsources has no effect
	since you can only pass one to you rendering function.
	For now shines light in all directions, not focused on any particular spot.

	- takes x, y, and z coordinates as arguments for the location of the lightsource. 
	"""

class Camera:
	"""
	The camera that views the scene. Always required.

	- cameraPos: A vector instance indicating the position of the camera
	- *zoom: a nr indicating the zoom level (WARNING, does not work properly yet)
	- *xangle: a nr indicating the x-axis viewing angle (WARNING, does not work properly yet)
	- *yangle: a nr indicating the y-axis viewing angle (WARNING, does not work properly yet)
	"""
	def __init__(self, cameraPos, zoom=50.0, xangle=-5, yangle=-5):
		self.pos = cameraPos
		self.zoom = zoom
		self.xangle = xangle
		self.yangle = yangle

def renderScene(camera, lightSource, objs, imagedims, savepath):
        """
        Renders the scene, given the following:

        - a camera instance
        - a lightsource instance
        - a list of geometry object instances
        - image dimensions
        - and the savepath with file extension of where to save the rendered image
        """
        imgwidth,imgheight = imagedims
        img = PIL.Image.new("RGB",imagedims)
        #objs.append( LightBulb(lightSource, 0.2, Vector(*white)) )
        print ("rendering 3D scene")
        t=time.clock()
        for x in xrange(imgwidth):
                #print x
                for y in xrange(imgheight):
                        ray = Ray( camera.pos, (Vector(x/camera.zoom+camera.xangle,y/camera.zoom+camera.yangle,0)-camera.pos).normal())
                        col = trace(ray, objs, lightSource, 10)
                        img.putpixel((x,imgheight-1-y),gammaCorrection(col,GAMMA_CORRECTION))
        print ("time taken", time.clock()-t)
        img.save(savepath)

def renderAnimation(camera, lightSource, staticobjs, animobjs, imagedims, savepath, saveformat):
        """
        Renders the scene, given the following:

        - a camera instance
        - a lightsource instance
        - a list of *static* geometry object instances (ie those that will not be moving)
        - a list of animated object instances (ie that will change for every picture frame)
        - image dimensions
        - the savepath (with filename but without file extension) of where to save the rendered image
        - the image format extension to use when saving (should have a dot, eg ".png")
        """
        frame = 0
        while True:
                print ("frame",frame)
                timesavepath = savepath+"_"+str(frame)+saveformat
                objs = []
                objs.extend(staticobjs)
                objs.extend([animobj[frame] for animobj in animobjs])
                renderScene(camera, lightSource, objs, imagedims, timesavepath)
                frame += 1

#SOME LIGHTNING OPTIONS
AMBIENT = 0.05 #daylight/nighttime
GAMMA_CORRECTION = 1/2.2 #lightsource strength?

#COLORS
red = (255,0,0)
yellow = (255,255,0)
green = (0,255,0)
blue = (0,0,255)
grey = (120,120,120)
white = (255,255,255)
purple = (200,0,200)

if __name__ == "__main__":
        
        def ospath(filepath):
                if isinstance(filepath, (list,tuple)):
                        pathlist = filepath
                elif "/" in filepath:
                        pathlist = filepath.split("/")
                elif "\\" in filepath:
                        pathlist = filepath.split("\\")
                return os.path.join(*pathlist)

        def origtest():
                print ("")
                print ("origtest")
                #BUILD THE SCENE
                imagedims = (500,500)
                savepath = ospath("testing/results/3dscene_orig.png")
                objs = []
                objs.append(Sphere( Vector(-2,0,-10), 2, Vector(*green)))      
                objs.append(Sphere( Vector(2,0,-10), 3.5, Vector(*red)))
                objs.append(Sphere( Vector(0,-4,-10), 3, Vector(*blue)))
                objs.append(Plane( Vector(0,0,-12), Vector(0,0,1), Vector(*grey)))
                lightSource = LightSource(0,10,0)
                camera = Camera(Vector(0,0,20))

                #RENDER
                renderScene(camera, lightSource, objs, imagedims, savepath)

        def normaltest():
                print ("")
                print ("normaltest")
                #BUILD THE SCENE
                """
                the camera is looking down on the surface with the spheres from above
                the surface is like looking down on the xy axis of the xyz coordinate system
                the light is down there together with the spheres, except from one of the sides
                """
                imagedims = (200,200)
                savepath = ospath("testing/results/3dscene.png")
                texturepath = ospath("testing/textures/spheretexture.gif")
                objs = []
                #objs.append(Sphere( Vector(-4, -2, 1), 1, Vector(*red), texture="spheretexture.gif"))
                objs.append(Sphere( Vector(-2, -2, 1), 1, Color(*blue), texture=texturepath, spintop=Vector(1,0,0), facing=Vector(0,1,0)))
                #objs.append(Sphere( Vector(-2, -4, 1), 1, Vector(*green), texture="spheretexture.gif"))
                #objs.append(Plane( Vector(0,0,0), Vector(0,0,1), Vector(*yellow)))
                objs.append(Rectangle( Vector(-3,-3,0), Vector(-4, -2, 2), width=2, height=2, color=Vector(*yellow)))
                lightSource = LightSource(-4, -2, 8)
                camera = Camera(Vector(-1,-1,20)) #AWESOME CLOSEUP ANGLE: Vector(-9,-9,20)

                #RENDER
                renderScene(camera, lightSource, objs, imagedims, savepath)

        def animtest():
                print ("")
                print ("falling ball test")
                #BUILD THE SCENE
                imagedims = (200,200)
                savepath = ospath("testing/results/3d_fallball")
                saveformat = ".png"
                testtexture = ospath("testing/textures/spheretexture.gif")
                staticobjs = []
                staticobjs.append(Sphere( Vector(-4, -2, 1), 1, Color(*red), texture=testtexture, spintop=Vector(1,0,0), facing=Vector(0,1,0)))
                staticobjs.append(Sphere( Vector(-2, -4, 1), 1, Color(*green), texture=testtexture, spintop=Vector(0,1,0), facing=Vector(0,0,1)))
                staticobjs.append(Plane( Vector(0,0,0), Vector(0,0,1), Vector(*purple)))
                animobjs = []
                fallingball = AnimatedObject(Sphere( Vector(-2, -2, 20), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                             Sphere( Vector(-2, -2, 15), 1, Vector(*yellow), texture=testtexture, facing=Vector(1,0,0)),
                                             Sphere( Vector(-2, -2, 9), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.7,0.3,0)),
                                             Sphere( Vector(-2, -2, 5), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.4,0.6,0)),
                                             Sphere( Vector(-2, -2, 1), 1, Vector(*yellow), texture=testtexture, facing=Vector(0.1,0.9,0)) )
                animobjs.append(fallingball)
                lightSource = LightSource(-4,-4,10)
                camera = Camera(Vector(0,0,30))

                #RENDER
                renderAnimation(camera, lightSource, staticobjs, animobjs, imagedims, savepath, saveformat)

        #RUN TESTS
        #origtest()
        normaltest()
        #animtest()

