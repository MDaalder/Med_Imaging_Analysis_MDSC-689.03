import vtk
 
#This is a basic program to read a Nifti image and display the slice indicated by the user

#1) Define a Nifti reader
NiftiReader = vtk.vtkNIFTIImageReader()  
  #This is a way to get input from the command line
NiftiPath = input("Please, indicate the path to the Nifti file: ")
  #Note this little difference with DICOM reader.
NiftiReader.SetFileName(NiftiPath)
NiftiReader.Update()  
NiftiImage = NiftiReader.GetOutputPort()

  
  #You can print some information about the image
NiftiHeader = NiftiReader.GetOutput()
print("Dimensions: " + str(NiftiHeader.GetDimensions()))
print("Spacing: " + str(NiftiHeader.GetSpacing()))
print("Origin: " + str(NiftiHeader.GetOrigin()))

#2) A mapper is required to indicate display options: slice number, window and level.
mapperNifti = vtk.vtkImageMapper()
mapperNifti.SetInputConnection(NiftiImage)
zSlice = input("Please, indicate the slice number: ")
mapperNifti.SetZSlice(int(zSlice))
  # You can define a suitable window and level for better visualization
mapperNifti.SetColorWindow(1000)
mapperNifti.SetColorLevel(500)       

#3) The actor will represent the image in the window to be displayed.
actorNifti = vtk.vtkActor2D()
actorNifti.SetMapper(mapperNifti)        

#4) The renderer generates the visualization of the actor.  
rendererNifti = vtk.vtkRenderer()
rendererNifti.AddActor(actorNifti)

#5) The window is displayed, containing the actor(s).  
windowNifti = vtk.vtkRenderWindow()          
windowNifti.AddRenderer(rendererNifti)  
   #Set the size of the window according to the image size
windowNifti.SetSize(NiftiHeader.GetDimensions()[0], NiftiHeader.GetDimensions()[1])    

#6) The interactor let's you interact with your window
windowInteractor = vtk.vtkRenderWindowInteractor()
windowInteractor.SetRenderWindow(windowNifti)     
  
windowNifti.Render()
windowInteractor.Start()
  
#Please, notice the elements and order: Reader, mapper, actor, renderer, window, and interactor.