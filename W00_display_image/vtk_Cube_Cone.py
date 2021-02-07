
	
import vtk
 
# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
WIDTH=640
HEIGHT=480
renWin.SetSize(WIDTH,HEIGHT)
 
# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
 
# create cube
cube = vtk.vtkCubeSource()
cube.SetXLength(1)
cube.SetYLength(1)
cube.SetZLength(1)
cube.SetCenter(-0.85,0,0)

# create cone
cone = vtk.vtkConeSource()
cone.SetResolution(60)
cone.SetCenter(0,0,0)
 
# cube mapper
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())

# cone mapper
coneMapper = vtk.vtkPolyDataMapper()
coneMapper.SetInputConnection(cone.GetOutputPort())

# cube actor
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)

# cone actor
coneActor = vtk.vtkActor()
coneActor.SetMapper(coneMapper)
 
# assign actor to the renderer
ren.AddActor(coneActor)
ren.AddActor(cubeActor)
 
# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
