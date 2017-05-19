#!/home/sherlock/anaconda/envs/Python2/bin/python

# Script to delete all JPEGS other than defaults.
# The defaults are office dogs, a car and a truck.
#
# Run it like this on the command line
#
#   python clean-jpegs.py
#
# Or make it executable
#
#   chmod +x clean-jpegs.py
#
# And execute it like this
#
#   ./clean-jpegs.py
#
# You can also set it up such that this script
# runs automatically every night.
#
# First see if the job already exists by doing.
#
#    crontab -l
#
# If it does, you should see something like this
#
# 0 3 * * * /home/sherlock/workspace/sherlock_demo_short/clean-jpegs.py
#
# This is saying run the script every day at 3 am.
# Look up crontab to understand the format.
#
# If the job does not exist you can add a line like the
# one above to the file that opens when you do
#
#    crontab -e
#

import os

# Get all file names in current directory
all_files = os.listdir(".")

# Get JPEGS to be removed
jpegs_to_remove = [x for x in all_files if x.lower().endswith('.jpg')]

# Defaults
default_jpegs = ['chibi.JPG', 'toby.JPG', 'car.JPG', 'truck.JPG']

# Remove dogs and vehicles from remove list.
# In other words, these won't be removed from filesystem.
# Note that the try is there to deal with the case of
# someone accidentally deleting the default images before
# running this script.
try:
    for jpeg in default_jpegs:
        jpegs_to_remove.remove(jpeg)
except ValueError:
    pass

# Now remove everything
for jpeg in jpegs_to_remove:
    os.remove(jpeg)
    
