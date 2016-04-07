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


class PythonInterface:
    """
    Class for interfaces.
    """
    def run(self):
        """

        :return: Boolean, 1 if the analysis shall be executed, 0 if not
        """
        return True
        pass

    def show_image(self, image, draw=[]):
        """

        :param image:
        :param draw:
        :return: None
        """
        if 0 != draw:
            for task in draw:
                image = task(image)

        plt.figure()
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_HSV2RGB))
        plt.show()

    total_frame_time = 0

    def show_video(self, frame, get_source_var, draw=[]):
        """

        :param frame: HSV-image
        :param get_source_var:
        :param draw:
        :return:
        """
        frame_time = get_source_var('FrameTime')
        self.total_frame_time = self.total_frame_time + frame_time

        #print(1/frame_time)

        if self.total_frame_time >= (1/30):

            if 0 != draw:
                for task in draw:
                    frame = task(frame)

            cv2.imshow('Soccer', cv2.cvtColor(frame, cv2.COLOR_HSV2BGR))
            cv2.waitKey(1)
            self.total_frame_time = 0
        else:
            return

    start_session = {"key": 0, "text": "Start a sesstion"}
    start_calibration = {"key": 1, "text": "Start calibration"}
    start_match = {"key": 2, "text": "Start the match"}

    def wait_for_user_command(self, command):
        """
        Returns if the desired command is issued by user.
        No time limit!
        :param command:
        :return:
        """
        #self.message(command["text"]+"?")

        #input(command["text"]+"?")

        return True

    def message(self, message):
        """
        prints the message text
        :param message: string
        :return:
        """
        print(message)
