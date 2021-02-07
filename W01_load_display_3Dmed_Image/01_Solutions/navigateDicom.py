#Import python libraries
import vtk

# def is used to define a function in python.
def ReadDicom():  
  print("---------------------------Reading image---------------------------")
  
  # Define a dicom reader from vtk.
  dicomReader = vtk.vtkDICOMImageReader()
  
     #Read the path that the user will input.
  dicomPath = input("Please, indicate the path to the DICOM directory: ")
  dicomReader.SetDirectoryName(dicomPath)
  dicomReader.Update()
  
     #Store the image in a global variable, so that it can be accesed later in any part of the code.
  global dicomImage
  dicomImage = dicomReader.GetOutput()
  
     #Print some information about the image
  print("Dimensions: " + str(dicomImage.GetDimensions()))
  print("Spacing: " + str(dicomImage.GetSpacing()))
  print("Origin: " + str(dicomImage.GetOrigin()))
  
# This function is used to define the image orientation as axial, coronal, or sagittal.
# Note how it receives two parameters: imageToOrient, and orientation
def orientImage (imageToOrient, orientation):  
  (xMin, xMax, yMin, yMax, zMin, zMax) = imageToOrient.GetExtent()
  (xSpacing, ySpacing, zSpacing) = imageToOrient.GetSpacing()
  (x0, y0, z0) = imageToOrient.GetOrigin()
  
  # Calculate the coordinates of the center of the image.
  center = [x0 + xSpacing * (xMin + xMax),
            y0 + ySpacing * (yMin + yMax),
            z0 + zSpacing * (zMin + zMax)]
    
  #This matrices are used to transform the coordinates of the image, for each orientation.  
  axial = vtk.vtkMatrix4x4()
  axial.DeepCopy((1, 0, 0,center[0] ,
                  0, -1, 0,center[1] ,
                  0, 0, 1,center[2],
                  0, 0, 0, 1))
    
  coronal = vtk.vtkMatrix4x4()
  coronal.DeepCopy((1, 0, 0, center[0],
                    0, 0, 1, center[1],
                    0, -1, 0, center[2],
                    0, 0, 0, 1))
    
  sagittal = vtk.vtkMatrix4x4()
  sagittal.DeepCopy((0, 0,-1, center[0],
                     1, 0, 0, center[1],
                     0, -1, 0,center[2] ,
                    0, 0, 0, 1))

  # vtkImageReslice orients an image, given a transformation matrix.
  reslice = vtk.vtkImageReslice()
  reslice.SetInputData(imageToOrient)
  reslice.SetOutputDimensionality(3)
  reslice.SetResliceAxesOrigin(0,0,0)
  
  if orientation=='axial':
    reslice.SetResliceAxes(axial)
  elif orientation=='coronal':
    reslice.SetResliceAxes(coronal)    
  elif orientation=='sagittal':
    reslice.SetResliceAxes(sagittal)
    
  # interpolation is required to re-slice the image in the required orientation  
  reslice.SetInterpolationModeToCubic()
  reslice.Update()
  
  return reslice.GetOutput()

# This is the main navigation function
def Navigate2D():
  print("---------------------------Navigating 2D---------------------------")
  print("Please, choose the navigation axis")
  print("1 Axial")
  print("2 Coronal")
  print("3 Sagittal")
  optionUser = input("?: ")  
  print("Use up and down arrows to navigate")
  
  global orientation
  global zSlice  
  zSlice = 0
    
  if (optionUser == "1"):
    orientation = "axial"
  if (optionUser == "2"):
    orientation = "coronal"    
  if (optionUser == "3"):
    orientation = "sagittal"    
    
  imageNavigate2D = orientImage(dicomImage, orientation)      
    
  global mapperNavigate2D
  mapperNavigate2D = vtk.vtkImageMapper()
  mapperNavigate2D.SetInputData(imageNavigate2D)
  mapperNavigate2D.SetZSlice(zSlice)
  # window and level have to be adjusted for better visualization
  mapperNavigate2D.SetColorWindow(1000)
  mapperNavigate2D.SetColorLevel(0)       
    
  actorNavigate2D = vtk.vtkActor2D()
  actorNavigate2D.SetMapper(mapperNavigate2D)        

  global renderWindowNavigate2D     
  rendererNavigate2D = vtk.vtkRenderer()
  rendererNavigate2D.AddActor(actorNavigate2D)
  
  renderWindowNavigate2D = vtk.vtkRenderWindow()          
  renderWindowNavigate2D.AddRenderer(rendererNavigate2D)  
  
  if (orientation == "axial"):
    renderWindowNavigate2D.SetSize(dicomImage.GetDimensions()[0], dicomImage.GetDimensions()[1])    
  if (orientation == "coronal"):
    renderWindowNavigate2D.SetSize(dicomImage.GetDimensions()[0], dicomImage.GetDimensions()[2])    
  if (orientation == "sagittal"):
    renderWindowNavigate2D.SetSize(dicomImage.GetDimensions()[1], dicomImage.GetDimensions()[2])    
  

  windowInteractorN2D = vtk.vtkRenderWindowInteractor()
  windowInteractorN2D.SetRenderWindow(renderWindowNavigate2D)     
  
  #Note here how the event is added to the observer. The name of the event is fixed, the name
  #of the function that handles the event is user defined.
  windowInteractorN2D.AddObserver("KeyPressEvent", KeyPressNavigate2D, 1.0)
    
  windowInteractorN2D.Initialize()
  renderWindowNavigate2D.Render()
  windowInteractorN2D.Start()    

  del renderWindowNavigate2D, windowInteractorN2D  
  
def KeyPressNavigate2D(obj, Event):  
  key = obj.GetKeySym()
  limitUp = 0
  limitDown = 0
  
  if (orientation == "axial"):
    limitUp = dicomImage.GetDimensions()[2] - 1       
  if (orientation == "coronal"):
    limitUp = dicomImage.GetDimensions()[1] - 1         
  if (orientation == "sagittal"):
    limitUp = dicomImage.GetDimensions()[0] - 1          
	
  global zSlice 	
        
  if (key == "Up"):       
    zSlice = zSlice + 1
    if (zSlice > limitUp):
      zSlice = limitUp
        
  if (key == "Down"):       
    zSlice = zSlice - 1
    if (zSlice < 0):
      zSlice = 0         

  mapperNavigate2D.SetZSlice(zSlice)         
  renderWindowNavigate2D.Render()           
  
 
# This is the body of the main program. 
# It defines an infinite loop that prints the menu and reads an option that the user will choose.
# You must start by reading the image, before trying to navigate it.
while True:
  print("---------------------------Main menu---------------------------")
  print("Please, choose an option")
  print("1 Indicate DICOM image directory path.")
  print("2 Navigate 2D slices.")
  print("q Quit.")
  optionUser = input("?: ")  
  
  if (optionUser == "q"):
    break
  
  if (optionUser == "1"):
    ReadDicom()  
    
  if (optionUser == "2"):
    Navigate2D()     