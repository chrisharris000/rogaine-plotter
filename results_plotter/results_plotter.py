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
            # start with blank canvas for stats
            stats_width, stats_height = 750, 750
            stats_background = np.ones((stats_width, stats_height, 3))

            stats_background = self.add_stats_text(stats_background)

            cv2.imshow(map_window_name, self.map)
            cv2.imshow(stats_window_name, stats_background)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

        cv2.destroyAllWindows()

    def add_stats_text(self, stats_background) -> np.ndarray:
        stats_font_settings = {
            "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
            "fontScale": 1,
            "color": (255, 0, 0),
            "thickness": 2,
            "lineType": 2
        }

        # stats page title
        cv2.putText(stats_background, f"Stats for team {self.config['team_number']}", 
                    (50, 50),
                    **stats_font_settings
                    )
        
        # event duration clock

        # cumulative points

        # leading team

        # distance travelled

        return stats_background
