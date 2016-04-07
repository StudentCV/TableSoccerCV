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

import math
import cv2
import numpy as np


class GameplayAnalyser:
    ball_history = []
    # is_goal_possible = True
    goal_time_threshold_s = 1000
    last_ball_in_field_time = 0
    is_ball_in_goal_area = False, 'none'
    is_ball_in_field = False
    is_real_goal = 0

    match_score = (0, 0)

    def draw(self, image):

        cv2.putText(image, str(self.match_score[0]) + " - " + str(self.match_score[1]), (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 255, 50), 2)
        cv2.putText(image, "Speed: " + str(round(self.ball_speed_average, 2)) + "m/s", (400, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 255, 50), 2)

        return image

    def count_score(self, goal_status):

        if goal_status == 'Left':
            self.match_score = (self.match_score[0] + 1, self.match_score[1])
        elif goal_status == 'Right':
            self.match_score = (self.match_score[0], self.match_score[1] + 1)

    def check_for_goal(self, get_ball_var, get_field_var):
        """

        :param get_ball_var:
        :param get_field_var:
        :return: Information, whether a team scored and which one, if necessary
        """
        ball_position = get_ball_var('ball_position')

        # IsBallInField ---------------------------------------------------------------
        self.is_ball_in_field = True  # Ball innerhalb des Feldes

        if (-1, -1) == ball_position:  # If Ball is not in field (-1,-1) is returned
            self.is_ball_in_field = False
        else:
            self.is_ball_in_field = True

            # is_ball_in_goal_area ----------------------------------------------------------------------------------
            goal_areas = get_field_var('GoalAreas')
            goal_center_left = goal_areas[0]
            goal_center_right = goal_areas[1]
            goal_area_radius = goal_areas[2]

            distance_left = math.sqrt((ball_position[0] - goal_center_left[0]) ** 2 + (ball_position[1] -
                                                                                       goal_center_left[1]) ** 2)
            distance_right = math.sqrt((ball_position[0] - goal_center_right[0]) ** 2 + (ball_position[1] -
                                                                                         goal_center_right[1]) ** 2)

            if distance_left <= goal_area_radius:
                self.is_ball_in_goal_area = True, 'Left'
            elif distance_right <= goal_area_radius:
                self.is_ball_in_goal_area = True, 'Right'
            else:
                self.is_ball_in_goal_area = False, 'none'

        # How long has the bass disappeared -----------------------------------------------------------------------
        if self.is_ball_in_field is False and self.is_ball_in_goal_area[0] is True:

                self.is_real_goal = self.is_real_goal + 1

                if self.is_real_goal >= 50:
                    # print(1111)

                    return_value = self.is_ball_in_goal_area[1]
                    self.is_real_goal = 0
                    self.is_ball_in_goal_area = False, 'none'
                    return return_value
                else:
                    return False

        else:
            return False

    last_ball_position = 0
    ball_position = 0
    # current_speed_ms = 0

    def __calc_ball_speed(self, get_source_var, get_ball_var, get_field_var):

        self.ball_position = get_ball_var('ball_position')

        if self.ball_position != (-1, -1):
            ratio_pxcm = get_field_var('ratio_pxcm')
            frame_time = get_source_var('FrameTime')

            if self.last_ball_position == 0:
                self.last_ball_position = self.ball_position

            bp = self.ball_position
            lbp = self.last_ball_position

            # bp = self.last_ball_position

            # print(lbp[0])

            distance_px = math.sqrt((bp[0]-lbp[0])*(bp[0]-lbp[0])+(bp[1]-lbp[1])*(bp[1]-lbp[1]))
            distance_cm = distance_px / ratio_pxcm
            distance_m = distance_cm / 100

            self.speed_ms = distance_m / frame_time
            self.last_ball_position = self.ball_position

            return self.speed_ms
        else:
            return False

    ball_speed_average_counter = [0]

    def calc_ball_speed_average(self, get_source_var, get_ball_var, get_field_var, accuracy=10):

        current_speed = self.__calc_ball_speed(get_source_var, get_ball_var, get_field_var)

        if current_speed is not False:
            self.ball_speed_average_counter.extend([current_speed])

        if len(self.ball_speed_average_counter) > accuracy:
            self.ball_speed_average_counter = self.ball_speed_average_counter[-accuracy:]

        self.ball_speed_average = sum(self.ball_speed_average_counter) / len(self.ball_speed_average_counter)

        return self.ball_speed_average

    def heatmap(self, get_ball_var):

        heat_values = get_ball_var('ball_position_history')

        # Generate some test data
        x = np.random.randn(8873)
        y = np.random.randn(8873)

        heatmap, xedges, yedges = np.histogram2d(x, y, bins=50)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

        # x = np.random.randn(100000)
        y = np.random.randn(100000)

        #  print(y)

        # plt.hist2d(HeatValues[0],HeatValues[1],bins=100);

        # plt.clf()
        # plt.imshow(heatmap, extent=extent)
        # plt.show()

    def get_var(self, _type):
        if 'match_score' == _type:
            return self.match_score
#        elif 'FrameCount' == _type:
#            return self.frame_count
        else:
            return ""  # False
