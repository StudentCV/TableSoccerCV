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

import pylon as py
import numpy as np
import matplotlib.pylab as plt

import cv2



icam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())
icam.Open()

icam.PixelFormat = "RGB8"

icam.StartGrabbing(100)

while(icam.IsGrabbing):
	gray = icam.RetrieveResult

	print(type(gray))
	print(1)
	#cv2.imshow('frame',gray)

	#register configuration