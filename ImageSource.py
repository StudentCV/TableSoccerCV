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

import cv2
import pypylon.pylon as py
import time


class ImageSource:
    """
    Class for any image source. It can be a Video, but also a live image from
    a camera
    """
    
    #cap = cv2.VideoCapture(r'.\Video.avi')
    cap = cv2.VideoCapture(r'C:\Users\lzuber\Desktop\TableSoccer2016\PylonTableSoccer\Video.avi')
    grab_status = False
    
    frame_count = 0
    frame_rate = 0

    def init(self):  # TODO: init or __init__?
        return

        self.icam = py.InstantCamera(py.TlFactory.GetInstance().CreateFirstDevice())

        self.icam.Close()

        self.icam.RegisterConfiguration(
            py.AcquireContinuousConfiguration(),
            py.RegistrationMode_ReplaceAll,
            py.Cleanup_Delete
        )

        self.icam.Open()

        self.icam.PixelFormat = "RGB8"

        self.icam.MaxNumBuffer = 2000

        pass

    def start_grab(self):

        self.grab_status = True
        return True

        if self.icam:
            self.icam.StartGrabbing(py.GrabStrategy_LatestImages)
            self.grab_status = True
            return True
        else:
            self.grab_status = False
            return False

    def get_newest_frame(self):

        live = 0

        if live == 1:
            if self.grab_status:

                with self.icam.RetrieveResult(200, py.TimeoutHandling_Return) as result:

                    image = cv2.cvtColor(result.Array, cv2.COLOR_RGB2HSV)

                    self.frame_count = self.frame_count + 1
                    self.__calc_frametime(time.time())
                    return image
            else:
                raise Exception('Camera not Grabbing')
        else:
            if self.cap.isOpened():

                ret, frame = self.cap.read()
                # cv2.imshow('Soccer', cv2.cvtColor(frame,cv2.COLOR_HSV2BGR))
                cv2.imshow('Soccer', frame)

                self.frame_count = self.frame_count + 1
                self.__calc_frametime(time.time())
                return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            else:
                self.cap.release()
                cv2.destroyAllWindows()


    def new_image_available(self):
        """

        :return: Is there a new image to get?
        """
        return True
        pass

    def get_var(self, _type):

        if 'frame_count' == _type:
            return self.frame_count
        elif 'FrameRate' == _type:
            return self.frame_rate
        elif 'FrameTime' == _type:
            return self.frametime
        else:
            return ""  # False

    last_timestamp = 0

    def __calc_frametime(self, timestamp):

        if 0 == self.last_timestamp:
            self.last_timestamp = timestamp
        else:
            period = timestamp - self.last_timestamp
            self.last_timestamp = timestamp

            self.frame_rate = 1 / period
            self.frametime = period

            # print(self.frame_rate)
