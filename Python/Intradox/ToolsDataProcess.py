import copy
import math
import numpy             as np
import ToolsImageProcess as cam
import ToolsCAD as cad

ThresholdPointError = 0.05

def findPointCloseTo(dataPoints, CP, dir):
	pRef = cad.Point()
	distMin = 1e10 # some large number
	# find the point closest to the center
	counter =  0
	index   = -1
	deltaX  =  0
	deltaY  =  0
	
	#print('Get point')
	for pt in dataPoints:
		p   = cad.Point()
		p.x = pt[0]
		p.y = pt[1]
		distance = cad.distance(p, CP)
		
		if not((p.x == CP.x) and (p.y == CP.y)) and (distance <= distMin):
			if (dir == -180) and (p.x <= CP.x) and (abs(p.y - CP.y) < abs(p.x - CP.x)/4) :
				distMin = distance
				pRef = copy.copy(p)
				index = counter
				deltaX = p.x - CP.x
				deltaY = p.y - CP.y
			if (dir == 180) and (p.x >= CP.x) and (abs(p.y - CP.y) < abs(p.x - CP.x)/4) :
				distMin = distance
				pRef = copy.copy(p)
				index = counter
				deltaX = p.x - CP.x
				deltaY = p.y - CP.y
			if (dir == -90) and (p.y >= CP.y) and (abs(p.x - CP.x) < abs(p.y - CP.y)/4) :
				distMin = distance
				pRef = copy.copy(p)
				index = counter
				deltaX = p.x - CP.x
				deltaY = p.y - CP.y
			if (dir ==  90) and (p.y <= CP.y) and (abs(p.x - CP.x) < abs(p.y - CP.y)/4) :
				distMin = distance
				pRef = copy.copy(p)
				index = counter
				deltaX = p.x - CP.x
				deltaY = p.y - CP.y
			if (dir == 0) and (distance <= distMin):
				distMin = distance
				pRef = copy.copy(p)
				index = counter
				deltaX = p.x - CP.x
				deltaY = p.y - CP.y
		counter += 1
	return  pRef, index, distMin, deltaX, deltaY

def refineCorners(dataPoints,PLT,PLB,PRB,PRT):
	dataLeft   = []
	dataRight  = []
	dataTop    = []
	dataBottom = []
	
	edge       = []
	
	p1 = cad.Point()
	
	for pt in dataPoints:
		p1.x = pt[0]
		p1.y = pt[1]
	
		# left
		distance = cad.pointLineDistance(p1,PLT,PLB)
		dist2    = cad.distance(PLT, PLB)
		if (distance <= math.sqrt((cam.marker.width//2) + (cam.marker.height//2))) and (cad.distance(p1,PLT) <= dist2) and (cad.distance(p1,PLB) <= dist2):
			#if DebugShow:
			#	cv2.circle(debugFrame,pt, 8, (255,255,255), 2)
			dataLeft.append(pt)
			edge.append(pt)
		
		# bottom
		distance = cad.pointLineDistance(p1,PLB,PRB)
		dist2    = cad.distance(PLB,PRB)
		if (distance <= math.sqrt((cam.marker.width//2) + (cam.marker.height//2))) and (cad.distance(p1,PLB) <= dist2) and (cad.distance(p1,PRB) <= dist2):
			#if DebugShow:
			#	cv2.circle(debugFrame,pt, 8, (255,0,255), 2)
			dataBottom.append(pt)
			edge.append(pt)
		
		# right
		distance = cad.pointLineDistance(p1,PRB,PRT)
		dist2    = cad.distance(PRB,PRT)
		if (distance <= math.sqrt((cam.marker.width//2) + (cam.marker.height//2))) and (cad.distance(p1,PRB) <= dist2) and (cad.distance(p1,PRT) <= dist2):
			#if DebugShow:
			#	cv2.circle(debugFrame,pt, 8, (255,255,255), 2)
			dataRight.append(pt)
			edge.append(pt)
		
		# top
		distance = cad.pointLineDistance(p1,PRT,PLT)
		dist2    = cad.distance(PRT,PLT)
		if (distance <= math.sqrt((cam.marker.width//2) + (cam.marker.height//2))) and (cad.distance(p1,PRT) <= dist2) and (cad.distance(p1,PLT) <= dist2):
			#if DebugShow:
			#	cv2.circle(debugFrame,pt, 8, (255,255,255), 2)
			dataTop.append(pt)
			edge.append(pt)
	
	PAT = cad.Point()
	PAL = cad.Point()
	PBB = cad.Point()
	PBL = cad.Point()
	PCB = cad.Point()
	PCR = cad.Point()
	PDR = cad.Point()
	PDT = cad.Point()
	
	if min(len(dataTop),len(dataLeft),len(dataBottom),len(dataRight)) > 2:
		PAT, PDT = cad.LinearReg2(dataTop)
		PAL, PBL = cad.LinearReg2(dataLeft)
		PBB, PCB = cad.LinearReg2(dataBottom)
		PCR, PDR = cad.LinearReg2(dataRight)
	
	PA = cad.lineIntersect(PDT,PAT,PAL,PBL)
	PB = cad.lineIntersect(PAL,PBL,PBB,PCB)
	PC = cad.lineIntersect(PBB,PCB,PCR,PDR)
	PD = cad.lineIntersect(PCR,PDR,PDT,PAT)
	
	coll = 0
	row  = 0
	if (len(dataTop) == len(dataBottom)) and (len(dataLeft) == len(dataRight)):
		coll = len(dataTop)
		row  = len(dataLeft)
		
	return PA,PB,PC,PD, coll, row, edge

def findCornersRaw(dataPoints,CP):
	PA = cad.Point()
	PB = cad.Point()
	PC = cad.Point()
	PD = cad.Point()
	
	# convert the data points list to a 2D array that is easier to handle
	pointMatrix = np.array([-1])
	
	#get some distance estimates in Pix values
	# find the center point as a starting point
	p, index1, dist, dX,dY = findPointCloseTo(dataPoints, CP,    0)
	# find the points around the center point and calculate the average distances in x and y
	q, index2, deltaY1,dX1,dY1 = findPointCloseTo(dataPoints,  p,   90)
	q, index2, deltaY2,dX2,dY2 = findPointCloseTo(dataPoints,  p,  -90)
	deltaY = (deltaY1 + deltaY2) / 2 
	
	q, index2, deltaX1, dX3,dY3 = findPointCloseTo(dataPoints,  p,  180)
	q, index2, deltaX2, dX4,dY4 = findPointCloseTo(dataPoints,  p, -180)
	deltaX = (deltaX1 + deltaX2) / 2
	
	#rint('90 [' , dX1,dY1,']  -90 [',dX2,dY2,']  180 [',dX3,dY3,'] -180 [',dX4,dY4,'] => [',deltaX,deltaY,']')
	
	xRef = p.x
	yRef = p.y
	dataRange = []
	
	if (deltaX > 0) and (deltaX <= cam.cam.width) and (deltaY > 0) and (deltaY <= cam.cam.height):
		#loop through the list to find the extremes in Pix that will define the required array size
		xMin = 1e10; 
		xMax = 0;
		yMin = 1e10;
		yMax = 0;
		for pt in dataPoints:
			if pt[0] < xMin:
				xMin = pt[0]
			if pt[0] > xMax:
				xMax = pt[0]
			if pt[1] < yMin:
				yMin = pt[1]
			if pt[1] > yMax:
				yMax = pt[1]
		# estimate the required array size
		xSize = round((xMax - xMin) / deltaX) + 4
		ySize = round((yMax - yMin) / deltaY) + 8
		
		#print(xSize,ySize)
		pointMatrix = np.resize(pointMatrix,(xSize,ySize))
		
		#determine the location of center point in the array
		xPosC = round ((xRef - xMin) / deltaX)
		yPosC = round ((yRef - yMin) / deltaY)
		
		if (xPosC >= 0) and (yPosC >= 0) and (xPosC < xSize) and (yPosC < ySize):
			pointMatrix[xPosC][yPosC] = 2
		
		#loop through the list to again to mark the point locations in a xy matrix
		count = 0
		for pt in dataPoints:
		
			P1 = cad.Point()
			P2 = cad.Point()
			P3 = cad.Point()
			P1.x = pt[0]
			P1.y = pt[1]
			P3.x = xRef
			P3.y = yRef
			
			#P1.x = 20
			#P1.y = 10
			#P3.x = 10
			#P3.y = 10
			# rotate the point on Rz to prevent phase shifts with belts that have large xy ratios
			P2 = cad.rotatePointOnPoint(P1,P3,-cad.anglePointPoint(p,q))
			#calculate the relevant point in the matrix and mark it
			xPos = round ((P2.x - xRef) / deltaX)
			yPos = round ((P2.y - yRef) / deltaY)
			
			pointMatrix[xPos + xPosC][yPos + yPosC] = count
			count += 1
		#print(pointMatrix)
		#print()
		
		# clean up the points that have a too large position error in relation to the points around them (thus most likely mis reads)
		checkMatrix = np.array([-1])
		checkMatrix = np.resize(checkMatrix,(xSize,ySize))
		
		errorRange = ThresholdPointError
		
		# check in the center for points that have all surrounding points in expected range
		for w in range(1,xSize - 1):
			for h in range(1,ySize - 1):
				if pointMatrix[w][h] >= 0:
					if (abs(abs(dataPoints[pointMatrix[w-1][h  ]][0] - dataPoints[pointMatrix[w]    [h]][0]) - \
							abs(dataPoints[pointMatrix[w+1][h  ]][0] - dataPoints[pointMatrix[w]    [h]][0])) < \
							deltaX * errorRange) and \
					   (abs(abs(dataPoints[pointMatrix[w]  [h-1]][1] - dataPoints[pointMatrix[w][h]][1]) - \
							abs(dataPoints[pointMatrix[w]  [h+1]][1] - dataPoints[pointMatrix[w][h]][1])) < \
							deltaY * errorRange):
					   checkMatrix[w,h] = 15
		
		# check if the point is properly connected on the right side
		for w in range(0,xSize - 1):
			for h in range(0,ySize):
				if (pointMatrix[w][h] >= 0) and (checkMatrix[w,h] < 0):
					if (abs(dataPoints[pointMatrix[w+1][h]][0] - dataPoints[pointMatrix[w][h]][0]) < \
					    deltaX * (1 + errorRange)) and \
					   (abs(dataPoints[pointMatrix[w+1][h]][0] - dataPoints[pointMatrix[w][h]][0]) > \
					    deltaX * (1 - errorRange)) and \
					   (abs(dataPoints[pointMatrix[w+1][h]][1] - dataPoints[pointMatrix[w][h]][1]) < \
					    deltaY * errorRange):
					   checkMatrix[w,h] = 2
		
		# check if the point is properly connected on the left side
		for w in range(1,xSize):
			for h in range(0,ySize):
				if (pointMatrix[w][h] >= 0) and (checkMatrix[w,h] < 0):
					if (abs(dataPoints[pointMatrix[w-1][h]][0] - dataPoints[pointMatrix[w][h]][0]) < \
					    deltaX * (1 + errorRange)) and \
					   (abs(dataPoints[pointMatrix[w-1][h]][0] - dataPoints[pointMatrix[w][h]][0]) > \
					    deltaX * (1 - errorRange)) and \
					   (abs(dataPoints[pointMatrix[w-1][h]][1] - dataPoints[pointMatrix[w][h]][1]) < \
					    deltaY * errorRange):
					   checkMatrix[w,h] = 8
		
		# check if the point is properly connected on the top side
		for w in range(0,xSize):
			for h in range(0,ySize-1):
				if (pointMatrix[w][h] >= 0) and (checkMatrix[w,h] < 0):
					if (abs(dataPoints[pointMatrix[w][h+1]][1] - dataPoints[pointMatrix[w][h]][1]) < \
					    deltaY * (1 + errorRange)) and \
					   (abs(dataPoints[pointMatrix[w][h+1]][1] - dataPoints[pointMatrix[w][h]][1]) > \
					    deltaY * (1 - errorRange)) and \
					   (abs(dataPoints[pointMatrix[w][h+1]][0] - dataPoints[pointMatrix[w][h]][0]) < \
					    deltaX * errorRange):
					   checkMatrix[w,h] = 1
		
		# check if the point is properly connected on the bottom side
		for w in range(0,xSize):
			for h in range(1,ySize):
				if (pointMatrix[w][h] >= 0) and (checkMatrix[w,h] < 0):
					if (abs(dataPoints[pointMatrix[w][h-1]][1] - dataPoints[pointMatrix[w][h]][1]) < \
					    deltaY * (1 + errorRange)) and \
					   (abs(dataPoints[pointMatrix[w][h-1]][1] - dataPoints[pointMatrix[w][h]][1]) > \
					    deltaY * (1 - errorRange)) and \
					   (abs(dataPoints[pointMatrix[w][h-1]][0] - dataPoints[pointMatrix[w][h]][0]) < \
					    deltaX * errorRange):
					   checkMatrix[w,h] = 4
		
		# fit the largest possible rectangle in the structured matrix using brute force
		surfaceMax = 0
		wMax = 0
		hMax = 0
		xPos = 0
		yPos = 0
		
		# set the box size searching from big to small, this to speed up the search
		for w in range(xSize, 0, -1):
			for h in range(ySize, 0, -1):
				# set the (possible) search range
				if w * h >= surfaceMax: # only continue to search in detail if there is a possibility to find a better result
					#print('--',w,h,surfaceMax)
					for ww in range(xSize - w):
						for hh in range(ySize - h):
							#print(' -',ww,hh,surfaceMax)
							# search the range
							check = True
							for www in range(w):
								for hhh in range(h):
									#print('  ',www,hhh,surfaceMax)
									if checkMatrix[ww + www][hh + hhh] < 0:
										check = False
							if check:
								if w * h > surfaceMax:
									wMax = w
									hMax = h
									xPos = ww
									yPos = hh
									surfaceMax = wMax * hMax
									PA.x = dataPoints[pointMatrix[ww       ][hh       ]][0]
									PA.y = dataPoints[pointMatrix[ww       ][hh       ]][1]
									PB.x = dataPoints[pointMatrix[ww       ][hh + h -1]][0]
									PB.y = dataPoints[pointMatrix[ww       ][hh + h -1]][1]
									PC.x = dataPoints[pointMatrix[ww + w -1][hh + h -1]][0]
									PC.y = dataPoints[pointMatrix[ww + w -1][hh + h -1]][1]
									PD.x = dataPoints[pointMatrix[ww + w -1][hh       ]][0]
									PD.y = dataPoints[pointMatrix[ww + w -1][hh       ]][1]
		# create the list of good points
		for w in range(xPos, xPos + wMax):
			for h in range(yPos, yPos + hMax):
				dataRange.append(dataPoints[pointMatrix[w][h]])
	return PA, PB, PC, PD, dataRange

def findCornersEdgeTrace(dataPoints,CP):
	# find the 4 corners of the data field
	
	# find the corners of the boundary box
	p = cad.Point()
	q = cad.Point()
	
	# find the center point as a starting point
	p, index1, dist, dX, dY = findPointCloseTo(dataPoints, CP,    0)
	# search for the top
	q, index2, dist, dX, dY = findPointCloseTo(dataPoints,  p,   90)
	dist2 = dist
	counter = 0
	if index1 != -1:
		counter += 1
		#imageCircle(p,(0,255,0))
		if index2 != -1:
			counter += 1
			#imageLine(q,p,(0,255,0))
	p = copy.copy(q)
	while index1 != -1:
		q, index2, dist, dX,dY = findPointCloseTo(dataPoints, p, 90)
		if (index2 == -1) or (dist > dist2 * 1.5):
			break
		else:
			#imageLine(q,p,(0,255,255))
			p = copy.copy(q)
			dists = dist
			counter += 1
	
	# search for the left side
	q, index2, dist, dX,dY = findPointCloseTo(dataPoints,  p,   -180)
	dist2 = dist
	counter = 0
	if index1 != -1:
		counter += 1
		#imageCircle(p,(0,255,0))
		if index2 != -1:
			counter += 1
			#imageLine(q,p,(0,255,0))
	p = copy.copy(q)
	while index1 != -1:
		q, index2, dist, dX,dY = findPointCloseTo(dataPoints, p, -180)
		if (index2 == -1) or (dist > dist2 * 1.5):
			break
		else:
			#imageLine(q,p,(0,255,255))
			p = copy.copy(q)
			dist2 = dist
			counter += 1
	
	# search for the bottom
	pointsLeft = []
	pointsLeft.append(p)
	q, index2, dist, dX,dY = findPointCloseTo(dataPoints,  p,   -90)
	dist2 = dist
	counter = 0
	if index1 != -1:
		counter += 1
		#imageCircle(p,(0,255,0))
		if index2 != -1:
			counter += 1
			#imageLine(q,p,(0,255,0))
			pointsLeft.append(q)
	p = copy.copy(q)
	while index1 != -1:
		q, index2, dist, dX, dY = findPointCloseTo(dataPoints, p, -90)
		if (index2 == -1) or (dist > dist2 * 1.5):
			break
		else:
			#imageLine(q,p,(0,255,255))
			pointsLeft.append(q)
			p = copy.copy(q)
			dist2 = dist
			counter += 1
	
	# search for the right side
	q, index2, dist, dX, dY = findPointCloseTo(dataPoints,  p,   180)
	dist2 = dist
	counter = 0
	if index1 != -1:
		counter += 1
		#imageCircle(p,(0,255,0))
		if index2 != -1:
			counter += 1
			#imageLine(q,p,(0,255,0))
	p = copy.copy(q)
	while index1 != -1:
		q, index2, dist, dX, dY = findPointCloseTo(dataPoints, p, 180)
		if (index2 == -1) or (dist > dist2 * 1.5):
			break
		else:
			#imageLine(q,p,(0,255,255))
			p = copy.copy(q)
			dist2 = dist
			counter += 1
	
	# search for the top
	pointsRight = []
	pointsRight.append(p)
	q, index2, dist, dX,dY = findPointCloseTo(dataPoints,  p,   90)
	dist2 = dist
	counter = 0
	if index1 != -1:
		counter += 1
		#imageCircle(p,(0,255,0))
		if index2 != -1:
			counter += 1
			#imageLine(q,p,(0,255,0))
			pointsRight.append(q)
	p = copy.copy(q)
	while index1 != -1:
		q, index2, dist, dX,dY = findPointCloseTo(dataPoints, p, 90)
		if (index2 == -1) or (dist > dist2 * 1.5):
			break
		else:
			#imageLine(q,p,(0,255,255))
			pointsRight.append(q)
			p = copy.copy(q)
			dist2 = dist
			counter += 1
	
	PA = cad.Point()
	PB = cad.Point()
	PC = cad.Point()
	PD = cad.Point()
	
	PA = pointsLeft[max(0,len(pointsLeft) - len(pointsRight))]
	PB = pointsLeft[len(pointsLeft) - 1]
	PC = pointsRight[0]
	PD = pointsRight[min(len(pointsRight) - 1, len(pointsLeft) - 1)]
	
	return PA, PB, PC, PD

def findCorners(dataPoints,CP):
	PA = cad.Point()
	PB = cad.Point()
	PC = cad.Point()
	PD = cad.Point()
	dataRange = []
	#print(len(dataPoints))
	if len(dataPoints) < 128:
		PA, PB, PC, PD, dataRange = findCornersRaw(dataPoints,CP)
		#print('RAW')
	else:
		PA, PB, PC, PD = findCornersEdgeTrace(dataPoints,CP)
		#print('Trace')
	return PA, PB, PC, PD, dataRange 


#
#
#
#
#
