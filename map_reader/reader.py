import csv
from pathlib import Path

import cv2
import easygui

from utils import PixelCoordinate

class ControlCoordinatesReader:
    """
    Module to interactively select controls from map and get pixel coordinates
    """
    def __init__(self, config: dict):
        self.config = config
        self.map = cv2.imread(self.config["map_file"])
        self.coordinates = {}

    def click_event(self, event, x, y, flags, params) -> None:
        """
        Source: https://www.tutorialspoint.com/opencv-python-how-to-display-the-coordinates-of-points-clicked-on-an-image
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            control_id = easygui.enterbox("Enter Control ID e.g. HH, 20, 57, etc", "Control ID Input", "")
            self.coordinates[control_id] = PixelCoordinate(x, y)
            
            # draw point on the image
            cv2.circle(self.map, (x,y), 10, (0, 0, 255), -1)

    def open_map(self) -> None:
        """
        Open map file and bind mouse click to event
        """
        # create window for map
        map_window_name = "Control Coordinates Selection"
        cv2.namedWindow(map_window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(map_window_name, self.click_event)

        while True:
            cv2.imshow(map_window_name, self.map)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()

    def write_coordinates(self) -> None:
        """
        Write the control coordinates to a csv
        """
        filepath = Path(self.config["control_coordinates"])
        with open(filepath, "w") as coordinates_fp:
            csvwriter = csv.writer(coordinates_fp)
            csvwriter.writerow(["control", "pixel_x", "pixel_y"])
            for control_id, coordinate in self.coordinates.items():
                csvwriter.writerow([control_id, coordinate.x, coordinate.y])
