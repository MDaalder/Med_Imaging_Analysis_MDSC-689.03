# -------------------------------------
# BMEN 619 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Assignment #2
#	Author:	Renzo Phellan, adapted from Sonny Chan's code for Assignment 1.
#	Date:	January 199, 2017
# -------------------------------------

import vtk
 
#This program applies either the median or gaussian filter to Nifti and DICOM images

import os
import sys
import vtk

# Parse command line arguments for a file
imagefile = "head.nii"
optionFilter = "median"
if (len(sys.argv) == 3):
	imagefile = sys.argv[1]
	optionFilter = sys.argv[2]
else:
	print ('Specify input image and filter type as argument.')
	print ('(using "' + imagefile + '" as default)' + ' and applying "' + optionFilter + '" filter.')	

if (not os.path.exists(imagefile)):
	print ("ERROR: " + imagefile + " does not exist!")
	sys.exit()

# Read the image data from a NIFTI file or DICOM directory
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

#!!! Create a copy, in order not to destroy the original
resultImage = vtk.vtkImageData()
resultImage.DeepCopy(medicalImage)    
	
if (optionFilter == "median"):
	for x in range(0, medicalImage.GetDimensions()[0]):
		for y in range(0, medicalImage.GetDimensions()[1]):
			for z in range(0, medicalImage.GetDimensions()[2]):
			#Assuming a 3 x 3 x 3 cubic kernel:
				# Consider this to avoid accesing voxels outside of your image
				minX = max(0, x - 1) 
				   #Why +2? The range function does not iterate until the right limit
				maxX = min(medicalImage.GetDimensions()[0], x + 2)
				minY = max(0, y - 1) 
				maxY = min(medicalImage.GetDimensions()[1], y + 2)
				minZ = max(0, z - 1) 
				maxZ = min(medicalImage.GetDimensions()[2], z + 2)
				   #Define an array
				voxelArray = []
				for i in range(minX, maxX):
					for j in range(minY, maxY):		
						for k in range(minZ, maxZ):
						   voxelValue = medicalImage.GetScalarComponentAsFloat(i,j,k,0)    
						   voxelArray.append(voxelValue)
				voxelArray.sort()				
				   #Notice how does this work with even or odd lenght arrays
				medianValue = voxelArray[int(len(voxelArray)/2)]
				resultImage.SetScalarComponentFromFloat(x, y, z, 0, medianValue)		   

if (optionFilter == "gaussian"):
	#Assuming a 3 x 3 x 3 cubic kernel, with values:
	# 1 2 1   2  4 2   1 2 1
	# 2 4 2   4 16 4   2 4 2
	# 1 2 1   2  4 2   1 2 1
	kernel = [[[1, 2, 1], [2, 4, 2], [1, 2, 1]], [[2, 4, 2], [4, 16, 4], [2, 4, 2]], [[1, 2, 1], [2, 4, 2], [1, 2, 1]]]	

	for x in range(0, medicalImage.GetDimensions()[0]):
		for y in range(0, medicalImage.GetDimensions()[1]):
			for z in range(0, medicalImage.GetDimensions()[2]):
				# Consider this to avoid accesing voxels outside of your image
				minX = max(0, x - 1) 
				   #Why +2? The range function does not iterate until the right limit
				maxX = min(medicalImage.GetDimensions()[0], x + 2)
				minY = max(0, y - 1) 
				maxY = min(medicalImage.GetDimensions()[1], y + 2)
				minZ = max(0, z - 1) 
				maxZ = min(medicalImage.GetDimensions()[2], z + 2)							
				sum = 0
				for i in range(minX, maxX):
					for j in range(minY, maxY):		
						for k in range(minZ, maxZ):						   						   
						   voxelValue = medicalImage.GetScalarComponentAsFloat(i,j,k,0)    
						   # Note this operation to match the kernel positions with the image positions
						   # Is it correct?
						   sum += voxelValue * kernel[i - x + 1][j - y + 1][k - z + 1]						   
				#Do not forget to divide to avoid excesively big values
				gaussianAverage = sum / 72.0
				resultImage.SetScalarComponentFromFloat(x, y, z, 0, gaussianAverage)		   
		
mapperNifti = vtk.vtkImageMapper()
mapperNifti.SetInputData(resultImage)
zSlice = input("Please, indicate the slice number: ")
mapperNifti.SetZSlice(int(zSlice))
mapperNifti.SetColorWindow(1000)
mapperNifti.SetColorLevel(500)       

actorNifti = vtk.vtkActor2D()
actorNifti.SetMapper(mapperNifti)        

rendererNifti = vtk.vtkRenderer()
rendererNifti.AddActor(actorNifti)

windowNifti = vtk.vtkRenderWindow()          
windowNifti.AddRenderer(rendererNifti)  
   #Set the size of the window according to the image size
windowNifti.SetSize(resultImage.GetDimensions()[0], resultImage.GetDimensions()[1])    

windowInteractor = vtk.vtkRenderWindowInteractor()
windowInteractor.SetRenderWindow(windowNifti)     
  
windowNifti.Render()
windowInteractor.Start() 
