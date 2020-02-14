# -------------------------------------
# BMEN 619.14 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Modified Assignment #3 for class example using built in VTK functions
# 1) Create a Segmentation and Dilate; 2) Write Segmentation image to output file
# Original Author: Renzo Phellan
# Modified Author: Andrew Michalski
# Date:	February, 2017
# -------------------------------------
# How to run example: python writeSegmentation.py -lt 0 -ut 0

# Load packages
import vtk
import sys
import os
import argparse
import time
import tkinter # Install in anaconda with conda install tk
from tkinter import filedialog

# Function for time stamp
def message(msg, *additionalLines):
    """Print message with time stamp
    The first argument is printed with the a time stamp
    Subsequent arguments are printed one to a line without a time stamp
    """
    print ("%8.2f %s" % (time.time() - start_time, msg))
    for line in additionalLines:
        print (" " * 9 + line)
start_time = time.time()

# Establish argument parser and give script description
parser = argparse.ArgumentParser(
    description = """This program applies global threshold to segment an image and overlays the result on the original for display.""")
parser.add_argument("-lt", type = int, default = 200,
    help = "Lt is the lower threshold. (default: %(default)s)")
parser.add_argument("-ut", type = int, default = 1000,
    help = "ut is the upper threshold. (default: %(default)s)")
parser.add_argument("-s", type = int, default = 100,
    help = "s is the z_slice number. (default: %(default)s)")
parser.add_argument("-w", action = 'store_true', default = False,
    help = "Write the segmented image to an output NIFTI File. (default: %(default)s)")

# Get your arguments
args = parser.parse_args()
lowerT = args.lt
upperT = args.ut
z_slice = args.s
write = args.w

#Show your nice GUI to get the input file
root = tkinter.Tk()
root.withdraw()
imagefile = filedialog.askopenfilename()
message("File Loaded: %s" % imagefile)

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
		print ("ERROR: image format not recognized for " + imagefile)
		sys.exit()

reader.Update()
medicalImage = reader.GetOutput()

# Theshold the image for the Segmentation
message("Thresholding Image Data between %d and %d..." % (lowerT, upperT))
thresh = vtk.vtkImageThreshold()
thresh.SetInputData(medicalImage)
thresh.ThresholdBetween(lowerT, upperT)
thresh.ReplaceInOn()
thresh.SetInValue(1)
thresh.ReplaceOutOn()
thresh.SetOutValue(0)
thresh.SetOutputScalarTypeToFloat()
thresh.Update()

# Dilate the image
message("Dilating the image...")
dilate = vtk.vtkImageDilateErode3D()
dilate.SetInputConnection(thresh.GetOutputPort())
dilate.SetKernelSize(3,3,3)
dilate.SetDilateValue(1)
dilate.SetErodeValue(0)
dilate.Update()

# Write output file
if (write):
    message("Writing segementation to output file...")

    # Determine output file name
    pathname = os.path.dirname(imagefile)
    basename = os.path.basename(imagefile)
    os.chdir(pathname)

    fileName = "mask_image.nii"

    message("Output file %s was written to %s" % (fileName, pathname))
    writer = vtk.vtkNIFTIImageWriter()
    writer.SetInputConnection(dilate.GetOutputPort())
    writer.SetFileName(fileName)
    writer.Write()


# View the images as an overlay.
inRangeValue = 1
outRangeValue = 0
#In general, overlaying one image over the other requires 2 actors.
#Define a LookupTable to set the color of your overlay
lookupTable = vtk.vtkLookupTable()
lookupTable.SetNumberOfTableValues(2)
lookupTable.SetRange(0.0,1.0)
lookupTable.SetTableValue( outRangeValue, 0.0, 0.0, 0.0, 0.0 ) #label outRangeValue is transparent
lookupTable.SetTableValue( inRangeValue, 1.0, 0.0, 0.0, 0.5 )  #label inRangeValue is opaque and green
lookupTable.Build()

# Color your segmentation
mapToColors = vtk.vtkImageMapToColors()
mapToColors.SetLookupTable(lookupTable)
mapToColors.PassAlphaToOutputOn()
mapToColors.SetInputConnection(dilate.GetOutputPort())

mapperSegm = vtk.vtkImageMapper()
mapperSegm.SetInputConnection(mapToColors.GetOutputPort())
mapperSegm.SetColorWindow(1)
mapperSegm.SetColorLevel(1)
mapperSegm.SetZSlice(z_slice)

actorSegm = vtk.vtkActor2D()
actorSegm.SetMapper(mapperSegm)

# Another actor is created for the base image
mapperOriginal = vtk.vtkImageMapper()
mapperOriginal.SetInputData(medicalImage)
mapperOriginal.SetZSlice(z_slice)
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
window.SetSize(medicalImage.GetDimensions()[0], medicalImage.GetDimensions()[1])

windowInteractor = vtk.vtkRenderWindowInteractor()
interactorStyle = vtk.vtkInteractorStyleImage()
interactorStyle.SetInteractionModeToImage3D()
windowInteractor.SetInteractorStyle(interactorStyle)
window.SetInteractor(windowInteractor)

window.Render()
windowInteractor.Start()
