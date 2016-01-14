from imp import reload
import numpy as np
import re
import math

def act():
	p = Parser()
	p.parseFile()
	return p

def act2(firstFP):
	np.set_printoptions(threshold=1000000)
	a = FPAnalyzer()
	a.compare(firstFP,1)
	#return a.applyRotation([1,1],90)

class FPAnalyzer:

	def __init__(self):
		self.p = Parser()
		self.p.parseFile()
		self.rotationAngle = 45
		self.rotationSteps = 1
		self.coordTreshold = 3
		self.minuMatchTreshold = 5

	def setValues(self, rotationAngle, rotationSteps, coordTreshold):
		self.rotationAngle = rotationAngle
		self.rotationSteps = rotationSteps
		self.coordTreshold = coordTreshold


	def compare(self,firstFP, secondFP):
		matrix = self.buildVectorMatrix(firstFP)
		matrix2 = self.buildVectorMatrix(secondFP)
		self.comparision(matrix,matrix2)
		#print(matrix)
		

	def comparision(self, matrix, matrix2):
		mostMatches = 0
		bestRotation = 0 
		for rot in drange(0,self.rotationAngle,self.rotationSteps):
			matches = []
			counter = 0
			for vector in matrix:
				matches.extend(self.findCounterpart(vector, matrix2, rot, counter))
				counter += 1
			if len(matches) > mostMatches:
				mostMatches = len(matches)
				bestRotation = rot
	
	def findCounterpart(self, vector, matrix, rot, counter):
		vector = self.applyRotation(vector, rot)
		return self.checkForTranslatedEqual(vector, matrix, counter)

	def checkForTranslatedEqual(self, vector, matrix, counter):
		matches = []
		counter2 = 0
		for vector2 in matrix:
			dx = round(vector[0]/vector2[0], 2)
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
		#vector = vectorMatrix.dot(rotationMatrix)
		vector = rotationMatrix.dot(vectorMatrix)
		vec[0] = vector[0]
		vec[1] = vector[1]
		return vec



#	def evaluateRotation(self, matrix, matrix2):
#		for vector in matrix:
#			self.searchRotation(vector, matrix)
#
	#def evaluateTranslation(self, matrix, matrix2):
		
			
	


#	def searchRotation(self vector):


	#def searchTranslatedCounterpart


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