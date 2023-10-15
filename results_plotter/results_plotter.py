import cv2
import numpy as np
import pandas as pd

import time

class ResultsPlotter:
    """
    Open map and display teams moving around map and summary stats
    """
    def __init__(self, config: dict, results: "dict[str, pd.Dataframe]"):
        self.config = config
        self.results = results
        self.map = cv2.imread(self.config["map_file"])

    def plot_results(self) -> None:
        """
        Main method to start results replay
        """
        map_window_name = "Results Replay"
        cv2.namedWindow(map_window_name, cv2.WINDOW_NORMAL)

        stats_window_name = "Summary Stats Window"
        cv2.namedWindow(stats_window_name, cv2.WINDOW_NORMAL)

        while True:
            white_background = np.ones((500, 500, 3))
            cv2.putText(white_background, str(time.time()), 
                        (100,100),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1,
                        color=(255, 0, 0),
                        thickness=2,
                        lineType=2)
            cv2.imshow(map_window_name, self.map)
            cv2.imshow(stats_window_name, white_background)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()