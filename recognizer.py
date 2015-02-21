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


def avgColor(myImage, minX, minY, maxX, maxY, pixelArray=None):
	"avgColor returns the average color from a section of a picture"
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
	"""twelveToneParallel returns the average colors of the four quadrants of an image, as concatenated RGB color values (hence 12 tones)
	The difference from twelveTone is that it uses the multiprocessing module to run all four quadrants in parallel"""
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
	"twelveTone returns the average colors of the four quadrants of an image, as concatenated RGB color values (hence 12 tones)"
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


class Brain:
	def __init__(self, hiddenNodes = 30):
		# construct neural network 
		self.myClassifierNet = buildNetwork(12, hiddenNodes, 1, bias=True, hiddenclass=TanhLayer) #parameters to buildNetwork are inputs, hidden, output
		# set up dataset
		self.myDataset = SupervisedDataSet(12, 1)
		self.myClassifierTrainer = BackpropTrainer(self.myClassifierNet, self.myDataset)

	def addSampleImageFromFile(self, imageFile, groupId):
		"adds a data sample from an image file, including needed processing"
		myImage = Image.open(imageFile)
		self.myDataset.addSample(twelveToneParallel(myImage), (groupId,))

	def train(self):
		#myClassifierTrainer.trainUntilConvergence() #this will take forever (possibly literally in the pathological case)
		for i in range(0, 15):
			self.myClassifierTrainer.train() #this may result in an inferior network, but in practice seems to work fine

	def save(self, saveFileName="recognizernet.brain"):
		saveFile = open(saveFileName, 'w')
		pickle.dump(self.myClassifierNet, saveFile)
		saveFile.close()

	def load(self, saveFileName="recognizernet.brain"):
		saveFile = open(saveFileName, 'r')
		myClassifierNet = pickle.load(saveFile)
		saveFile.close()

	def classify(self, fileName):
		myImage = Image.open(fileName)
		if self.myClassifierNet.activate(twelveToneParallel(myImage)) < 0.5:
			return 0
		else:
			return 1

