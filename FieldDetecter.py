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

# TODO: extensive commenting on calculations
import cv2
import numpy as np


class FieldDetection:
    """
    The soccer field is determined by the position of the center spot, the
    angle of the center line and the size of the center circle.
    Since the diameter of the center circle is fixed at 20.5 cm, all other
    points of the field can be calculated by these three measures.
    """

    field = 0
    center = 0
    ratio_pxcm = 0
    angle = 0
    goal_center_left = 0
    goal_center_right = 0
    goal_area_radius = 0

    def draw(self, image):
        """
        Draws the field borders and markers onto the image.
        :param image: The HSV-image to draw on
        :return: The image with the markers drawn
        """
        if self.field != 0:
            top_left = self.field[0]
            top_right = self.field[1]
            bottom_right = self.field[2]
            bottom_left = self.field[3]
            goal_center_right = self.goal_center_right
            goal_center_left = self.goal_center_left

            cv2.line(image, (top_left[0], top_left[1]), (top_right[0], top_right[1]), (120, 255, 255), 2)
            cv2.line(image, (top_right[0], top_right[1]), (bottom_right[0], bottom_right[1]), (120, 255, 255), 2)
            cv2.line(image, (bottom_right[0], bottom_right[1]), (bottom_left[0], bottom_left[1]), (120, 255, 255), 2)
            cv2.line(image, (bottom_left[0], bottom_left[1]), (top_left[0], top_left[1]), (120, 255, 255), 2)

            cv2.circle(image, (goal_center_left[0], goal_center_left[1]), self.goal_area_radius, (120, 255, 255), 2)
            cv2.circle(image, (goal_center_right[0], goal_center_right[1]), self.goal_area_radius, (120, 255, 255), 2)

        else:
            print('Feld wurde nicht ermittelt!')  # TODO: Interface message or error code in return value

        return image

    def get_center_scale(self, calibration_image):
        """

        :param calibration_image: The HSV-image to use for calculation
        :return: Position of center point in image (tuple), ratio px per cm (reproduction scale)
        """
        gray = cv2.cvtColor(calibration_image, cv2.COLOR_HSV2BGR)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 1)

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=50, param2=30, minRadius=50, maxRadius=300)

        center_circle = (0, 0, 0)
        min_dist = 0xFFFFFFFFFFF
        for circle in circles[0]:
            dist_x = abs(circle[0] - calibration_image.shape[1] / 2)
            dist_y = abs(circle[1] - calibration_image.shape[0] / 2)

            if(dist_x + dist_y) < min_dist:
                min_dist = dist_x + dist_y
                center_circle = circle

        rgb = cv2.cvtColor(calibration_image, cv2.COLOR_HSV2RGB)
        cv2.circle(rgb, (center_circle[0], center_circle[1]), center_circle[2], (0, 255, 0), 1)

        center = center_circle[0], center_circle[1]

        radius = center_circle[2]
        ratio_pxcm = radius / 10.25

        self.center = center
        self.ratio_pxcm = ratio_pxcm

        return [center, ratio_pxcm]

    def get_angle(self, calibration_image):
        """

        :param calibration_image: The HSV-image to use for calculation
        :return: Rotation angle of the field in image
        """
        # TODO: correct return value comment?
        rgb = cv2.cvtColor(calibration_image, cv2.COLOR_HSV2BGR)
        angle = 0
        count = 0

        gray = cv2.cvtColor(cv2.cvtColor(calibration_image, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        lines = cv2.HoughLines(edges, 1, np.pi/180, 110)

        if lines.shape[0]:
            line_count = lines.shape[0]
        else:
            raise Exception('field not detected')

        for x in range(line_count):

            for rho, theta in lines[x]:
                a = np.cos(theta)
                b = np.sin(theta)
                # print(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*a)
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*a)

                corr_angle = np.degrees(b)
                if corr_angle < 5:
                    # print(CorrAngle)
                    angle = angle + corr_angle
                    count = count + 1
                    cv2.line(rgb, (x1, y1), (x2, y2), (0, 0, 255), 2)
        print(angle)
        if isinstance(angle, int) and isinstance(count, int):
            angle = angle / count
            self.angle = angle
            return angle
        else:
            self.angle = 0.1
            return False

    def calc_field(self):
        """
        This method needs some class variables. get_angle and get_center_scale
        have to be called beforehand.
        :return: field edges [Top left, top right, bottom right and bottom left corner] (list)
        """

        half_field_width = 60
        half_field_height = 34

        # x1 = int(self.center[0])
        # y1 = int(self.center[1])

        angle_radial_scale = np.radians(self.angle)

        # x2 = int((self.center[0]) + np.tan(angle_radial_scale)*(HalfFieldHeight*self.ratio_pxcm))
        # y2 = int(self.center[1] - (HalfFieldHeight*self.ratio_pxcm))

        x2 = int(self.center[0] - (half_field_width * self.ratio_pxcm) + np.tan(angle_radial_scale) *
                 (half_field_height * self.ratio_pxcm))
        y2 = int(self.center[1] - np.tan(angle_radial_scale) * (half_field_width * self.ratio_pxcm) -
                 (half_field_height * self.ratio_pxcm))
        top_left = [x2, y2]

        x2 = int(self.center[0] + (half_field_width * self.ratio_pxcm) + np.tan(angle_radial_scale) *
                 (half_field_height * self.ratio_pxcm))
        y2 = int(self.center[1] + np.tan(angle_radial_scale) * (half_field_width * self.ratio_pxcm) -
                 (half_field_height * self.ratio_pxcm))
        top_right = [x2, y2]

        x2 = int(self.center[0] - (half_field_width * self.ratio_pxcm) - np.tan(angle_radial_scale) *
                 (half_field_height * self.ratio_pxcm))
        y2 = int(self.center[1] - np.tan(angle_radial_scale) * (half_field_width * self.ratio_pxcm) +
                 (half_field_height * self.ratio_pxcm))
        bottom_left = [x2, y2]

        x2 = int(self.center[0] + (half_field_width * self.ratio_pxcm) - np.tan(angle_radial_scale) *
                 (half_field_height * self.ratio_pxcm))
        y2 = int(self.center[1] + np.tan(angle_radial_scale) * (half_field_width * self.ratio_pxcm) +
                 (half_field_height * self.ratio_pxcm))
        bottom_right = [x2, y2]

        self.field = [top_left, top_right, bottom_right, bottom_left]
        return [top_left, top_right, bottom_right, bottom_left]

    def calc_goal_area(self):
        """
        The 'goal area' is the half circle around the goals. It is assumed,
        that the ball will be seen in a goal area before the score is
        incremented.
        :return: None
        """
        top_left = self.field[0]
        top_right = self.field[1]
        bottom_left = self.field[3]

        tlbl = bottom_left[0] - top_left[0], bottom_left[1] - top_left[1]  # Topleft to BottomLeft
        tltr = top_right[0] - top_left[0], top_right[1] - top_left[1]  # Topleft to TopRight

        self.goal_center_left = int(top_left[0] + (0.5 * tlbl[0])), int(top_left[1] + (0.5 * tlbl[1]))
        self.goal_center_right = int(self.goal_center_left[0] + tltr[0]), int(self.goal_center_left[1] + tltr[1])

        self.goal_area_radius = int(16 * self.ratio_pxcm)


    def get_var(self, _type):
        """
        Get the class variables
        :param _type: String to choose the variabe
        :return: The requested variable, empty string if requested name is
        unavailable
        """
        if 'GoalAreas' == _type:
            return [self.goal_center_left, self.goal_center_right, self.goal_area_radius]
        elif 'field' == _type:
            return self.field
        elif 'ratio_pxcm' == _type:
            return self.ratio_pxcm
        elif 'angle' == _type:
            return self.angle
        elif 'center' == _type:
            return self.center
        else:
            return ""  # False
