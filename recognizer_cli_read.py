#! /usr/bin/env python2

# classifies pictures using a saved neural network
# takes 2 training directories, 1 directory to classify, and 2 output directories
# Brian Cole

import os
import sys
from sys import argv
import shutil

from recognizer import Brain

#initialize a netword and such
brain = Brain()

#load network state
brain.load("recognizernet.brain")

#run and actually use the network to evaluate the test images
for f in os.listdir(argv[1]):
	sys.stdout.write("Classifying file ")
	sys.stdout.write(os.path.join(argv[1], f))
	if brain.classify(os.path.join(argv[1], f)) == 0:
		sys.stdout.write(" is a member of group ")
		print(os.path.join(argv[2]))
		shutil.move(os.path.join(argv[1], f), argv[2])
	else:
		sys.stdout.write(" is a member of group ")
		print(os.path.join(argv[3]))
		shutil.move(os.path.join(argv[1], f), argv[3])

