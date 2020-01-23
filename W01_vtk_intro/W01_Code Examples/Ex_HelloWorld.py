# MDSC 689.03
# Advanced Medical Image Processing
#
# Example #1 - Demonstrating the VTK pipeline
# Modified by Danielle Whittier
# January 21, 2020
# --------------------------------------------
#
# This example shows how to apply a vtkImageData texture to 
# a sphere object (vtkPolyData) and add text to the render window.
#
# Example command line to run the script
#
#    python Ex_HelloWorld.py
#
# --------------------------------------------


#import packages used
import vtk

#define variable for the input jpg image
filename = "earth.jpg"
filename2 = "moon.jpeg"

# --------------------------------------------
# first make the earth sphere
# --------------------------------------------

# Generate an sphere polydata
sphere = vtk.vtkSphereSource()
sphere.SetRadius(10.0)


# specify how smooth the sphere will be
# sphere.SetThetaResolution(12)
# sphere.SetPhiResolution(12)

# Read the image data from a file
reader = vtk.vtkJPEGReader()
reader.SetFileName(filename)
reader.Update()

# Create texture object from the image data
texture = vtk.vtkTexture()
texture.SetInputConnection(reader.GetOutputPort())

# Map texture coordinates to the sphere coordinates
map_to_sphere = vtk.vtkTextureMapToSphere()
map_to_sphere.SetInputConnection(sphere.GetOutputPort())
map_to_sphere.PreventSeamOn()

# Create mapper and set the mapped texture as input
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(map_to_sphere.GetOutputPort())

# Create actor and set the mapper and the texture
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.SetTexture(texture)

# --------------------------------------------
# now make the moon sphere
# --------------------------------------------

# Generate an sphere polydata
sphereM = vtk.vtkSphereSource()
sphereM.SetRadius(2.5)

# specify how smooth the sphere will be
sphereM.SetThetaResolution(12)
sphereM.SetPhiResolution(12)

# Read the image data from a file
readerM = vtk.vtkJPEGReader()
readerM.SetFileName(filename2)
readerM.Update()

# Create texture object from the image data
textureM = vtk.vtkTexture()
textureM.SetInputConnection(readerM.GetOutputPort())

# Map texture coordinates to the sphere coordinates
map_to_sphereM = vtk.vtkTextureMapToSphere()
map_to_sphereM.SetInputConnection(sphereM.GetOutputPort())
map_to_sphereM.PreventSeamOn()

# Create mapper and set the mapped texture as input
mapperM = vtk.vtkPolyDataMapper()
mapperM.SetInputConnection(map_to_sphereM.GetOutputPort())

# Create actor and set the mapper and the texture
actorM = vtk.vtkActor()
actorM.SetMapper(mapperM)
actorM.SetTexture(textureM)
actorM.SetPosition(15,10,-10)


# --------------------------------------------
# now add some text to go with the sphere world
# --------------------------------------------

# create a text actor
txt = vtk.vtkTextActor()
txt.SetInput("Hello World!")
txtprop=txt.GetTextProperty()
txtprop.SetFontFamilyToArial()
txtprop.SetFontSize(40)
txtprop.SetColor(1,1,1)
txt.SetDisplayPosition(20,30)


# --------------------------------------------
# now bring it together: creater the renderer, 
# render window, and interactor 
# --------------------------------------------

#create the renderer    
ren = vtk.vtkRenderer()

#add the render window
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(1000,1000)

#add the interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# add the actors to the renderer (our sphere and text)
ren.AddActor(actor)
ren.AddActor(actorM)
ren.AddActor(txt)

# Initialize the interactor
iren.Initialize()

# now render the scene with all actors in it 
renWin.Render()

# Start the event loop for the interactor.
iren.Start()
