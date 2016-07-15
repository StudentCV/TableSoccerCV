# TableSoccerCV
Table Soccer Video Analysis with OpenCV in Python - Basler dart / pulse Camera connected with PyPylon

During my own websearch couple of weeks ago I found some impressive demonstrations of video analysis setups for table soccer matches. But sadly none of those mostly university groups have published their code.

So not that long ago I began coding an OpenCV based ball-detection as a first step realizing the project. It became clear pretty fast that I won't be able to do all of the coding by myself, so I decided to release the project to all of you already although there still is a lot of work to be done before the project could somehow be called as "finished".

I focused a lot on writing the project code in a as modular way as possible so it will be easy to adapt new awesome features you might want to add to it. 

So here's what I've done for now

  - Basic structure with clear separation between 
    - camera interaction
    - several analyzing classes
    - a universal output class
  - Ball tracking with automatic color calibration
  - Field detection (orientation, scale, goal line, etc.) 
  - Goal detection and counting
  - ball speed calculation in m/s
  - Heatmap generation when a match is finished

Obviously there is plenty of work to do and probably you have even more **great** ideas what can be done for a great user experience. Here I some ideas which I would like to implement if I have enough time in the future.
  - ball prediction for a faster ball detection
  - Web-based user interface with a responsive design to be usable on any device with Bluetooth or wifi 

TableSoccerCV is hopefully just the beginning of some great *Open Source* table soccer video analysis projects. I hope you find my code useful!
Cheers,
StudentCV

### Version
0.1 - PreRelease

### Installation

You will need the following packages for python to get the code working:
* Python 3.4
* OpenCV 3.0
* PyPylon 1.0.5 Get it [here](https://github.com/StudentCV/PyPylon)
* NumPy
* Matplotlib

### Development

Want to contribute? Great!

The code itself is documented within the source code as much as possible. I'll also provide a short coding manual asap.

Feel free to add some great functionalities!

License
----
**Free Software, Hell Yeah!**

Copyright and related rights are licensed under the Solderpad Hardware License, Version 0.51 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law or agreed to in writing, software, hardware and materials distributed under this License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
