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
import sys
    
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
        
        imageFile = input("Please input nifti file path or DICOM folder path:\n " )
        
        if (len(sys.argv) == 2):
            imageFile = sys.argv[1]
            print("Using " + os.path.splitext(imageFile)[0] + ' as image to read')
        elif os.path.exists(imageFile):
            print("Using " + os.path.splitext(imageFile)[0] + ' as image to read')
        else:
            imageFile = 'headGaussian.nii'
            print("Inappropriate input. Using " + imageFile + ' as default.')
            
        if (not os.path.exists(imageFile)):
        	print("ERROR: " + imageFile + " does not exist!")
        	sys.exit()
        

        # asserts this is a directory appropriate for DICOM reading
        if (os.path.isdir(imageFile)):
        	reader = vtk.vtkDICOMImageReader()
        	reader.SetDirectoryName(imageFile)
        # asserts this is a file appropriate for nifti reading
        else:
        	ext = os.path.splitext(imageFile)[1]
        	if (ext == ".nii" or ext == ".nifti"):
        		reader = vtk.vtkNIFTIImageReader()
        		reader.SetFileName(imageFile)
        	else:
        		print("ERROR: image format not recognized for " + imageFile)
        		sys.exit()
        
        reader.Update()
            
        find = False
            
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
    infoText.SetInput("Scroll up or down to navigate through the slices. \n")
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
    
    # Connect an interactor to the image viewer
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    
    # function to change projected image slice with key press            
    # Add observers for mouse wheel events to scroll through slices
    def wheelForward(obj, event):
        zSlice = mapper.GetZSlice()
    	
        if (zSlice < mapper.GetWholeZMax()):
            mapper.SetZSlice(zSlice + 1)
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        txt.SetInput(outputText1)
            
    def wheelBackward(obj, event):
        zSlice = mapper.GetZSlice()
        
        if (zSlice > mapper.GetWholeZMin()):
            mapper.SetZSlice(zSlice - 1)
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        txt.SetInput(outputText1)    
    
    # add the scrolling events to move through slices    
    iren.AddObserver("MouseWheelForwardEvent", wheelForward)
    iren.AddObserver("MouseWheelBackwardEvent", wheelBackward)
    
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
