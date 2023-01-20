import cad as cad
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from Intradox.BeltPitch import imageLine, imageCircle


# from Intradox.BeltPitch import imageLine, imageCircle


def autoCorrelate(frame):
	h1 = frame.shape[0]
	w1 = frame.shape[1]
	kernel_size = w1
	kernelH = np.zeros((kernel_size,kernel_size))
	kernelV = np.zeros((kernel_size,kernel_size))
	kernelH [:,int((kernel_size - 1) /2)] = np.ones(kernel_size)
	kernelV [int((kernel_size - 1) /2),:] = np.ones(kernel_size)
	kernelH /= kernel_size
	kernelV /= kernel_size
	
	hh11 = h1//2
	hh01 = h1//2
	
	wh11 = w1//12
	wh01 = w1//2 - (wh11//2)
	
	
	hw11 = h1//12
	hw01 = h1//2 - (hw11//2)
	
	ww11 = w1//2
	ww01 = w1//2
	
	plt.clf()
	datH = []
	datV = []
	dataPointsH = [[],[]]
	dataPointsV = [[],[]]
	fftDat =[]
	for i in range(0,2):
		
		img_cropFullWidth  = frame[hh01 * i: (hh01*i)+hh11, 0      : w1]
		img_cropFullHeight = frame[0       : h1           , ww01*i : (ww01*i)+ww11]
		
		img_cropFullWidth  = cv2.blur(img_cropFullWidth,(20,20),0)
		img_cropFullHeight = cv2.blur(img_cropFullHeight,(20,20),0)
		
		img_cropFullWidth  = cv2.cvtColor(img_cropFullWidth, cv2.COLOR_BGR2GRAY)
		img_cropFullHeight = cv2.cvtColor(img_cropFullHeight, cv2.COLOR_BGR2GRAY)
		
		img_cropFullWidth  = cv2.filter2D(img_cropFullWidth, -1, kernelH)
		img_cropFullHeight = cv2.filter2D(img_cropFullHeight, -1, kernelV)
		
		cv2.normalize(img_cropFullWidth,img_cropFullWidth, 0, 255, cv2.NORM_MINMAX)
		
		datH.append(img_cropFullWidth)
		datV.append(img_cropFullHeight)
		
		img_cropH = img_cropFullWidth [0    : img_cropFullWidth.shape[0], wh01 : wh01+wh11]
		img_cropV = img_cropFullHeight[hw01 : hw01+hw11                 , 0    : img_cropFullHeight.shape[1]]
		
		datH.append(img_cropH)
		datV.append(img_cropV)
		plt.subplot(413)
		plt.plot(img_cropFullWidth[i],'-')
		
		fftDat.append(img_cropFullWidth)
		
		#img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
		
		Method = cv2.TM_CCOEFF_NORMED
		resultH = cv2.matchTemplate(img_cropFullWidth,img_cropH,Method)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultH)
		#print(resultH)
		plt.subplot(411)
		plt.xlim = w1
		plt.plot(w1,0)
		plt.plot(resultH[0],'-')
		plt.plot(max_loc[0],max_val,'o')
		plt.plot(min_loc[0],min_val,'+')
		
		print(i , cad.correlate(resultH[0],img_cropFullWidth[i].astype(int)), end = ' ')
		
		x = max_loc[0] + (wh11 / 2)
		y = hh11 / 2 + ((hh11) * i) 
		dataPointsH[i].append((x,y))
		
		while max_val >= 0.5:
			# black out the area where the point was found to allow finding the next best 
			cv2.rectangle(resultH,(max_loc[0] - (wh11//2), 0), (max_loc[0] + (wh11//2),1), 0, -1)
			min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultH)
			# add the found point to the list of points
			if (max_val >= 0.5) and (max_loc[0] != 0) and (max_loc[0] <= w1 - (wh11 * 2) - 1):
				plt.plot(max_loc[0],max_val,'o')
				x = max_loc[0] + (wh11 / 2)
				y = hh11 / 2 + ((hh11) * i) 
				dataPointsH[i].append((x,y))
		
		Method = cv2.TM_CCOEFF_NORMED
		resultV = cv2.matchTemplate(img_cropFullHeight,img_cropV,Method)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultV)
		resultVT = np.array(resultV).T.tolist()
		
		plt.subplot(412)
		plt.xlim = w1
		plt.plot(w1,0)
		
		plt.plot(resultVT[0],'-')
		plt.plot(max_loc[1],max_val,'o')
		
		x = ww11 / 2 + ((ww11) * i) 
		y = max_loc[1] + (hw11 / 2)
		dataPointsV[i].append((x,y))
		
		while max_val >= 0.5:
			# black out the area where the point was found to allow finding the next best 
			cv2.rectangle(resultV,(0,max_loc[1] - (hw11//2)),( 1,max_loc[1] + (hw11//2)), 0, -1)
			min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultV)
			# add the found point to the list of points
			if (max_val >= 0.5) and (max_loc[1] != 0) and (max_loc[1] <= h1 - (hw11 * 2) -1):
				plt.plot(max_loc[1],max_val,'o')
				x = ww11 / 2 + ((ww11) * i) 
				y = max_loc[1] + (hw11 / 2)
				dataPointsV[i].append((x,y))
	
	plt.subplot(414)
	#subpl = img_cropFullWidth[0] + img_cropFullWidth[1]
	
	# FFT...
	#print(img_cropFullWidth[0]-128)
	temp = (fftDat[0][0].astype(int)) - np.mean(fftDat[0][0])
	#print(temp)
	mfft=np.fft.fft(temp)
	imax=np.argmax(np.absolute(mfft))
	mask=np.zeros_like(mfft)
	mask[[imax]] = 1
	mfft*=mask
	fdata=np.fft.ifft(mfft)
	plt.plot(fdata,'-')
	
	temp1 = (fftDat[1][0].astype(int)) - np.mean(fftDat[1][0])
	mfft1=np.fft.fft(temp1)
	imax1=np.argmax(np.absolute(mfft1))
	mask1=np.zeros_like(mfft)
	mask1[[imax1]] = 1
	mfft1*=mask1
	fdata1=np.fft.ifft(mfft1)
	plt.plot(fdata1,'-')
	
	plt.draw()
	plt.pause(1e-17)
	
	# sort and correct the data sets for H
	tempX, tempY = dataPointsH[0][0]
	dataPointsH[0] = sorted(dataPointsH[0], key=lambda tup: tup[0])
	dataPointsH[1] = sorted(dataPointsH[1], key=lambda tup: tup[0])
	count0 = 0
	for pt in dataPointsH[0]:
		if pt[0] < tempX:
			count0 += 1
	count1 = 0
	for pt in dataPointsH[1]:
		if pt[0] < tempX:
			count1 += 1
	while (count0 != count1):
		if count0 < count1:
			dataPointsH[1].pop(0)
			count1 -= 1
		else:
			dataPointsH[0].pop(0)
			count0 -= 1
	
	# sort and correct the data sets for V
	tempX, tempY = dataPointsV[0][0]
	dataPointsV[0] = sorted(dataPointsV[0], key=lambda tup: tup[1])
	dataPointsV[1] = sorted(dataPointsV[1], key=lambda tup: tup[1])
	count0 = 0
	for pt in dataPointsV[0]:
		if pt[1] < tempY:
			count0 += 1
	count1 = 0
	for pt in dataPointsV[1]:
		if pt[1] < tempY:
			count1 += 1
			
	while (count0 != count1):
		if count0 < count1:
			dataPointsV[1].pop(0)
			count1 -= 1
		else:
			dataPointsV[0].pop(0)
			count0 -= 1
	
	for i in range(min(len(dataPointsH[0]),len(dataPointsH[1]))):
		p1 = cad.Point()
		p2 = cad.Point()
		p1.x, p1.y = dataPointsH[0][i]
		p2.x, p2.y = dataPointsH[1][i]
		imageLine(p1,p2,(0.255,255))
		imageCircle(p1,(255,255,0))
		imageCircle(p2,(255,0,255))
		
	for i in range(min(len(dataPointsV[0]),len(dataPointsV[1]))):
		p1 = cad.Point()
		p2 = cad.Point()
		p1.x, p1.y = dataPointsV[0][i]
		p2.x, p2.y = dataPointsV[1][i]
		imageLine(p1,p2,(0.255,255))
		imageCircle(p1,(255,255,0))
		imageCircle(p2,(255,0,255))
		
	p1 = cad.Point()
	p2 = cad.Point()
	p3 = cad.Point()
	p4 = cad.Point()
	p1.x, p1.y = dataPointsH[0][0]
	p2.x, p2.y = dataPointsH[1][0]
	
	p3.x, p3.y = dataPointsV[0][0]
	p4.x, p4.y = dataPointsV[1][0]
	PA = cad.lineIntersect(p1,p2,p3,p4)
	
	p3.x, p3.y = dataPointsV[0][min(len(dataPointsV[0]),len(dataPointsV[1]))-1]
	p4.x, p4.y = dataPointsV[1][min(len(dataPointsV[0]),len(dataPointsV[1]))-1]
	PB = cad.lineIntersect(p1,p2,p3,p4)
	
	p1.x, p1.y = dataPointsH[0][min(len(dataPointsH[0]),len(dataPointsH[1]))-1]
	p2.x, p2.y = dataPointsH[1][min(len(dataPointsH[0]),len(dataPointsH[1]))-1]
	PC = cad.lineIntersect(p1,p2,p3,p4)
	
	p3.x, p3.y = dataPointsV[0][0]
	p4.x, p4.y = dataPointsV[1][0]
	PD = cad.lineIntersect(p1,p2,p3,p4)
	
	coll = min(len(dataPointsH[0]),len(dataPointsH[1]))
	row  = min(len(dataPointsV[0]),len(dataPointsV[1]))
	
	
	
	count = 0
	for img in datH:
		cv2.imshow(str(count),img)
		count += 1
	
	return PA,PB,PC,PD, coll, row

def imagePrint2(captionStr,p,color,size,width):
	global frame
	frame_PIL = Image.fromarray(frame)
	draw = ImageDraw.Draw(frame_PIL)
	font = ImageFont.truetype("courbd.ttf",size)
	#if width <= 1:
	#	font = ImageFont.truetype("cour.ttf",size)
	#	width = 0
	#else:
	#	font = ImageFont.truetype("courbd.ttf",size)
	#	width -= 1
	
	if color == (0,0,0):
		#cv2.putText(frame, captionStr, (p[0]-1,p[1]-1), font, size, (255,255,255), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]+1,p[1]-1), font, size, (255,255,255), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]+1,p[1]+1), font, size, (255,255,255), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]-1,p[1]+1), font, size, (255,255,255), width, cv2.LINE_AA)
		draw.text((p[0]-width,p[1]-width),captionStr,(255,255,255),font)
		draw.text((p[0]+width,p[1]-width),captionStr,(255,255,255),font)
		draw.text((p[0]+width,p[1]+width),captionStr,(255,255,255),font)
		draw.text((p[0]-width,p[1]+width),captionStr,(255,255,255),font)
	else:
		#cv2.putText(frame, captionStr, (p[0]-1,p[1]-1), font, size, (0,0,0), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]+1,p[1]-1), font, size, (0,0,0), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]+1,p[1]+1), font, size, (0,0,0), width, cv2.LINE_AA)
		#cv2.putText(frame, captionStr, (p[0]-1,p[1]+1), font, size, (0,0,0), width, cv2.LINE_AA)
		draw.text((p[0]-width,p[1]-width),captionStr,(0,0,0),font)
		draw.text((p[0]+width,p[1]-width),captionStr,(0,0,0),font)
		draw.text((p[0]+width,p[1]+width),captionStr,(0,0,0),font)
		draw.text((p[0]-width,p[1]+width),captionStr,(0,0,0),font)
	#cv2.putText(frame, captionStr, p, font, size, color, width, cv2.LINE_AA)
	for i in range(width - 1):
		draw.text((p[0]-i,p[1]-i),captionStr,color,font)
		draw.text((p[0]+i,p[1]-i),captionStr,color,font)
		draw.text((p[0]+i,p[1]+i),captionStr,color,font)
		draw.text((p[0]-i,p[1]+i),captionStr,color,font)
	draw.text(p,captionStr,color,font)
	frame = np.array(frame_PIL)
#
#
#
#
#