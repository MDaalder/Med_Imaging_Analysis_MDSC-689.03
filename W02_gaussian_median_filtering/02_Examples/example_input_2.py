# Example to demonstrate how to use the Argument Parser (argparse)
#
# Example Command Line:
# 	python example_input_2.py -h
#	python example_input_2.py input_file
# 	python example_input_2.py input_file --arg_1 50
#	python example_input_2.py input_file --arg_1 5 --arg_2 0.1 0.1 0.1 --arg_3
####################

# Begin Script

##
# load package
import argparse

##
# Establish argument parser and give script description
parser = argparse.ArgumentParser(
    description = """This script is an example of how to use the argument parser.""")

##
# Set up required arguments
parser.add_argument("input")    # input file for script
# parser.add_argument("input_2")
# parser.add_argument("output")     # any number of required arguments as needed

##
# Set up optional arguments, have pre-defined default values
parser.add_argument("--arg_1", type = int, default = 1,
    help = "Argument 1 is an integer value. (default: %(default)s)")
parser.add_argument("--arg_2", nargs = "+", type = float, default = [0.08, 0.08, 0.08],
    help = "Argument 2 is type float and has multiple values. (default: %(default)s)")
parser.add_argument("--arg_3", action = 'store_true', default = False,
    help = "Argument 3 is an action.  Useful to turn script functions on or off. (default: %(default)s)")

##
# Define input arguments to easy names for reference
args = parser.parse_args()

file = args.input
# file_2 = args.input_2
# output_file = args.output
arg_1 = args.arg_1
arg_2 = args.arg_2
arg_3 = args.arg_3

##
# Print the arguments to terminal
print ("Input: ", file)
# print "Input 2: ", file_2
# print "output_file: ", output_file
print ("Arg_1: ", arg_1)
print ("Arg_2: ", arg_2)

# If argument 3 is True (--arg_3 in command line --> action stores True)
if (arg_3):
    print ("Arg_3: ", arg_3)

# End Script
