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

        curr_sim_time = 0.0 # secs
        sim_length = self.config["replay_length"]*60 # secs
        curr_event_time = 0.0   # hrs
        event_length = self.config["event_length"]  # hours
        scale = (sim_length/3600) / (event_length)    # unitless, + 0.5 to account for late arrivals
        fps = 15    # frames per sec
        dt = 1/fps

        while curr_sim_time < sim_length:
            # start with blank canvas for stats
            stats_width, stats_height = 750, 750
            stats_background = np.ones((stats_width, stats_height, 3))
            stats_background = self.add_stats_text(stats_background)

            cv2.imshow(map_window_name, self.map)
            cv2.imshow(stats_window_name, stats_background)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

            curr_sim_time += dt
            curr_event_time += dt/scale

            time.sleep(dt)

        cv2.destroyAllWindows()

    def add_stats_text(self, stats_background: np.ndarray) -> np.ndarray:
        """
        Add the text to be display on the stats window, including:
         - the title
         - event elapsed time
         - cumulative points
         - overall leading team
         - distance travelled

        args:
        - stats_background: numpy array representing the area that stats can be written onto
        """
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
        cv2.putText(stats_background, f"Local time {time.ctime(time.time())}", 
                    (50, 150),
                    **stats_font_settings
                    )

        # cumulative points

        # leading team

        # distance travelled

        return stats_background
    
    def add_teams_location(self, map: np.ndarray, t: float) -> np.ndarray:
        """
        Add team icons on map

        args:
        - map: numpy array representing the rogaining map
        - t: float representing the time elapsed since the start of the simulation run
        """
        pass
