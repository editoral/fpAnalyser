from imp import reload
import numpy as np
import re


def act():
	p = Parser()
	p.parseFile()
	return p

def act2(firstFP):
	a = FPAnalyzer()
	a.compare(firstFP,1)	

class FPAnalyzer:

	def __init__(self):
		self.p = Parser()
		self.p.parseFile()


	def compare(self,firstFP, secondFP):
		matrix = self.buildVectorMatrix(firstFP)
		matrix2 = self.buildVectorMatrix(secondFP)
		
	def evaluateTranslation(self, matrix, matrix2)


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
		return matrix



		






class Parser:
	

	def __init__(self):
		self.f = open('C:/Users/Marc/SkyDrive/BFH2014/Biometrie/Kursaufgabe/Projekt/test.txt','r')
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