import vtk


# create a rendering window and renderer
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)

# create a renderwindowinteractor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# create a cube source
cube = vtk.vtkCubeSource()

# set the length of cube source in x, y, and z direction
cube.SetXLength(1)
cube.SetYLength(1)
cube.SetZLength(1)

# mapper
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputConnection(cube.GetOutputPort())

# actor
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)

# assign actor to the renderer
ren.AddActor(cubeActor)

# enable user interface interactor
iren.Initialize()
renWin.Render()
iren.Start()
