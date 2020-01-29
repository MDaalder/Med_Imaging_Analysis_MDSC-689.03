"""
MDSC 689.03
Assignment #1: How to load and display a 3D medical image

Inputs: when prompted, a path to a NIFTI image or DICOM image directory
        these images do NOT need to be in the working directory

This code will display a single set of DICOM or NIFTI medical images independent
of the Python working directory.

It requires only that you have a DICOM directory path containing only one set
of DICOM images or a single NIFTI image file path.

Last edited on Jan 25 2020

@author: MattD

"""

#import packages required
import vtk   
from pathlib import Path
import os
    
# =============================================================================
# Prompts the user for the file location of the images to read
# Checks to see if the file or directory is useable
# Returns the useable path of the file (NIFTI) or directory (DICOM) to use as a reader
# This allows the location of the file(s) used to be independent of the working directory
# =============================================================================
def readImages():
    
    # dummy variable to run the while loop
    find = True
    
    # define the variables to determine the location of DICOM directory or NIFTI file
    while find == True:
        
        # ask user if they want to read DICOM images or NIFTI image(s)
        print("\nDo you wish to read and display DICOM or NIFTI type files? \n")
        print("Press 'D' for DICOM, 'N' for NIFTI, or 'ctrl-c' to terminate")
    
        answer = input("[D]/[N]: ")
        
        # getting NIFTI image file
        if answer == 'n' or answer == 'N':
            imageFile = input("Input the path where the NIFTI image file is stored: \n\n")
            
            # checks to make sure the file and path specified exists and is a NIFTI file
            if not os.path.isfile(imageFile):
                raise Exception("The path specified does not exist. Please try again.")
            if not Path(imageFile).suffix == '.nii' or Path(imageFile).suffix == '.nifti':
                raise Exception("The file or path specified is inappropriate. Please try again.")
            
            # setup the reader object
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(imageFile)
            reader.Update()
            
            find = False
        
        # getting DICOM images directory
        # to-do: check files in dir to be DICOM (.dcm)
        elif answer == 'd' or answer == 'D':
            imageFile = input("Input the path to the directory where the DICOM images are located: \n\n")
            
            # checks to make sure the specified path is a directory    
            if not os.path.isdir(imageFile):
                raise Exception("The path specified is inappropriate. Please try again.")
            
            # setup the reader object
            reader = vtk.vtkDICOMImageReader()
            reader.SetDirectoryName(imageFile) # maybe use SetFileNames or SetFilePrexix because of .DS_Store warning
            reader.Update()
            
            find = False
            
        else:
            None
            
    return (reader)


# =============================================================================
# Display everything in vtk window.
# Includes information about image slice and image windowing.
#
# Input: an intialised vtkImageReader object 
# 
# Eventual wants: display patient id, patient position, and automatic center positioning of medical images 
# =============================================================================
def displayImages(reader):  
    
    # Gets all image data
    imageData = reader.GetOutput()
    
    # Extracting the dimensions of the image 
    coordBounds = imageData.GetDimensions() # this gives maxx, maxy, maxz coordinate numbers
    
    # assigning dimension variables in case want to use for sizing and positioning actors and windows   
    # in the future, would want to assign location and sizing of objects by local screen resolution
    xdim = int(coordBounds[0])
    ydim = int(coordBounds[1])
    zdim = int(coordBounds[2])
    
    # can be used to display information
    # print(imageData)
    # print('x dimension: 1-> ' + str(xdim) + ' y dimension: 1->' + str(ydim) +' number of slices: ' + str(zdim))  
     
    # initialise the mapper. The image displayed will be the middle image in the image set
    mapper = vtk.vtkImageMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetZSlice(int(zdim/2))
    mapper.SetColorWindow(1000)
    mapper.SetColorLevel(200)
    
    # create the actor
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    actor.SetPosition(100, 170)
    
    # assign text to display: current slice and window level and color level
    outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                  'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
    
    # create text actor
    txt = vtk.vtkTextActor()
    txt.SetInput(outputText1)
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(30)
    txtprop.SetColor(1,1,1)
    txt.SetDisplayPosition(10,30)
    
    # create second text actor
    infoText = vtk.vtkTextActor()
    infoText.SetInput("Press the 'up' or 'down' arrow keys to navigate through the slices. \n"
                      "Click with your mouse to update the displayed image.")
    infotxtprop=infoText.GetTextProperty()
    infotxtprop.SetFontFamilyToArial()
    infotxtprop.SetFontSize(20)
    infotxtprop.SetColor(1,1,1)
    infoText.SetDisplayPosition(10, 15)
    
    # create the renderer
    ren = vtk.vtkRenderer()
    
    # create the render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(800, 700)

    # create the window interactor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    
    # function to change projected image slice with key press
    # to-do: make sure displayed slice meets this criteria: minSlice <= currentSlice <= maxSlice
    # to-do: change window and color level with mouse drag or left/right key press
    def imageScroll(obj, env):
        direction = iren.GetKeySym()

        if direction == 'Up' and (mapper.GetZSlice()) < (zdim-1): #getzslice returns 0<->#, zdim returns 1<->#+1
            mapper.SetZSlice(mapper.GetZSlice() + 1)
        elif direction == 'Down' and mapper.GetZSlice() > (zdim-zdim):
            mapper.SetZSlice(mapper.GetZSlice() - 1)
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                  'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        txt.SetInput(outputText1)
    
    # initialize the key press event to scroll through images
    iren.AddObserver("KeyPressEvent", imageScroll, 1.0)
    
    # add the actors to the renderer
    ren.AddActor(actor)
    ren.AddActor(txt)
    ren.AddActor(infoText)
    
    # initialise the interactor
    iren.Initialize()
    
    # render the scene with all actors in it
    renWin.Render()
    
    # Start the event loop for the interactor
    iren.Start()
    
    
    return()

reader = readImages()

displayImages(reader)
