# MDSC 689.03
# Advanced Medical Image Processing
#
# Example W3.B - Interactive image selection and image zoom
# Created by Danielle Whittier
# January 31, 2020
#
# --------------------------------------------
#
# Opens a NIFTI or DICOM interactively using the tkinter package
# Image file does not need tobe specified, a window will pop up
# Image size can be scaled usign and slice number can be selected
# Scrolls through z-slices using mouse scroll functionality
#
# --------------------------------------------
#
# Example command line to run the script
#
#    python image_open_and_zoom.py -s 150 -z 3
#
# --------------------------------------------
#

import vtk
import sys
import os
import argparse

# package used to show a nice GUI to select your image instead of using commandline
# Install in anaconda with conda install tk, for python 2.7 only. 
# The name of the package may vary in other versions.
import tkinter
import tkinter.filedialog 


# Establish argument parser and give script description
parser = argparse.ArgumentParser(
    description = """This program opens the image file onthe specified slize and scales the image to the specified zoom""")
parser.add_argument("-s", type = int, default = 100,
    help = "s is the slice number. (default: %(default)s)")
parser.add_argument("-z", type = int, default = 1,
    help = "z is the zoom factor to scale the image size. (default: %(default)s)")

# Get your arguments
args = parser.parse_args()
slice = args.s
zoom = args.z

#Show your nice GUI to get the input file
root = tkinter.Tk()
root.withdraw()
imagefile = tkinter.filedialog.askopenfilename()

#extract the file extension
ext = os.path.splitext(imagefile)[1]

# Initiate image reader
reader = vtk.vtkImageReader()

# Check if you are reading either DICOM or nifti
# if the file extension is a DICOM, then used the DICOM reader
if (ext == ".dcm"):
    imagedir = os.path.dirname(imagefile)
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(imagedir)

else:
	if (ext == ".nii" or ext == ".nifti"):
		reader = vtk.vtkNIFTIImageReader()
		reader.SetFileName(imagefile)
	else:
		print(("ERROR: image format not recognized for " + imagefile))
		sys.exit()
 	
reader.Update()
image = reader.GetOutput()


#Resize the image in the x and y axis, leave z axis as-is
resize = vtk.vtkImageResize()
resize.SetInputData(image)
resize.SetResizeMethodToMagnificationFactors()
resize.SetMagnificationFactors(zoom,zoom,0)
resize.Update()

#initiate image viewer with resized image
viewer = vtk.vtkImageViewer()
viewer.SetInputConnection(resize.GetOutputPort())
viewer.SetZSlice(slice)

# Connect an interactor to the image viewer
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
viewer.SetupInteractor(iren)

#Create user functions to allow for slice scrollthrough capability
#allows for mouse scroll or left/righ mouse clicks to navigate through images
def ScrollFwd(obj, ev):
    zSlice = viewer.GetZSlice()
    zSlice = zSlice + 1
    viewer.SetZSlice(zSlice)

def ScrollBwd(obj, ev):
    zSlice = viewer.GetZSlice()
    zSlice = zSlice - 1
    viewer.SetZSlice(zSlice)

iren.AddObserver("MouseWheelForwardEvent",ScrollFwd,1.0)
iren.AddObserver("MouseWheelBackwardEvent",ScrollBwd,1.0)


#Launch
viewer.Render()
iren.Start()

