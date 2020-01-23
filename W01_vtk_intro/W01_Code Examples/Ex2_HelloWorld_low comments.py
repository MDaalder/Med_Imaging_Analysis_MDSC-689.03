##
# This example shows how to apply an vtkImageData texture to an sphere
# vtkPolyData object and add text to image.
##

import vtk

jpegfile = "earth.jpg"

# Create a render window
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(480,480)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Generate an sphere polydata
sphere = vtk.vtkSphereSource()
sphere.SetThetaResolution(12)
sphere.SetPhiResolution(12)


reader = vtk.vtkJPEGReader()
reader.SetFileName(jpegfile)


texture = vtk.vtkTexture()
texture.SetInputConnection(reader.GetOutputPort())

# create a text actor
txt = vtk.vtkTextActor()
txt.SetInput("Hello World!")
txtprop=txt.GetTextProperty()
txtprop.SetFontFamilyToArial()
txtprop.SetFontSize(40)
txtprop.SetColor(1,1,1)
txt.SetDisplayPosition(20,30)

# Map texture coordinates
map_to_sphere = vtk.vtkTextureMapToSphere()
map_to_sphere.SetInputConnection(sphere.GetOutputPort())
map_to_sphere.PreventSeamOn()


mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(map_to_sphere.GetOutputPort())

# Create actor and set the mapper and the texture
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.SetTexture(texture)

ren.AddActor(actor)
ren.AddActor(txt)

iren.Initialize()
renWin.Render()
iren.Start()
