#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:36:35 2020

@author: MattD
"""

import vtk
import os
from pathlib import Path

imageFile = "head.nii"
file = 'something.txt'




# vtk.vtkNIFTIImageReader.CanReadFile(filePath)

# try:
#     os.path.exists(file)
#     Path(file).suffix == '.nii' or Path(file).suffix == '.nifti'
# except:
#     print("Try again")
    
# reader = vtk.vtkNIFTIImageReader()
# reader.SetFileName(filePath)
# if reader.CanReadFile(filePath) == False:
#     print("it's false")
    
# else:
#     print("it's true")

reader = vtk.vtkNIFTIImageReader()
reader.SetFileName(imageFile)
reader.Update()

imageData = reader.GetOutput() # assuming this gives minx, maxx, miny, maxy, minz, maxz
dataBounds = imageData.GetDimensions() # assuming this gives minx, maxx, miny, maxy, minz, maxz


print(dataBounds)

midx = int(dataBounds[0]/2)
midy = int(dataBounds[1]/2)
midz = int(dataBounds[2]/2)

WindowX = dataBounds[0]
WindowY = dataBounds[1]

# midx = WindowX/2
# midy = WindowY/2
# midz = 100

# initialise the mapper
mapper = vtk.vtkImageMapper()
mapper.SetInputConnection(reader.GetOutputPort())
mapper.SetZSlice(midz)
mapper.SetColorWindow(1000)
mapper.SetColorLevel(0)

# create the actor
actor = vtk.vtkActor2D()
actor.SetMapper(mapper)
# actor.SetPosition(midx, midy)

# create the renderer
ren = vtk.vtkRenderer()

# create the render window
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(WindowX,WindowY)


# create the window interactor
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# add the actors to the renderer
ren.AddActor(actor)

# initialise the interactor
iren.Initialize()

# render the scene with all actors in it
renWin.Render()

# Start the event loop for the interactor
iren.Start()