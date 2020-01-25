#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDSC 689.03
Assignment #1: How to load and display a 3D medical image

Inputs: when prompted, a path to a NIFTI image or DICOM image directory
        these images do NOT need to be in the working directory

This code will display a single set of DICOM or NIFTI medical images independent
of the Python working directory.

It requires only that you have a DICOM directory path containing only one set
of DICOM images or a NIFTI image file path.

Last edited on Fri Jan 24 2020

@author: MattD

"""

#import packages required
import vtk   
from pathlib import Path
import os
     
    
# =============================================================================
# Prompts the user for the file location of the images to read
# Checks to see if the file or directory is useable
# Returns the useable path of the file (NIFTI) or directory (DICOM) to use
# This allows the lcoation of the file(s) used to be independent of the working directory
# =============================================================================
def readImages():
    
    # dummy variable to run the while loop
    find = True
    
    # define the variables to determine the location of DICOM directory or NIFTI file
    while find == True:
        
        # ask user if they want to read DICOM images or NIFTI images

        print("\nDo you wish to read and display DICOM or NIFTI type files? \n")
        print("Press 'D' for DICOM, 'N' for NIFTI, or 'ctrl-c' to terminate")
    
        answer = input("[D]/[N]: ")
        
        # getting NIFTI image file
        if answer == 'n' or answer == 'N':
            imageFile = input("Input the path where the NIFTI image file is stored: \n\n")
            
            # checks to make sure the file and path specified is a NIFTI file
            if not Path(imageFile).suffix == '.nii' or Path(imageFile).suffix == '.nifti':
                raise Exception("The file or path specified is inappropriate. Please try again.")
            if not os.path.exists(imageFile):
                raise Exception("The file or path specified is inappropriate. Please try again.")
            
            # setup the reader object
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(imageFile)
            reader.Update()
            
            find = False
        
        # getting DICOM images directory
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
# Includes information about about image slice and image windowing.
#
# Input: an intialised vtkImageReader object 
# 
# Eventual wants: display patient id, patient position, image number, window level 
# =============================================================================
def displayImages(reader):  
       
    imageData = reader.GetOutput() # get the image data
    coordBounds = imageData.GetDimensions() # this gives minx, maxx, miny, maxy, minz, maxz coordinate numbers
    
    # print(imageData)
    print(coordBounds)  
        
    midx = int(coordBounds[0]/2)
    midy = int(coordBounds[1]/2)
    midz = int(coordBounds[2]/2)
    
    # initialise the mapper. The image displayed will be the middle image in the image set
    mapper = vtk.vtkImageMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetZSlice(midz)
    mapper.SetColorWindow(1000) # sets window level
    mapper.SetColorLevel(100) # sets color level
    
    # create the actor
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    actor.SetPosition(midx, midy)
    
    # create text actor
    txt = vtk.vtkTextActor()
    txt.SetInput("Current slice: " + str(mapper.GetZSlice()) + " of " + str(coordBounds[2]) + '\n'
                 'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(30)
    txtprop.SetColor(1,1,1)
    txt.SetDisplayPosition(int(midx/2),5)
    
    # create second text actor
    infoText = vtk.vtkTextActor()
    infoText.SetInput("Press the 'up' or 'down' arrow keys to navigate through the slices. \n"
                      "Remember to click with your mouse to update the displayed image.")
    infotxtprop=infoText.GetTextProperty()
    infotxtprop.SetFontFamilyToArial()
    infotxtprop.SetFontSize(20)
    infotxtprop.SetColor(1,1,1)
    infoText.SetDisplayPosition(int(midx/2), coordBounds[1]*2 - 100)
    
    # create the renderer
    ren = vtk.vtkRenderer()
    
    # create the render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(coordBounds[0]*5,coordBounds[1]*2)
    
    # create the window interactor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    def imageScroll(obj, env):
        direction = iren.GetKeySym()
        
        if direction == 'Up':
            mapper.SetZSlice(mapper.GetZSlice() + 1)
            txt.SetInput("Current slice: " + str(mapper.GetZSlice()) + " of " + str(coordBounds[2]) + '\n'
                 'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        elif direction == 'Down':
            mapper.SetZSlice(mapper.GetZSlice() - 1)
            txt.SetInput("Current slice: " + str(mapper.GetZSlice()) + " of " + str(coordBounds[2]) + '\n'
                 'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
    
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

# imagePathN = '/Users/MattD/Projects/courses/MDSC-689.03/W01_vtk_intro/W01_Assignment/NIFTI/head.nii'
# imagePathD = '/Users/MattD/Projects/courses/MDSC-689.03/W01_vtk_intro/W01_Assignment/DICOM/Hip'

displayImages(reader)
