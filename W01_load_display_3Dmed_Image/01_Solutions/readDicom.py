import vtk
 
#This is a basic program to read a DICOM image and display the slice indicated by the user

#1) Define a DICOM reader
dicomReader = vtk.vtkDICOMImageReader()
  #This is a way to get input from the command line
dicomPath = input("Please, indicate the path to the DICOM directory: ")
dicomReader.SetDirectoryName(dicomPath) 
dicomReader.Update()  
dicomImage = dicomReader.GetOutput()
  
  #You can print some information about the image
print("Dimensions: " + str(dicomImage.GetDimensions()))
print("Spacing: " + str(dicomImage.GetSpacing()))
print("Origin: " + str(dicomImage.GetOrigin()))

#2) A mapper is required to indicate display options: slice number, window and level.
mapperDicom = vtk.vtkImageMapper()
mapperDicom.SetInputData(dicomImage)
zSlice = input("Please, indicate the slice number: ")
mapperDicom.SetZSlice(int(zSlice))
  # You can define a suitable window and level for better visualization
mapperDicom.SetColorWindow(1000)
mapperDicom.SetColorLevel(0)       

#3) The actor will represent the image in the window to be displayed.
actorDicom = vtk.vtkActor2D()
actorDicom.SetMapper(mapperDicom)        

#4) The renderer generates the visualization of the actor.  
rendererDicom = vtk.vtkRenderer()
rendererDicom.AddActor(actorDicom)

#5) The window is displayed, containing the actor(s).  
windowDicom = vtk.vtkRenderWindow()          
windowDicom.AddRenderer(rendererDicom)  
   #Set the size of the window according to the image size
windowDicom.SetSize(dicomImage.GetDimensions()[0], dicomImage.GetDimensions()[1])    

#6) The interactor let's you interact with your window
windowInteractor = vtk.vtkRenderWindowInteractor()
windowInteractor.SetRenderWindow(windowDicom)     
  
windowDicom.Render()
windowInteractor.Start()
  
#Please, notice the elements and order: Reader, mapper, actor, renderer, window, and interactor.