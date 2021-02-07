# Example script to input arguments using method 1 (sys.argv)
# Prints out input arguments in command prompt.

# Example command line: python example_input_1.py arg_1 arg_2 arg_3 arg_4 arg_5

# Load package
import sys

# Check number of inputs
# sys.argv is a list containing the command line arguments, with sys.argv[0] = name of the script
if len(sys.argv) != 6:
    print ("Incorrect input. Use: python example_input_1.py fileName arg_1 arg_2 arg_3 arg_4 arg_5")
    sys.exit()

# Define input arguments to variables
input_file = sys.argv[1]
arg_2 = sys.argv[2]
arg_3 = sys.argv[3]
arg_4 = sys.argv[4]
arg_5 = sys.argv[5]

# print out arguments
print ("Input File: ", input_file)
print ("arg_2: ", arg_2)
print ("arg_3: ", arg_3)
print ("arg_4: ", arg_4)
print ("arg_5: ", arg_5)
