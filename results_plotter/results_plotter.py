import datetime
import re
import time

import cv2
import numpy as np
import pandas as pd

from utils import PixelCoordinate

class ResultsPlotter:
    """
    Open map and display teams moving around map and summary stats
    """
    def __init__(self, config: dict,
                 results: "dict[str, pd.Dataframe]",
                 control_coordinates: "dict[str, PixelCoordinate]",
                 leg_statistics: pd.DataFrame):
        self.config = config
        self.results = results
        self.control_coordinates = control_coordinates
        self.leg_statistics = leg_statistics
        self.original_map = cv2.imread(self.config["map_file"])
        self.canvas_map = self.original_map.copy()

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
        scale = (sim_length/3600) / (event_length + 0.5)    # unitless, + 0.5 to account for late arrivals
        fps = 15    # frames per sec
        dt = 1/fps

        while curr_sim_time < sim_length:
            # start with blank canvas for stats
            stats_width, stats_height = 800, 800
            stats_background = np.ones((stats_width, stats_height, 3))
            stats_background = self.add_stats_text(stats_background, curr_event_time)
            self.canvas_map = self.add_teams_location(self.canvas_map, curr_event_time)
            self.canvas_map = self.add_control_locations(self.canvas_map, curr_event_time)

            cv2.imshow(map_window_name, self.canvas_map)
            cv2.imshow(stats_window_name, stats_background)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

            curr_sim_time += dt
            curr_event_time += dt/scale

            # reset canvas map
            self.canvas_map = self.original_map.copy()

            time.sleep(dt)

        cv2.destroyAllWindows()

    def add_stats_text(self, stats_background: np.ndarray, t_event: float) -> np.ndarray:
        """
        Add the text to be display on the stats window, including:
         - the title
         - event elapsed time
         - cumulative points
         - overall leading team
         - distance travelled

        args:
        - stats_background: numpy array representing the area that stats can be written onto
        - t_event: float representing seconds since start of event
        """
        stats_font_settings = {
            "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
            "fontScale": 1,
            "color": (255, 0, 0),
            "thickness": 2,
            "lineType": 2
        }

        # stats page title
        team_number = self.config["team_number"]
        cv2.putText(stats_background, f"Stats for team {team_number}", 
                    (50, 50),
                    **stats_font_settings
                    )
        
        # event duration clock
        t_event_timedelta = datetime.timedelta(seconds=t_event)
        event_elapsed_text = str(t_event_timedelta)
        cv2.putText(stats_background, f"Time since event started: {event_elapsed_text} hrs", 
                    (50, 100),
                    **stats_font_settings
                    )
        
        # distance travelled
        dist_travelled = 0
        # rows for which at a given t_event time into the event, have already passed
        team_result = self.results[team_number]
        controls_reached = team_result[team_result.cumulative_time < t_event_timedelta]
        # get most recent row
        recent_control_row = controls_reached.tail(1)
        if not recent_control_row.empty:
            dist_travelled = recent_control_row.cumulative_distance.values[0]
        else:
            dist_travelled = 0
        dist_travelled_text = f"Straight line distance travelled: {dist_travelled:.2f} km"
        cv2.putText(stats_background, dist_travelled_text,
                    (50, 150),
                    **stats_font_settings
                    )

        # top 3 teams
        sorted_team_points = self._get_leading_team(t_event)
        first_team_number, first_team_points = sorted_team_points[0]
        first_team_text = f"1st place: Team {first_team_number}, {first_team_points} pts"
        cv2.putText(stats_background, first_team_text,
                    (50, 200),
                    **stats_font_settings
                    )
        
        second_team_number, second_team_points = sorted_team_points[1]
        second_team_text = f"2nd place: Team {second_team_number}, {second_team_points} pts"
        cv2.putText(stats_background, second_team_text,
                    (50, 250),
                    **stats_font_settings
                    )
        
        third_team_number, third_team_points = sorted_team_points[2]
        third_team_text = f"3rd place: Team {third_team_number}, {third_team_points} pts"
        cv2.putText(stats_background, third_team_text,
                    (50, 300),
                    **stats_font_settings
                    )
        
        # cumulative points
        overall_position = 0
        cumulative_points = 0
        for position, (sorted_team_number, sorted_points) in enumerate(sorted_team_points):
            if sorted_team_number == team_number:
                overall_position = position + 1
                cumulative_points = sorted_points
        
        position_text = position_to_text(overall_position)
        cumulative_points_text = f"{position_text} place: Team {team_number}, {cumulative_points} pts"
        cv2.putText(stats_background, cumulative_points_text,
                    (50, 350),
                    **stats_font_settings
                    )

        return stats_background
    
    def add_teams_location(self, canvas_map: np.ndarray, t_event: float) -> np.ndarray:
        """
        Add team icons on map

        args:
        - canvas_map: numpy array representing the rogaining map
        - t_event: float representing the seconds elapsed since the start of the event
        """
        t_event_timedelta = datetime.timedelta(seconds=t_event)
        for team, result in self.results.items():
            df = result

            prev_control = ""
            next_control = ""
            controls_reached = df[df.cumulative_time < t_event_timedelta]
            # get most recent row
            recent_control_row = controls_reached.tail(1)

            # get previous control
            if not recent_control_row.empty:
                prev_control_row = recent_control_row
            else:
                prev_control_row = pd.DataFrame(
                    [["HH",  # control
                    0, # cumulative_points
                    datetime.timedelta(seconds=0), # time_split
                    0.0, # distance
                    datetime.timedelta(seconds=0), # cumulative_time
                    0.0]],    # cumulative_distance
                    columns=["control", "cumulative_points", "time_split", "distance", "cumulative_time", "cumulative_distance"])

            prev_control = prev_control_row.control.values[0]

            # get next control index
            prev_control_idx = -1
            if not recent_control_row.empty:
                prev_control_idx = recent_control_row.index.values[0]

            # get next control row
            if prev_control_idx + 1 < len(df):
                next_control_row = df.iloc[[prev_control_idx + 1]]
            else:
                next_control_row = df.iloc[[-1]]

            # get next control
            next_control = next_control_row.control.values[0]
            
            prev_control_px = self.control_coordinates[prev_control]
            next_control_px = self.control_coordinates[next_control]

            t_event_timedelta_np = np.array([t_event_timedelta], dtype="timedelta64[ms]")[0]
            total_time_split_between_controls = next_control_row.time_split.values[0]
            time_start_at_prev_control = prev_control_row.cumulative_time.values[0]
            curr_time_delta_between_controls = t_event_timedelta_np - time_start_at_prev_control
            if total_time_split_between_controls != np.timedelta64(0):
                time_frac = curr_time_delta_between_controls / total_time_split_between_controls
            else:
                time_frac = 0
            interp_pt_px_x = prev_control_px.x + ((next_control_px.x - prev_control_px.x) * time_frac)
            interp_pt_px_y = prev_control_px.y + ((next_control_px.y - prev_control_px.y) * time_frac)
            interpolated_pt_px = PixelCoordinate(int(interp_pt_px_x), int(interp_pt_px_y))

            circle_colour = (0, 0, 0)
            if team == self.config["team_number"]:
                circle_colour = (0, 120, 50)

            cv2.circle(canvas_map, (interpolated_pt_px.x, interpolated_pt_px.y), 20, circle_colour, -1)
            team_font_settings = {
                "text": team,
                "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
                "fontScale": 1,
                "thickness": 2,
            }

            text_size, _ = cv2.getTextSize(**team_font_settings)
            text_origin = (int(interpolated_pt_px.x - text_size[0] / 2), int(interpolated_pt_px.y + text_size[1] / 2))

            cv2.putText(img=canvas_map, org=text_origin, color=(255, 255, 255), **team_font_settings)

        return canvas_map
    
    def _get_leading_team(self, t_event: float) -> dict:
        """
        Return teams ordered by points at time t_event seconds in event

        args
        - t_event: float representing seconds elapsed since start of the event
        """
        team_points = []
        for team_number, result in self.results.items():
            t_event_timedelta = datetime.timedelta(seconds=t_event)
            # rows for which at a given t_event time into the event, have already passed
            elapsed_times_rows = result[result.cumulative_time < t_event_timedelta]
            # get most recent row
            recent_elapsed_row = elapsed_times_rows.tail(1)
            if not recent_elapsed_row.empty:
                points = recent_elapsed_row.cumulative_points.values[0]
            else:
                points = 0
            team_points.append(tuple([team_number, points]))

        sorted_by_points = list(reversed(sorted(team_points, key=lambda tup: tup[1])))
        return sorted_by_points
    
    def add_control_locations(self, canvas_map: np.ndarray, t_event: float) -> np.ndarray:
        """
        Add circles over the control locations
        Circles change colour as controls are visited more often

        args:
        - canvas_map: numpy array representing the rogaining map
        - t_event: float representing the seconds elapsed since the start of the event
        """
        for control, coordinate in self.control_coordinates.items():
            circle_colour = (255, 0, 0)

            cv2.circle(canvas_map, (coordinate.x, coordinate.y), 20, circle_colour, -1)
            team_font_settings = {
                "text": control,
                "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
                "fontScale": 1,
                "thickness": 2,
            }

            text_size, _ = cv2.getTextSize(**team_font_settings)
            text_origin = (int(coordinate.x - text_size[0] / 2), int(coordinate.y + text_size[1] / 2))

            cv2.putText(img=canvas_map, org=text_origin, color=(255, 255, 255), **team_font_settings)
        return canvas_map
    
    def display_leg_stats(self):
        """
        Open window and display legs stats after main replay is complete
        """
        leg_stats_window_name = "Leg Statistics"
        cv2.namedWindow(leg_stats_window_name, cv2.WINDOW_NORMAL)

        leg_stats = self.leg_statistics.set_index("leg")["leg_count"].to_dict()
        for leg, visit_count in leg_stats.items():
            self.canvas_map = self.add_control_locations(self.canvas_map, -1)

            start_control, end_control = leg.split(":")

            start_control_px = self.control_coordinates[start_control]
            end_control_px = self.control_coordinates[end_control]

            cv2.arrowedLine(self.canvas_map,
                            (start_control_px.x, start_control_px.y),
                            (end_control_px.x, end_control_px.y),
                            color=(0, 0, 0),
                            thickness=5)
            
            midpoint = (
                int((start_control_px.x + end_control_px.x) / 2),
                int((start_control_px.y + end_control_px.y) / 2)
            )
            visit_font_settings = {
                "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
                "fontScale": 1.5,
                "color": (255, 255, 0),
                "thickness": 4,
                "lineType": 2
            }
            cv2.putText(self.canvas_map, str(visit_count), midpoint, **visit_font_settings)
            
            time.sleep(1)

            cv2.imshow(leg_stats_window_name, self.canvas_map)

            # reset canvas map
            self.canvas_map = self.original_map.copy()
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
    
def position_to_text(num: int) -> str:
    """
    Convert a given position to its text representation
    e.g.
    1 -> "1st"
    2 -> "2nd"
    3 -> "3rd"
    4 -> "4th"

    Source: https://pypi.org/project/inflect/
    """
    DIGIT = re.compile(r"\d")
    nth = {
        0: "th",
        1: "st",
        2: "nd",
        3: "rd",
        4: "th",
        5: "th",
        6: "th",
        7: "th",
        8: "th",
        9: "th",
        11: "th",
        12: "th",
        13: "th",
    }
    ordinal = dict(
        ty="tieth",
        one="first",
        two="second",
        three="third",
        five="fifth",
        eight="eighth",
        nine="ninth",
        twelve="twelfth",
    )
    ordinal_suff = re.compile(fr"({'|'.join(ordinal)})\Z")

    
    if DIGIT.match(str(num)):
        if isinstance(num, (float, int)) and int(num) == num:
            n = int(num)
        else:
            if "." in str(num):
                try:
                    # numbers after decimal,
                    # so only need last one for ordinal
                    n = int(str(num)[-1])

                except ValueError:  # ends with '.', so need to use whole string
                    n = int(str(num)[:-1])
            else:
                n = int(num)  # type: ignore
        try:
            post = nth[n % 100]
        except KeyError:
            post = nth[n % 10]
        return f"{num}{post}"
    else:
        # Mad props to Damian Conway (?) whose ordinal()
        # algorithm is type-bendy enough to foil MyPy
        str_num: str = num  # type: ignore[assignment]
        mo = ordinal_suff.search(str_num)
        if mo:
            post = ordinal[mo.group(1)]
            rval = ordinal_suff.sub(post, str_num)
        else:
            rval = f"{str_num}th"
        return rval