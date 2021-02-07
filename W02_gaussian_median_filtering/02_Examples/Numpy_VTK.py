# This is an example of creating a 2D numpy array, converting it to vtk
# and converting back to numpy

# Begin Script

# Libraries
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk


# Create 2D numpy array

numpy_array = np.array([[[0,0], [0,0], [0,255], [0,255], [0,0], [0,0]],
                        [[0,0], [0,0], [0,255], [0,255], [0,0], [0,0]]], np.uint8)

# Print some info on the numpy array
print ("\n")
print ("+++++++++++++++++++++++++")
print ("Numpy Array: \n", numpy_array)
print ("Data type: ", numpy_array.dtype)
print ("Array Shape: ", numpy_array.shape)
print ("Value for numpy_array[1,3]: ", numpy_array[1,3])

# Convery Array to VTK
numpy_array_shape = numpy_array.shape
vtk_data = numpy_to_vtk(num_array = numpy_array.ravel(), deep = True, array_type = vtk.VTK_UNSIGNED_INT)

# Print some info on the VTK array
print ("\n")
print ("+++++++++++++++++++++++++")
print ("VTK Data Array: \n", vtk_data)
for i in range(0, vtk_data.GetNumberOfTuples()):
    print ("Value at Index %d: " % i, vtk_data.GetTuple(i)[0])

print ("\n")
print ("+++++++++++++++++++++++++")

# Convert Array back to numpy Array
numpy_converted = vtk_to_numpy(vtk_data)
numpy_converted = numpy_converted.reshape(numpy_array_shape)

# Print some info on the converted numpy array

print ("Numpy Array: \n", numpy_array)
print ("Data type: ", numpy_array.dtype)
print ("Array Shape: ", numpy_array.shape)
print ("Value for numpy_array[1,3]: ", numpy_array[1,3])
print ("+++++++++++++++++++++++++")
