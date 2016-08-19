#def generate_grid(gridPath):
#CHECKING GRID FILE PATH
import os
import math
import PyQt4.QtGui
import PyQt4.QtCore

#READ IN FILES AND GETTING INFO
filepath = 'C:\Users\Dumex\Desktop\OutputData\grid_size00025_tags.csv'

f = open(filepath, 'r')
lines = f.read().splitlines()
y = lines.__len__()
x = lines[3].split(';').__len__()
tags_array =[[0 for i in range (0,x)] for i in range (0,y)]
print tags_array

for i in range (0, y):
    line = lines[i].replace(',',' ')
    tags = line.split(';')
    for n in range (0, x):
        tag = tags[n]
        tags_array[i][n] = tag

print tags_array