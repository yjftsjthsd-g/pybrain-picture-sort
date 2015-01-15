#! /usr/bin/env python2

# classifies pictures using a neural network
# takes 2 training directories, 1 directory to classify, and 2 output directories
# Brian Cole

import os
import sys
from sys import argv
from PIL import Image
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain import TanhLayer
import pickle
from multiprocessing import Process, Pipe
import shutil

def avgColor(myImage, minX, minY, maxX, maxY, pixelArray=None):
	if pixelArray==None:
		pixelArray = myImage.load()
	cumulativeCounts = [0, 0, 0]
	pixelsCounted = 0
	for x in range(minX, maxX):
		for y in range(minY, maxY):
			#cumulativeCounts += pixelArray[x, y]
			cumulativeCounts[0] += pixelArray[x, y][0]
			cumulativeCounts[1] += pixelArray[x, y][1]
			cumulativeCounts[2] += pixelArray[x, y][2]
			pixelsCounted += 1
	return [cumulativeCounts[0]/pixelsCounted, cumulativeCounts[1]/pixelsCounted, cumulativeCounts[2]/pixelsCounted]

def twelveToneParallel(myImage):
	pa=myImage.load()
	def getAvgColor(conn, myImage, minX, minY, maxX, maxY,pa):
		conn.send(avgColor(myImage, minX, minY, maxX, maxY, pixelArray=pa))
		conn.close()
	
	#TODO I'd like to try interleaving so that we kick each process off before moving on to setting up the next
	# but test that and see if it's actually faster; this version is clearer
	pipea_parent, pipea_child = Pipe()
	pipeb_parent, pipeb_child = Pipe()
	pipec_parent, pipec_child = Pipe()
	piped_parent, piped_child = Pipe()

	proca = Process(target=getAvgColor, args=(pipea_child, myImage, 0, 0, myImage.size[0]/2, myImage.size[1]/2,pa))
	procb = Process(target=getAvgColor, args=(pipeb_child, myImage, myImage.size[0]/2, 0, myImage.size[0], myImage.size[1]/2,pa))
	procc = Process(target=getAvgColor, args=(pipec_child, myImage, 0, myImage.size[1]/2, myImage.size[0]/2, myImage.size[1],pa))
	procd = Process(target=getAvgColor, args=(piped_child, myImage, myImage.size[1]/2, myImage.size[1]/2, myImage.size[0], myImage.size[1],pa))

	proca.start()
	procb.start()
	procc.start()
	procd.start()

	a = pipea_parent.recv()
	b = pipeb_parent.recv()
	c = pipec_parent.recv()
	d = piped_parent.recv()
	proca.join()
	procb.join()
	procc.join()
	procd.join()
	#a = avgColor(myImage, 0, 0, myImage.size[0]/2, myImage.size[1]/2)
	#b = avgColor(myImage, myImage.size[0]/2, 0, myImage.size[0], myImage.size[1]/2)
	#c =  avgColor(myImage, 0, myImage.size[1]/2, myImage.size[0]/2, myImage.size[1])
	#d =  avgColor(myImage, myImage.size[1]/2, myImage.size[1]/2, myImage.size[0], myImage.size[1])
	return [
			a[0], a[1], a[2],
			b[0], b[1], b[2],
			c[0], c[1], c[2],
			d[0], d[1], d[2]
			]

def twelveTone(myImage):
	a = avgColor(myImage, 0, 0, myImage.size[0]/2, myImage.size[1]/2)
	b = avgColor(myImage, myImage.size[0]/2, 0, myImage.size[0], myImage.size[1]/2)
	c =  avgColor(myImage, 0, myImage.size[1]/2, myImage.size[0]/2, myImage.size[1])
	d =  avgColor(myImage, myImage.size[1]/2, myImage.size[1]/2, myImage.size[0], myImage.size[1])
	return [
			a[0], a[1], a[2],
			b[0], b[1], b[2],
			c[0], c[1], c[2],
			d[0], d[1], d[2]
			]

# load network  
saveFile = open("recognizernet.brain", 'r')
myClassifierNet = pickle.load(saveFile) 
saveFile.close() 

#output
#print myClassifierNet.activate(twelveTone(testImage))

# run and actually use the network to move the test images
for f in os.listdir(argv[1]):
	sys.stdout.write("Classifying file ")
	sys.stdout.write(os.path.join(argv[1], f))
	myImage = Image.open(os.path.join(argv[1], f))
	if myClassifierNet.activate(twelveToneParallel(myImage)) < 0.5:
		print(" into ", argv[2])
		shutil.move(os.path.join(argv[1], f), argv[2])
	else:
		print(" into ", argv[3])
		shutil.move(os.path.join(argv[1], f), argv[3])

