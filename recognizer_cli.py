#! /usr/bin/env python2

# classifies pictures using a neural network
# takes 2 training directories, 1 directory to classify, and 2 output directories
# Brian Cole

import os
import sys
from sys import argv
import shutil

from recognizer import Brain

#initialize a netword and such
brain = Brain()

#provide it with samples
for f in os.listdir(argv[1]):
	print("adding file", os.path.join(argv[1], f), "to dataset as part of group 0")
	brain.addSampleImageFromFile(os.path.join(argv[1], f), 0)
for f in os.listdir(argv[2]):
	print("adding file", os.path.join(argv[2], f), "to dataset as part of group 1")
	brain.addSampleImageFromFile(os.path.join(argv[2], f), 1)

#train the network on the datasets
brain.train()

#save network
brain.save("recognizernet.brain")

#run and actually use the network to evaluate the test images
for f in os.listdir(argv[3]):
	sys.stdout.write("Classifying file ")
	sys.stdout.write(os.path.join(argv[3], f))
	if brain.classify(os.path.join(argv[3], f)) == 0:
		sys.stdout.write(" is a member of group ")
		print(os.path.join(argv[1]))
		shutil.move(os.path.join(argv[3], f), argv[4])
	else:
		sys.stdout.write(" is a member of group ")
		print(os.path.join(argv[2]))
		shutil.move(os.path.join(argv[3], f), argv[5])

