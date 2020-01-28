# Example for adding timestamp to a printed line

# Library
import time

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

# Perform loop that prints out timestamp for each iteration of loop
for i in range(0,10):
    message("Iteration number: %d" % i,"additional")
    time.sleep(1) # pause for one second between iterations
