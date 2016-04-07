#Copyright 2016 StudentCV
#Copyright and related rights are licensed under the
#Solderpad Hardware License, Version 0.51 (the “License”);
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at http://solderpad.org/licenses/SHL-0.51.
#Unless required by applicable law or agreed to in writing,
#software, hardware and materials distributed under this License
#is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
#either express or implied. See the License for the specific language
#governing permissions and limitations under the License.

import matplotlib.pyplot as plt
import cv2
import numpy as np
import math

class DetectFieldClass:
    """Takes an image and processes it to give back the ball's and field corners' positions"""
    ImgHSV = 0
    xMean, yMean = [],[]
    dist = []
    BallCenter = (0,0)
    BallContours = []
    FieldContours = []

    def SetImage(self, image):
        """
        Copies the image to internal memory
        :param image: numpy array containing the BGR imagedata
        :return: none
        """

        self.ImgHSV = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)


    def FindField(self):
        #Feld: Hue zwischen 60 und 100
        LowerGreen = np.array([40,0,0])
        UpperGreen = np.array([90,255,150])
        mask = cv2.inRange(self.ImgHSV,LowerGreen,UpperGreen)

#        plt.figure()
#        plt.imshow(mask,cmap='gray')

        mask = self.SmoothFieldMask(mask)
#        plt.figure()
#        plt.imshow(mask.copy(),cmap='gray')

        im2, contours, hierarchy = cv2.findContours(mask.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if(len(contours) <= 0):
            return
        contours_sorted = sorted(contours, key = cv2.contourArea, reverse=True)[:10]

        peri = cv2.arcLength(contours_sorted[0],True)
        approx = cv2.approxPolyDP(contours_sorted[0], 0.02*peri, True)

        if(len(approx) >-1):#== 4):
            self.FieldContours = approx
            cv2.rectangle(mask,(((self.FieldContours[0])[0])[0],((self.FieldContours[0])[0])[1]),(((self.FieldContours[2])[0])[0],((self.FieldContours[2])[0])[1]),(128,128,128),3)
  #          plt.imshow(mask, cmap="gray")
  #          plt.show()


    def ShowImage(self):
        """
        Opens the image in a window with the ball marked red
        :return:
        """
        rgb = cv2.cvtColor(self.ImgHSV,cv2.COLOR_HSV2RGB)

        if(len(self.FieldContours) > 0):
            cv2.drawContours(rgb,self.FieldContours,-1,(0,0,0),3,lineType=cv2.LINE_8)
            cv2.rectangle(rgb,(((self.FieldContours[0])[0])[0],((self.FieldContours[0])[0])[1]),(((self.FieldContours[2])[0])[0],((self.FieldContours[2])[0])[1]),(0,0,0),3)
        cv2.circle(rgb,self.BallCenter, 2, (255,0,0), 2)
        #plt.imshow(rgb)
       # plt.show()
        #cv2.imshow('frame',cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR))


#    def CreateMask(self, LowerBorder, UpperBorder):
        """
        Internal function. Creates a mask by color
        :param LowerBorder: Lower border of the color to match (HSV)
        :param UpperBorder: Higher border of the color to match (HSV)
        :return: mask array
        """
        # Find Image areas, that have the right color and thus may contain the ball
#        mask = cv2.inRange(self.ImgHSV,LowerBorder,UpperBorder)

        #plt.imshow(cv2.cvtColor(cv2.bitwise_and(self.ImgHSV,self.ImgHSV,mask=mask),cv2.COLOR_HSV2RGB),cmap="gray")
        #plt.show()

 #      return mask

    def SmoothFieldMask(self, mask):
        # erst Close und dann DILATE führt zu guter Erkennung der Umrandung oben

        kernel = np.ones((20,20),np.uint8)


        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        #kernel = np.ones((20,20),np.uint8)
    #mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        #kernel = np.ones((20,20),np.uint8)

        mask = cv2.GaussianBlur(mask,(11,11),0)

        #mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)

    #    plt.imshow(cv2.cvtColor(cv2.bitwise_and(self.ImgHSV,self.ImgHSV,mask=mask),cv2.COLOR_HSV2RGB),cmap="gray")
     #   plt.show()

        return mask

    def FindCircle(self):

        gray = cv2.cvtColor(self.ImgHSV,cv2.COLOR_HSV2BGR)
        gray = cv2.cvtColor(gray,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(5,5),1)

        circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,100,param1=50,param2=30,minRadius=50,maxRadius=300)

        CenterCircle = (0,0,0)
        minDist = 0xFFFFFFFFFFF
        for circle in circles[0]:
            distX = abs(circle[0] - self.ImgHSV.shape[1]/2)
            distY = abs(circle[1] - self.ImgHSV.shape[0]/2)

            if((distX+distY) < minDist):
                minDist = distX+distY
                CenterCircle = circle

        rgb = cv2.cvtColor(self.ImgHSV,cv2.COLOR_HSV2RGB)
        cv2.circle(rgb, (CenterCircle[0], CenterCircle[1]), CenterCircle[2], (0,255,0), 1)

        Center = (CenterCircle[0],CenterCircle[1])
        Radius = (CenterCircle[2])

        RatioPxCm = Radius / 10.25
        HalfFieldWidth = 60
        HalfFieldHeight = 34
        
        
       # print(pxcm)
        x1 = int(Center[0])
        y1 = int(Center[1])

        AngleRadialScale = np.radians(self.angle)


        #x2 = int((center[0]) + np.tan(AngleRadialScale)*(HalfFieldHeight*ratio_pxcm))
        #y2 = int(center[1] - (HalfFieldHeight*ratio_pxcm))

        x2 = int(Center[0] - (HalfFieldWidth*RatioPxCm) + np.tan(AngleRadialScale)*(HalfFieldHeight*RatioPxCm))
        y2 = int(Center[1] - np.tan(AngleRadialScale)*(HalfFieldWidth*RatioPxCm) - (HalfFieldHeight*RatioPxCm))
        TopLeft = [x2, y2]

        x2 = int(Center[0] + (HalfFieldWidth*RatioPxCm) + np.tan(AngleRadialScale)*(HalfFieldHeight*RatioPxCm))
        y2 = int(Center[1] + np.tan(AngleRadialScale)*(HalfFieldWidth*RatioPxCm) - (HalfFieldHeight*RatioPxCm))
        TopRight = [x2, y2]

        x2 = int(Center[0] - (HalfFieldWidth*RatioPxCm) - np.tan(AngleRadialScale)*(HalfFieldHeight*RatioPxCm))
        y2 = int(Center[1] - np.tan(AngleRadialScale)*(HalfFieldWidth*RatioPxCm) + (HalfFieldHeight*RatioPxCm))
        BottomLeft = [x2, y2]

        x2 = int(Center[0] + (HalfFieldWidth*RatioPxCm) - np.tan(AngleRadialScale)*(HalfFieldHeight*RatioPxCm))
        y2 = int(Center[1] + np.tan(AngleRadialScale)*(HalfFieldWidth*RatioPxCm) + (HalfFieldHeight*RatioPxCm))
        BottomRight = [x2, y2]


        cv2.line(rgb,(TopLeft[0],TopLeft[1]),(TopRight[0],TopRight[1]),(0,0,255),2)
        cv2.line(rgb,(TopRight[0],TopRight[1]),(BottomRight[0],BottomRight[1]),(0,0,255),2)
        cv2.line(rgb,(BottomRight[0],BottomRight[1]),(BottomLeft[0],BottomLeft[1]),(0,0,255),2)
        cv2.line(rgb,(BottomLeft[0],BottomLeft[1]),(TopLeft[0],TopLeft[1]),(0,0,255),2)

        #cv2.rectangle(rgb,(TopLeft[0],TopLeft[1]),(BottomRight[0],BottomRight[1]),(0,255,0),2)

        cv2.imshow('frame', rgb)


    def FindSkeleton(self):

        rgb = cv2.cvtColor(self.ImgHSV, cv2.COLOR_HSV2BGR)
        angle = 0
        count = 0

        gray = cv2.cvtColor(cv2.cvtColor(self.ImgHSV,cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,50,150,apertureSize = 3)

        lines = cv2.HoughLines(edges,1,np.pi/180,110)

        #print (lines)
        line_count = lines.shape[0]

        for x in range(line_count):

            for rho,theta in lines[x]:
                a = np.cos(theta)
                b = np.sin(theta)
                #print(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))

                crr_angle = np.degrees(b)
                if (crr_angle < 5):
                    #print(crr_angle)
                    angle = angle + crr_angle
                    count = count + 1
                    cv2.line(rgb,(x1,y1),(x2,y2),(0,0,255),2)

        angle = angle / count
        self.angle = angle
        return (angle)