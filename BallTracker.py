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
import numpy as np


class BallTracker:
    # --- ball detection in a single image --- #

    ball_detection_threshold = 0.2
    interface = 0

    ball_color = (-1, -1, -1)
    curr_ball_position = (-1, -1)

    def __init__(self, interface):
        super().__init__
        self.interface = interface

    def draw(self, image):
        """
        Draws the ball marker onto the image.
        :param image: The HSV-image to draw on
        :return: The image with the marker drawn
        """
        if self.curr_ball_position != (-1, -1):
            cv2.circle(image, (self.curr_ball_position[0], self.curr_ball_position[1]), 2, (120, 255, 255), 2)
        else:
            #self.interface.message("No ball detected")
            pass
        
        return image

    def calibrate(self, img_hsv):
        """
        Calibration routine.
        Measures the color of the ball and stores it in the class.
        :param img_hsv: HSV-image to use for calculation.
        The ball has to be positioned in the center
        :return: None
        """
        x_center = int(round(img_hsv.shape[1]/2))
        y_center = int(round(img_hsv.shape[0]/2))

        # Get the color of the pixel in the image center
        color = img_hsv[y_center, x_center]

        # Create a mask for the areas with a color similar to the center pixel
        lower_border_arr = color - [20, 20, 20]
        upper_border_arr = color + [20, 20, 20]
        lower_border = tuple(lower_border_arr.tolist())
        upper_border = tuple(upper_border_arr.tolist())
        mask = cv2.inRange(img_hsv, lower_border, upper_border)

        # Average the color values of the masked area
        colors = img_hsv[mask == 255]
        h_mean = int(round(np.mean(colors[:, 0])))
        s_mean = int(round(np.mean(colors[:, 1])))
        v_mean = int(round(np.mean(colors[:, 2])))

        av = [h_mean, s_mean, v_mean]
        self.ball_color = tuple(av)

    def detect_ball_position(self, img_hsv):
        """
        Finds the ball in the image.

        The algorithm is based on the ball color and does not use edge
        recognition to find the ball. As long as the ball color differs from
        the other colors in the image, it works well and is a save way to find
        the ball.
        First, the image is searched for pixels with similar color to the ball
        color creatinga mask. The mask should contain a white point (the ball).
        To ensure that the ball is found, the contours of the mask are found.
        If there are more than one element with contours, a simple
        circle-similarity measure is calculated.
        The element with the highest similarity to a circle is considered as
        the ball.
        :param img_hsv: HSV-image to find the ball on
        :return: None
        """
        # TODO: also include the expected ball size into the decision
        x_mean = []
        y_mean = []
        dist = []
        self.curr_ball_position = (0, 0)

        # Get the areas of the image, which have a similar color to the ball color
        lower_color = np.asarray(self.ball_color)
        upper_color = np.asarray(self.ball_color)
        lower_color = lower_color - [10, 50, 50]  # good values (for test video are 10,50,50)
        upper_color = upper_color + [10, 50, 50]  # good values (for test video are 10,50,50)
        lower_color[lower_color < 0] = 0
        lower_color[lower_color > 255] = 255
        upper_color[upper_color < 0] = 0
        upper_color[upper_color > 255] = 255
        mask = cv2.inRange(img_hsv, lower_color, upper_color)
        mask = self._smooth_ball_mask(mask)

        # Find contours in the mask, at the moment only one contour is expected
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # For every contour found, the center is calculated (by averaging the
        # points), and the circe-comparison is done.
        element_ctr = 0
        for element in contours:
            element = element[:,0,:]
            x_mean.append(int(np.round(np.mean(element[:,0]))))
            y_mean.append(int(np.round(np.mean(element[:,1]))))
            element_ctr += 1

            dist.append(self._check_circle(element))

        if element_ctr <= 0 or min(dist) > self.ball_detection_threshold:
            # If there is nothin found or it does not look like a circle, it is
            # assumed that there is no ball in the image.
            self.curr_ball_position = (-1, -1)
            #print("No ball detected")  # TODO: give that message to the interface
        else:
            # Otherwise the element with the best similarity to a circle is chosen
            # to be considered as the ball.
            self.curr_ball_position = (x_mean[np.argmin(dist)], y_mean[np.argmin(dist)])

        self.__store_ball_position(self.curr_ball_position)

    def _smooth_ball_mask(self, mask):
        """
        The mask created inDetectBallPosition might be noisy.
        :param mask: The mask to smooth (Image with bit depth 1)
        :return: The smoothed mask
        """
        # create the disk-shaped kernel for the following image processing,
        r = 3
        kernel = np.ones((2*r, 2*r), np.uint8)
        for x in range(0, 2*r):
            for y in range(0, 2*r):
                if(x - r + 0.5)**2 + (y - r + 0.5)**2 > r**2:
                    kernel[x, y] = 0

        # remove noise
        # see http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask

    def _check_circle(self, points):
        """
        Calculates a comparison value with a circle.
        First, it normalizes the given points, so that their mean is the origin and their distance to the origin
        is 1 in average.
        Then it averages the differences between the points' distance to the origin and 1.
        The resulting value is 0 when the points form a circle, and increases, if there is any deformation.
        It has no upper limit, but will not be smaller than 0.
        To sum up: the lower the value, the better fit the points to a circle
        :param points: the points that mark the contour to check
        :return: Comparison value.
        """
        # Split x- and y-Values into two arrays
        x_vals, y_vals = [], []
        for point in points:
            x_vals.append(point[0])
            y_vals.append(point[1])

        # Shift the circle center to (0,0)
        x_vals = x_vals - np.mean(x_vals)
        y_vals = y_vals - np.mean(y_vals)

        # Bring the circle radius to 1
        radius = np.sqrt((np.sum(x_vals**2 + y_vals**2)) / len(x_vals))
        for point in range(0, len(x_vals)):
            x_vals[point] = x_vals[point]/radius
            y_vals[point] = y_vals[point]/radius

        # Now the result is compared to a unit circle (radius 1), and the
        # differences are averaged.
        dist = np.mean(np.abs(x_vals**2 + y_vals**2 - 1))

        return dist

    ball_position_history = []

    def __store_ball_position(self, ball_position):
        """

        :param ball_position:
        :return:
        """
        if ball_position is not (-1, -1):
            self.ball_position_history.append([ball_position])

    def get_var(self, _type):
        """
        Get the class variables
        :param _type: String to choose the variabe
        :return: The requested variable, empty string if requested name is
        unavailable
        """
        if 'ball_position' == _type:
            return self.curr_ball_position
        elif 'ball_position_history' == _type:
            return self.ball_position_history
        else:
            return ""  # False

    def restart(self):
        """
        Clears the ball position history
        :return: None
        """
        self.ball_position_history = []
