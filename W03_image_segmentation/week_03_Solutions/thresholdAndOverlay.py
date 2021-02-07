# -------------------------------------
# BMEN 619.14 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Assignment #3
#	Author:	Renzo Phellan
#	Date:	January, 2017
#
#   Modified to python 3
#   Jan 31 2020
#   Danielle Whittier
# -------------------------------------
# How to run example: python thresholdAndOverlay.py -lt 0 -ut 100
# a window will pop up to select the image file to use

import vtk
import sys
import os
# argparser functions
import argparse
# timestamp functions, to calculate the run time of your program
import time
# Require to show a nice GUI to input your image name path
# Install in anaconda with conda install tk, for python 2.7 only. 
# The name of the package may vary in other versions.
import tkinter
import tkinter.filedialog 

#Store the start time of the program
startTime = time.time()

# Establish argument parser and give script description
parser = argparse.ArgumentParser(
    description = """This program applies global threshold to segment an image and overlays the result on the original for display.""")
parser.add_argument("-lt", type = int, default = 0,
    help = "Lt is the lower threshold. (default: %(default)s)")
parser.add_argument("-ut", type = int, default = 100,
    help = "ut is the upper threshold. (default: %(default)s)")
parser.add_argument("-s", type = int, default = 100,
    help = "s is the slice number. (default: %(default)s)")

# Get your arguments
args = parser.parse_args()
lowerT = args.lt
upperT = args.ut
slice = args.s

#Show your nice GUI to get the input file
root = tkinter.Tk()
root.withdraw()
imagefile = tkinter.filedialog.askopenfilename()
print(imagefile)

# Check if you are reading either DICOM or nifti
reader = vtk.vtkImageReader()
if (os.path.isdir(imagefile)):
	reader = vtk.vtkDICOMImageReader()
	reader.SetDirectoryName(imagefile)
else:
	ext = os.path.splitext(imagefile)[1]
	if (ext == ".nii" or ext == ".nifti"):
		reader = vtk.vtkNIFTIImageReader()
		reader.SetFileName(imagefile)
	else:
		print(("ERROR: image format not recognized for " + imagefile))
		sys.exit()
 	
reader.Update()
medicalImage = reader.GetOutput()

#!!! Create a copy, in order not to destroy the original
#Notice the result is a binary image (either 0 or 1)
resultBinaryImage = vtk.vtkImageData()
resultBinaryImage.DeepCopy(medicalImage)    
inRangeValue = 1
outRangeValue = 0

#Iterate every voxel to apply the threshold
for x in range(0, medicalImage.GetDimensions()[0]):
	for y in range(0, medicalImage.GetDimensions()[1]):
		for z in range(0, medicalImage.GetDimensions()[2]):
			voxelValue = medicalImage.GetScalarComponentAsFloat(x, y, z, 0)
			if (voxelValue < lowerT):
				resultBinaryImage.SetScalarComponentFromFloat(x, y, z, 0, outRangeValue)		   
			elif ((voxelValue >= lowerT) and (voxelValue <= upperT)):
				resultBinaryImage.SetScalarComponentFromFloat(x, y, z, 0, inRangeValue)		   
			elif (voxelValue > upperT):
				resultBinaryImage.SetScalarComponentFromFloat(x, y, z, 0, outRangeValue)		   
				
print(("Execution time: %8.2f seconds." % (time.time() - startTime)))				

#In general, overlaying one image over the other requires 2 actors.
#Define a LookupTable to set the color of your overlay
lookupTable = vtk.vtkLookupTable()    
lookupTable.SetNumberOfTableValues(2)
lookupTable.SetRange(0.0,1.0)
lookupTable.SetTableValue( outRangeValue, 0.0, 0.0, 0.0, 0.0 ) #label outRangeValue is transparent
lookupTable.SetTableValue( inRangeValue, 0.0, 1.0, 0.0, 1.0 )  #label inRangeValue is opaque and green
lookupTable.Build()				

# Color your segmentation
mapToColors = vtk.vtkImageMapToColors()    
mapToColors.SetLookupTable(lookupTable)
mapToColors.PassAlphaToOutputOn()
mapToColors.SetInputData(resultBinaryImage)  
				
mapperSegm = vtk.vtkImageMapper()
mapperSegm.SetInputConnection(mapToColors.GetOutputPort())
mapperSegm.SetColorWindow(1)
mapperSegm.SetColorLevel(1) 
mapperSegm.SetZSlice(slice)

actorSegm = vtk.vtkActor2D()
actorSegm.SetMapper(mapperSegm)        

# Another actor is created for the base image
mapperOriginal = vtk.vtkImageMapper()
mapperOriginal.SetInputData(medicalImage)
mapperOriginal.SetZSlice(slice)
mapperOriginal.SetColorWindow(1000)
mapperOriginal.SetColorLevel(500)       

actorOriginal = vtk.vtkActor2D()
actorOriginal.SetMapper(mapperOriginal)        

# Add both actors to the same renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actorOriginal)
renderer.AddActor(actorSegm)

window = vtk.vtkRenderWindow()          
window.AddRenderer(renderer)  
   #Set the size of the window according to the image size
window.SetSize(resultBinaryImage.GetDimensions()[0], resultBinaryImage.GetDimensions()[1])    

windowInteractor = vtk.vtkRenderWindowInteractor()
windowInteractor.SetRenderWindow(window)     
  
window.Render()
windowInteractor.Start() 				

	
