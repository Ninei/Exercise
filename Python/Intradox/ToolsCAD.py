import math

from scipy.integrate._ivp.radau import P


class Point(object):
	def __init__(self):
		self.x = 0.0
		self.y = 0.0

class Point3D(object):
	def __init__(self):
		self.x = 0.0
		self.y = 0.0
		self.z = 0.0

class Line(object):
	def __init__(self):
		self.P1 = Point()
		self.P2 = Point()

class Plane3D(object):
	def __init__(self):
		self.P1 = Point3D()
		self.P2 = Point3D()
		self.P3 = Point3D()

def debugPrintPoint(P):
	print('[',P.x,',',P.y,']')

def debugPrintPoint2(P1,P2):
	print('[',P1.x,',',P1.y,'],[',P2.x,',',P2.y,']')

def debugPrintPoint3D(P):
	print('[',P.x,',',P.y,',',P.z,']')

def debugPrintLine(L):
	debugPrintPoint2(L.P1,L.P2)

def debugPrintPlane(PL):
	print('[',PL.P1.x,',',PL.P1.y,PL.P1.z,'],[',PL.P2.x,',',PL.P2.y,PL.P2.z,'],[',PL.P3.x,',',PL.P3.y,PL.P3.z,']')

def build_point_matrix(rows, cols):
	matrix = [[Point() for row in range(rows)] for col in range(cols)]
	return matrix

def correlate(x, y):
	SX   = 0.0
	SY   = 0.0
	SXY  = 0.0
	SX2  = 0.0
	SY2  = 0.0
	d    = 0.0
	
	for n in range(len(x)):
		SX  += x[n]
		SY  += y[n]
		SXY += x[n] * y[n]
		SX2 += x[n]**2
		SY2 += y[n]**2
	
	d = math.sqrt(((len(x) * SX2) - (SX**2)) * ((len(x) * SY2)- (SY**2)))
	
	if d == 0: 
		return 0.0
	else:
		return ((len(x) * SXY) - (SX * SY)) / d

def lineIntersect(P1,P2,P3,P4): #P1 & P2 as Point on line 1, P3 & P4 Point on line 2
	x1 = P1.x;
	x2 = P2.x;
	x3 = P3.x;
	x4 = P4.x;
	
	y1 = P1.y;
	y2 = P2.y;
	y3 = P3.y;
	y4 = P4.y;
	
	d = ((x1-x2)*(y3-y4))-((y1-y2)*(x3-x4))
	
	r = Point()
	if d != 0:
		u = (((x1 - x3)*(y1 - y2)) - (y1-y3)*(x1-x2))/(((x1-x2)*(y3-y4))-((y1-y2)*(x3-x4)))
		r.x = x3 + (u*(x4-x3))
		r.y = y3 + (u*(y4-y3))
		return r
	else:
		r.x = 0
		r.y = 0
		return r

def linePlaneIntersect(P1,P2,PL): #P1 & P2 as Points on the line, PL as the intersect plane
	Px = P1.x
	Py = P1.y
	Pz = P1.z
	
	Qx = P2.x
	Qy = P2.y
	Qz = P2.z
	
	ax = PL.P1.x
	ay = PL.P1.y
	az = PL.P1.z
	
	bx = PL.P2.x
	by = PL.P2.y
	bz = PL.P2.z

	cx = PL.P3.x
	cy = PL.P3.y
	cz = PL.P3.z 
	
	
	# https://keisan.casio.com/exec/system/1223596129
	a = ((by-ay)*(cz-az)) - ((cy-ay)*(bz-az))
	b = ((bz-az)*(cx-ax)) - ((cz-az)*(bx-ax))
	c = ((bx-ax)*(cy-ay)) - ((cx-ax)*(by-ay))
	d = -((a * ax) + (b * ay) + (c * az))
	
	
	# https://stackoverflow.com/questions/5666222/3d-line-plane-intersection
	tDenom = (a * (Qx-Px)) + (b * (Qy-Py)) + (c * (Qz-Pz))
	if tDenom == 0:
		r = Point3D()
		r.x = 0
		r.y = 0
		r.z = 0
		return r
	else:
		r = Point3D()
		t = - ((a * Px) + (b * Py) + (c * Pz) + d) / tDenom
		r.x = (Px + (t * (Qx - Px)))
		r.y = (Py + (t * (Qy - Py)))
		r.z = (Pz + (t * (Qz - Pz)))
		return r

def movePoint(P1,V1): #P1 point to move, V1 move vector
	P = Point()
	P.x = P1.x + V1.x
	P.y = P1.y + V1.y
	return P

def moveLine(LP1,LP2,VP1,VP2): #LP1, LP2 line, VP1 start of move vector, VP2 end of move vector
	P1 = Point()
	P2 = Point()
	
	V = Point()
	V.x = VP2.x - VP1.x
	V.y = VP2.y - VP1.y
	
	P1 = movePoint(LP1, V)
	P2 = movePoint(LP2, V)
	return P1, P2

def distance(P1,P2): #P1 & P2 as Point
	r = math.sqrt(((P1.x - P2.x)**2) + ((P1.y - P2.y)**2))
	return r

def anglePointPoint(P1,P2): #P1 & P2 as point vectors from origin,
	if P1.x == P2.x:
		if P1.y >= P2.y:
			a = math.pi / 2
		else:
			a = -math.pi / 2
	else:
		a = math.atan((P2.y - P1.y) / (P2.x - P1.x))
		if (P1.x < P2.x) and (P1.y > P2.y):
			a += math.pi
		if (P1.x < P2.x) and (P1.y < P2.y):
			a -= math.pi
	if P1.y == P2.y:
		if P1.x >= P2.x:
			a = 0
		else:
			a = math.pi
	return a

def angle(P): #P1 & P2 as point vectors from origin,
	if P.y == 0.0:
		return math.pi
	else:
		a = math.atan(P.x / P.y)
		return a

def rotatePointOnPoint(P1,P2,alpha):
	P = Point()
	P.x = P2.x + (math.cos(anglePointPoint(P1,P2) + alpha) * distance(P1,P2))
	P.y = P2.y + (math.sin(anglePointPoint(P1,P2) + alpha) * distance(P1,P2))
	#print(math.degrees(anglePointPoint(P1,P2)),end=' ' )
	return P

def pointLineDistance(P1,P2,P3): #P1 as Point, P2 & P3 as Point on line
	x0 = P1.x
	y0 = P1.y
	x1 = P2.x
	y1 = P2.y
	x2 = P3.x
	y2 = P3.y
	d = ((x2 - x1)**2) + ((y2 - y1)**2)
	if d != 0:
		r  = abs(((x2 - x1)*(y1 - y0)) - ((x1 - x0)*(y2 - y1))) / math.sqrt(d)
	else:
		r = 1e10 # some very large number to mimic infinite 
	return r

def distancePointPoint(P1,P2):
	return math.sqrt(((P1.x - P2.x)**2) + ((P1.y - P2.y)**2))

def distancePointPoint3D(P1,P2): 
	return math.sqrt(((P1.x - P2.x)**2) + ((P1.y - P2.y)**2) + ((P1.z - P2.z)**2))

def LinearReg(Pt):
	SX   = 0.0
	SY   = 0.0
	SXY  = 0.0
	SX2  = 0.0
	SY2  = 0.0
	d    = 0.0
	
	P1 = Point()
	P2 = Point()
	for n in range(len(Pt)):
		SX  += Pt[n].x
		SY  += Pt[n].y
		SXY += Pt[n].x * Pt[n].y
		SX2 += Pt[n].x**2
		SY2 += Pt[n].y**2
	
	if abs(P[0].x - Pt[len(P) - 1].x) > abs(Pt[0].y - Pt[len(P) - 1].y):
		#dominant horizontal regression
		#b0 is: [(ΣY)(ΣX2) – (ΣX)(ΣXY)]  /  [n(ΣX2) – (ΣX)2]
		b0 = ((SY * SX2) - (SX * SXY)) / ((len(P) * SX2) - ((SX)**2))
		#b1 is: [n(ΣXY) – (ΣX)(ΣY)]  /  [n(ΣX2) – (ΣX)2]
		b1 =  (((len(P)*SXY)) - (SX * SY)) / ((len(P) * SX2) - ((SX)**2))
		
		P1.x = Pt[0].x
		P1.y = b0 + (b1 * Pt[0].x)
		P2.x =            Pt[len(P) - 1].x
		P2.y = b0 + (b1 * Pt[len(P) - 1].x)
		return P1,P2
	else:
		#dominant vertical regression
		b0 = ((SX * SY2) - (SY * SXY)) / ((len(Pt) * SY2) - ((SY)**2))
		b1 =  (((len(Pt)*SXY)) - (SY * SX)) / ((len(Pt) * SY2) - ((SY)**2))
		
		P1.x = b0 + (b1 * Pt[1].y)
		P1.y =            Pt[1].y
		P2.x = b0 + (b1 * Pt[len(P) - 1].y)
		P2.y =            Pt[len(P) - 1].y
		return P1,P2

def LinearReg2(P):
	SX   = 0.0
	SY   = 0.0
	SXY  = 0.0
	SX2  = 0.0
	SY2  = 0.0
	d    = 0.0
	
	P1 = Point()
	P2 = Point()

	for n in range(len(P)):
		SX  += P[n][0]
		SY  += P[n][1]
		SXY += P[n][0] * P[n][1]
		SX2 += P[n][0]**2
		SY2 += P[n][1]**2

	if abs(P[0][0] - P[len(P) - 1][0]) > abs(P[0][1] - P[len(P) - 1][1]):
		#dominant horizontal regression
		#b0 is: [(ΣY)(ΣX2) – (ΣX)(ΣXY)]  /  [n(ΣX2) – (ΣX)2]
		b0 = ((SY * SX2) - (SX * SXY)) / ((len(P) * SX2) - ((SX)**2))
		#b1 is: [n(ΣXY) – (ΣX)(ΣY)]  /  [n(ΣX2) – (ΣX)2]
		b1 =  (((len(P)*SXY)) - (SX * SY)) / ((len(P) * SX2) - ((SX)**2))
		
		P1.x = P[0][0]
		P1.y = b0 + (b1 * P[0][0])
		P2.x =            P[len(P) - 1][0]
		P2.y = b0 + (b1 * P[len(P) - 1][0])
		return P1,P2
	else:
		#dominant vertical regression
		b0 = ((SX * SY2) - (SY * SXY)) / ((len(P) * SY2) - ((SY)**2))
		b1 =  (((len(P)*SXY)) - (SY * SX)) / ((len(P) * SY2) - ((SY)**2))
		
		P1.x = b0 + (b1 * P[1][1])
		P1.y =            P[1][1]
		P2.x = b0 + (b1 * P[len(P) - 1][1])
		P2.y =            P[len(P) - 1][1]
		return P1,P2

def centerImage(PA,PB,PC,PD,CP): #P1,2,3,4 as the corners of the box in the image plane, PC as the new centerPoint of the image
	
	VPV  = Point()
	VPH  = Point()
	VPSV = Point()
	VPSH = Point()
	CPP  = Point()
	
	PA2  = Point()
	PB2  = Point()
	PC2  = Point()
	PD2  = Point()
	
	PAB2 = Point()
	PBC2 = Point()
	PAD2 = Point()
	PDC2 = Point()
	
	VPL  = Line()
	VDE  = Line()
	VDE2 = Line()
	PTemp = Point()
	
	# find the center of the current image
	CPP = lineIntersect(PA,PC,PB,PD)
	
	# find the vanish points
	VPV = lineIntersect(PA,PB,PD,PC)
	VPH = lineIntersect(PA,PD,PB,PC)
	
	# find the points vanish points of the image diagonals, must be on the line VPV - VPH
	VPSH = lineIntersect(PB,PD,VPV,VPH)
	VPSV = lineIntersect(PA,PC,VPV,VPH)
	
	# create the support line parallel to VPV - VPH to enable shifting the image without loosing perspective
	PTemp.x =  CP.x # This should be a 'random' point in space and not on the line VPL, using the image center for convenience
	PTemp.y =  CP.y
	
	VPL.P1.x = VPV.x
	VPL.P1.y = VPV.y
	VPL.P2.x = VPH.x
	VPL.P2.y = VPH.y
	VPL.P1, VPL.P2 = moveLine(VPL.P1,VPL.P2,VPL.P1,PTemp)
	
	# calculate the offset between the original and shifted image on the VPL support line
	VDE.P1 = lineIntersect(VPL.P1, VPL.P2, CPP, VPV)
	VDE.P2 = lineIntersect(VPL.P1, VPL.P2, CP,VPV)
	
	# calculate image move intersection point based upon the offset
	VDE2.P1, VDE2.P2   = moveLine(VDE.P1,VDE.P2,VDE.P1,lineIntersect(VPL.P1,VPL.P2,PD,VPV))
	
	# calculate the new image position
	PD2 = lineIntersect(VPV, VDE2.P2, VPSH, CP)
	PA2 = lineIntersect(VPH, PD2,     VPSV, CP)
	PB2 = lineIntersect(VPV, PA2,     VPSH, CP)
	PC2 = lineIntersect(VPV, PD2,     VPSV, CP)
	
	PAB2 = lineIntersect(PA2, PB2, VPH, CP)
	PBC2 = lineIntersect(PB2, PC2, VPV, CP)
	PAD2 = lineIntersect(PA2, PD2, VPV, CP)
	PDC2 = lineIntersect(PD2, PC2, VPH, CP)
	
	return PA2,PB2,PC2,PD2,PAB2,PBC2,PAD2,PDC2

def getElongation(PA,PB,PC,PD,PAB,PBC,PAD,PDC,CC,CP,COLL,ROW, ColWidth, RowHeight): #P1,2,3,4 as the corners of the box in the image plane, CC as the camera distance from the image in image coordinates
	
	IA = Point3D() # corner points of the object in the Image plane
	IB = Point3D()
	IC = Point3D()
	ID = Point3D()
	
	OA = Point3D() # corner points of the object in the Object plane
	OB = Point3D()
	OC = Point3D()
	OD = Point3D()
	
	IP1 = Point()
	IP2 = Point()
	IP3 = Point()
	
	CFP = Point() # Camera Focal point
	PCF = Point3D() # Camera Focal point
	
	XX  = Line() # X-axis
	YY  = Line() # Y-axis
	Rx  = 0.0
	RY  = 0.0
	
	PPRx = Point()
	PPRy = Point()
	
	AB = 0.0 # lengths of the box sides
	BC = 0.0
	CD = 0.0
	DA = 0.0
	
	OPL = Plane3D() # object plane 
	# set the plane center to the center of the camera
	OPL.P1.x = CP.x
	OPL.P1.y = CP.y
	OPL.P1.z = 0.0
	
	# Set the 2D camera reference points
	CFP.x = CC
	CFP.y = 0.0;
	
	PCF.x = CP.x # camera focal point in 3D
	PCF.y = CP.y
	PCF.z = CC
	
	#Convert from 3D to 2D,
	XX.P1.x = CP.x;
	XX.P1.y = CP.y;
	XX.P2.x = CP.x + 1;
	XX.P2.y = CP.y;
	
	YY.P1.x = CP.x;
	YY.P1.y = CP.y;
	YY.P2.x = CP.x;
	YY.P2.y = CP.y + 1;
	
	# calculate Rx
	# calculate the reference marker line crossings with the Y axiS
	IP1 = lineIntersect(PA,  PD,  YY.P1, YY.P2);
	IP2 = lineIntersect(PAB, PDC, YY.P1, YY.P2);
	IP3 = lineIntersect(PB,  PC,  YY.P1, YY.P2);
	
	# shift to lens center
	IP1.y -= IP2.y
	IP3.y -= IP2.y
	
	CP.y = IP2.y
	
	# calculate the (2D transformed) Y and X points of the Object plane
	if abs(CFP.x) != 0 and (abs(IP1.y) + abs(IP3.y)) != 0:
		PPRx.x = (abs(IP1.y) -  abs(IP3.y)          ) / ((abs(IP1.y) + abs(IP3.y)) / abs(CFP.x))
		PPRx.y = (abs(IP1.y) * (abs(CFP.x) - PPRx.x)) /   abs(CFP.x)
	else:
		PPRx.x = 0
		PPRx.y = 0
	
	# rotate the Object plane Rx by setting the Object plane P3 values
	OPL.P3.x =  0     + CP.x
	OPL.P3.y = PPRx.y + CP.y
	OPL.P3.z = PPRx.x 
	
	# Calculate Ry
	IP1 = lineIntersect(PA,  PB,  XX.P1, XX.P2)
	IP2 = lineIntersect(PAD, PBC, XX.P1, XX.P2)
	IP3 = lineIntersect(PD,  PC,  XX.P1, XX.P2)
	
	#shift to lens center
	IP1.x -= IP2.x
	IP3.x -= IP2.x
	
	CP.x = IP2.x
	
	# calculate the (2D transformed) Y and X points of the Object plane
	if abs(CFP.x) != 0 and (abs(IP1.x) + abs(IP3.x)) != 0:
		PPRy.x = (abs(IP1.x) -  abs(IP3.x)          ) / ((abs(IP1.x) + abs(IP3.x)) / abs(CFP.x))
		PPRy.y = (abs(IP1.x) * (abs(CFP.x) - PPRy.x)) /   abs(CFP.x)
	else:
		PPRy.x = 0
		PPRy.y = 0
	
	# rotate the Object plane in Ry by setting the Object plane P2 values
	OPL.P2.x = PPRy.y + CP.x
	OPL.P2.y = 0      + CP.y
	OPL.P2.z = PPRy.x
	
	
	# Calculate the corners on the Image plane, convert from 2D back to 3D
	IA.x = PA.x
	IA.y = PA.y
	IA.z = 0.0
	
	IB.x = PB.x
	IB.y = PB.y
	IB.z = 0.0
	
	IC.x = PC.x
	IC.y = PC.y
	IC.z = 0.0
	
	ID.x = PD.x
	ID.y = PD.y
	ID.z = 0.0
	
	# Calculate the 3D points on the Object plane in 3D
	OA = linePlaneIntersect(IA,PCF,OPL)
	OB = linePlaneIntersect(IB,PCF,OPL)
	OC = linePlaneIntersect(IC,PCF,OPL)
	OD = linePlaneIntersect(ID,PCF,OPL)
	
	# Calculate the distances between the points on the Object Plane
	AB = distancePointPoint3D(OA,OB)
	BC = distancePointPoint3D(OB,OC)
	CD = distancePointPoint3D(OC,OD)
	DA = distancePointPoint3D(OD,OA)
	
	Rx = angle(PPRx)
	Ry = angle(PPRy)
	Rz = anglePointPoint(PDC,PAB)
	
	if (AB + CD) != 0:
		r = (((BC + DA) * (ROW - 1) * RowHeight) / ((AB + CD) * (COLL - 1) * ColWidth) -  1 ) * 100
	else:
		r = 0
	return r, Rx, Ry, Rz


#
#
#
#
#



