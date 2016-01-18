from imp import reload
import numpy as np
import re
import math
import os
import time

def act():
	p = Parser()
	p.parseFile()
	return p
#simplified for comparision of thwo fingerprints use this to test
def act2(firstFP, secondFP, rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold):
	np.set_printoptions(threshold=1000000)
	a = FPAnalyzer()
	a.setValues(rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold)
	if a.compare(firstFP,secondFP):
		print("same fingerprint")
	else:
		print("different fingerprint")
	#return a.applyRotation([1,1],90)

#simplified to calculate a Matrix and prints the success and returns the matching
def act3(rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold):
	a = FPAnalyzer()
	a.setValues(rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold)
	matrix = a.calculateMatchingMatrix()
	print(matrix[1])
	return matrix

#use this function to calculate a matrix over all fingerprints and write them to the output Folder
#It doesn't overwrite nothing because it creates Folders based on the current Timestamp
def buildMatrix(rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold):
	a = FPAnalyzer()
	a.setValues(rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold)
	#result = a.calculateMatchingMatrix()
	result = [[1,4,2],[10,11,14],[20,28,29]]
	currOutput = "C:/Users/Marc/SkyDrive/BFH2014/Biometrie/Kursaufgabe/fpAnalyser/output/" + str(time.time())
	if not os.path.exists(currOutput):
		os.makedirs(currOutput)
	fParams = open(currOutput + "/params.txt" ,'w+')
	fSucess = open(currOutput + "/matches.txt" ,'w+')
	fFail = open(currOutput + "/nonMatches.txt" ,'w+')
	fAll = open(currOutput + "/all.txt" ,'w+')
	fSucess.write(str(result[1]))
	fFail.write(str(result[2]))
	fAll.write(str(result[0]))
	s = "Rotation: " + str(rotationAngle)
	s = s + " Rotate steps: " + str(rotationSteps)
	s = s + " Coordinate treshold: " + str(coordTreshold)
	s = s + " Nr of matches required: " + str(vectorMatchTreshold)
	fParams.write(s)

#Only use these Functions:
#	setValue() to initiate
#	calculateMatchingMatrix() to calculate a Matrix with all FP matches. use only if you have a LOT of time
#	
class FPAnalyzer:

	def __init__(self):
		self.p = Parser()
		self.p.parseFile()
		self.rotationAngle = 1
		self.rotationSteps = 1
		self.coordTreshold = 10
		self.vectorMatchTreshold = 5

	#sets the Parameters.
	#until which angle of rotation does the algorithm try in which iteration steps?
	#How large can be de differences of the coordinates from the Minutiae in the Vectors
	#How many matches have to be found until it is considered the same fingerprint?
	def setValues(self, rotationAngle, rotationSteps, coordTreshold, vectorMatchTreshold):
		self.rotationAngle = rotationAngle
		self.rotationSteps = rotationSteps
		self.coordTreshold = coordTreshold
		self.vectorMatchTreshold = vectorMatchTreshold

	#Calcualtes a matching Matrix based on the parameters over all fingerprints.
	#be aware that the average execution time will be computed as follows as all FP are matched:
	# (60*(60-1) / 2) * 100000 ^ rotationSteps
	#so prepare to wait for a looooong time
	def calculateMatchingMatrix(self):
		nrFPTemp = len(self.p.headers)
		toMatch = []
		for i in range(0,nrFPTemp):
			for c in range(0,nrFPTemp):
				toMatch.append([i, c])
		toMatch = self.removeDupicateEntries(toMatch,nrFPTemp)
		return self.dispatchComparision(toMatch)



	#Just executes 100000 ^ rotationSteps operations to calculate if a fingerprint is the same as another
	#Compares two fingerprints based on the parameters from setValues and returns a boolean wheter they are the same
	def compare(self,firstFP, secondFP):
		matrix = self.buildVectorMatrix(firstFP)
		matrix2 = self.buildVectorMatrix(secondFP)
		matches = self.comparision(matrix,matrix2, firstFP, secondFP)
		#realMatches = self.evaluateMatches(matches,matrix,matrix2,firstFP,secondFP)
		print("count real matches")
		print(len(matches))
		if len(matches) > self.vectorMatchTreshold:
			return True
		else:
			return False


	def evaluateMatches(self, matches, matrix, matrix2, firstFP, secondFP):
		minutiae = self.p.headers[firstFP].minutiae
		minutiae2 = self.p.headers[secondFP].minutiae
		realMatches = []
		for match in matches:
			vector = matrix[match[0]] 
			vector2 = matrix2[match[1]]
			isRealMatch = False
			#print(vector[3])
			minutia0Vec = minutiae[int(vector[2])]
			minutia1Vec = minutiae[int(vector[3])]
			minutia0Vec2 = minutiae2[int(vector2[2])]
			minutia1Vec2 = minutiae2[int(vector2[3])]
			if self.compareMinutia(minutia0Vec, minutia0Vec2) and self.compareMinutia(minutia1Vec, minutia1Vec2):
				isRealMatch = True
			elif self.compareMinutia(minutia0Vec, minutia1Vec2) and self.compareMinutia(minutia1Vec, minutia0Vec2):
				isRealMatch = True
			if isRealMatch:
				realMatches.append(match)
		return realMatches


	def compareMinutia(self, minutia, minutia2):
		result = False
		x = int(minutia.xCoord)
		y = int(minutia.yCoord)
		typ = int(minutia.minType)
		x2 = int(minutia2.xCoord)
		y2 = int(minutia2.yCoord)
		typ2 = int(minutia2.minType)
		if abs(x - x2) < self.coordTreshold and abs(y - y2) < self.coordTreshold:
			if typ == typ2:
				result = True
		return result



	def comparision(self, matrix, matrix2, firstFP, secondFP):
		mostMatches = 0
		bestRotation = 0
		bestMatches = []
		for rot in drange(0,self.rotationAngle,self.rotationSteps):
			matches = []
			counter = 0
			for vector in matrix:
				matches.extend(self.findCounterpart(vector, matrix2, rot, counter))
				counter += 1
			realMatches = self.evaluateMatches(matches,matrix,matrix2,firstFP,secondFP)
			if len(realMatches) > mostMatches:
				mostMatches = len(realMatches)
				bestRotation = rot
				print("count matches")
				print(len(matches))
				bestMatches = realMatches
		print("rotation with most matches")
		print(bestRotation)
		return bestMatches
	
	def findCounterpart(self, vector, matrix, rot, counter):
		vector = self.applyRotation(vector, rot)
		return self.checkForTranslatedEqual(vector, matrix, counter)

	def checkForTranslatedEqual(self, vector, matrix, counter):
		matches = []
		counter2 = 0
		for vector2 in matrix:
			dx = 0
			dy = 1
			if vector2[0] == 0:
				if vector[0] == 0:
					dx = 0
				else:
					dx = 1000
			else:
				dx = round(vector[0]/vector2[0], 2)
			if vector2[1] == 0:
				if vector[1] == 0:
					dy = 0
				else:
					dy = 10000
			else:			
				dy = round(vector[1]/vector2[1], 2)
			if dx == dy:
				matches.append([counter, counter2])
			counter2 += 1
		return matches

	def applyRotation(self, vec, rot):
		rot = math.radians(rot)
		cos = math.cos(rot)
		sin = math.sin(rot)
		rotationMatrix = np.matrix([[cos, -sin],[sin, cos]])
		vectorMatrix = np.matrix([vec[0], vec[1]])
		vectorMatrix = vectorMatrix.getT()
		vector = rotationMatrix.dot(vectorMatrix)
		vec[0] = vector[0]
		vec[1] = vector[1]
		return vec

	def dispatchComparision(self, toMatch):
		allMatches = []
		successfulMatches = []
		failMatechs = []
		for tryMatch in toMatch:
			firstFP = tryMatch[0]
			secondFP = tryMatch[1]
			result = self.compare(firstFP, secondFP)
			allMatches.append([firstFP,secondFP,result])
			if result:
				successfulMatches.append([firstFP,secondFP])
			else:
				failMatechs.append([firstFP,secondFP])
		returnMatches = [allMatches, successfulMatches, failMatechs]
		return returnMatches


	def buildVectorMatrix(self,fpNumber):
		minutiae = self.p.headers[fpNumber].minutiae
		countMins = len(minutiae)
		vectorCount = 0
		vectorCount = int((countMins*(countMins - 1)))
		matrix = np.zeros((vectorCount,4))
		countk = 0
		countj = 0
		countTot = 0
		for minutia in minutiae:
			for minutia2 in minutiae:
				if(not minutia2.equals(minutia)):
					for i in range(4):
						matrix[countTot] = [int(minutia2.xCoord) - int(minutia.xCoord), int(minutia2.yCoord) - int(minutia.yCoord), countk, countj]
					countTot += 1
				countj += 1
			countk += 1
			countj = 0
		matrix = self.removeDuplicateVectors(matrix, countTot)
		return matrix

	def removeDuplicateVectors(self, matrix, length):	
		result = np.zeros(((length/2),4))
		counter = []
		index = 0
		for vector in matrix:
			first = vector[2]
			second = vector[3] 
			valPair = [first, second]
			valPair2 = [second, first]
			if valPair not in counter and valPair2 not in counter:
				counter.append(valPair)
				result[index] = vector
				index += 1
		return result

	def removeDupicateEntries(self, matrix, length):
		counter = []
		index = 0
		for vector in matrix:
			first = vector[0]
			second = vector[1] 
			valPair = [first, second]
			valPair2 = [second, first]
			if valPair not in counter and valPair2 not in counter:
				counter.append(valPair)
				index += 1
		return counter






class Parser:
	

	def __init__(self):
		self.f = open('C:/Users/Marc/SkyDrive/BFH2014/Biometrie/Kursaufgabe/fpAnalyser/test.txt','r')
		self.blockSize = 5
		self.blockSizeCounter = 0
		self.headers = []
		self.currHeader = None

	def parseFile(self):
		self.blockSizeCounter = 0
		dispatcher = 0
		currValues = []
		isFirst = True
		for line in self.f:
			if self.blockSizeCounter == 0:
				if isFirst:
					isFirst = False
				else:
					self.dispatch(dispatcher,currValues)
				dispatcher = self.matchRegex(line)
				self.blockSizeCounter = self.blockSize
				currValues = []
			else:
				val = re.search('-?[0-9]+',line)
				currValues.append(val.group(0))
				self.blockSizeCounter = self.blockSizeCounter - 1



			
	def matchRegex(self, line):
		if 'RecordHeader' in line:
			return 0
		elif 'FingerViewHeader' in line:
			return 1
		elif 'MinutiaIndex' in line:
			return 2

	def dispatch(self,dis,vals):
		if dis == 0:
			self.currHeader = RecordHeader(vals[0],vals[1],vals[2],vals[3],vals[4])
			self.headers.append(self.currHeader)
		elif dis == 1:
			self.currHeader.addFingerViewHeader(vals[0],vals[1],vals[2],vals[3],vals[4])
		elif dis == 2:
			self.currHeader.addMinutiae(vals[0],vals[1],vals[2],vals[3],vals[4])




class RecordHeader:
	def __init__(self, imgWidth, imgHeight, xResol, yResol, nViews):
		self.imgWidth = imgWidth
		self.imgHeight = imgHeight
		self.xResol = xResol
		self.yResol = yResol
		self.nViews = nViews
		self.fingerViewHeader = None
		self.minutiae = []

	def addFingerViewHeader(self, fingPos, nView, imprType, fingQuality, nMinutiae):
		self.fingerViewHeader = FingerViewHeader(fingPos, nView, imprType, fingQuality, nMinutiae)

	def addMinutiae(self, minType, xCoord, yCoord, minAngle, minQuality):
		self.minutiae.append(Minutiae(minType, xCoord, yCoord, minAngle, minQuality))





class FingerViewHeader:
	def __init__(self, fingPos, nView, imprType, fingQuality, nMinutiae):
		self.fingPos = fingPos
		self.nView = nView
		self.imprType = imprType
		self.fingQuality = fingQuality
		self.nMinutiae = nMinutiae


class Minutiae:
	def __init__(self, minType, xCoord, yCoord, minAngle, minQuality):
		self.minType = minType
		self.xCoord = xCoord
		self.yCoord = yCoord
		self.minAngle = minAngle
		self.minQuality = minQuality
	def equals(self,min):
		result = False
		if self.xCoord == min.xCoord and self.yCoord == min.yCoord:
			result = True
		return result




#Hilfsfunktion für iteration über Dezimalwerte
def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step