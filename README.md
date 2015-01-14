# ballin-octo-cyril
Image classification with pybrain
by Brian Cole

This was originally a project for class (CS 344, AI); it uses a neural network to classify images, given images to pattern off of. For instance, if you have directories full of images of goats and whales, and a directory full of images of assorted mammals:

.
./goats
./goats/babyGoat.jpg
./goats/rammingRam.png
./goats/fakeSheep.jpeg
./whales
./whales/bigBlue.png
./whales/greatWhite.jpg
./whales/helloGround.png
./unknown
./unknown/bigBlueThing.png
./unknown/whiteFurryThing.png
./unknown/brownFurryThing.png
./unknown/cat.png
./probablyGoats
./probablyWhales

Then you should be able to run the command

recognizer5.py goats whales unknown probablyGoats probablyWhales

and end up with the contents of unknown/ moved into probablyGoats and probablyWhales as is appropriate. The cat will probably end up with the goats, since the neural network will always say that an image is closer to one category or the other.
