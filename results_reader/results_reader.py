import math
from pathlib import Path

import pandas as pd

from utils import PixelCoordinate

class ResultsReader:
    """
    Import results of rogaine event from original txt files or from csv generated by this program
    """
    def __init__(self, config: dict, control_coordinates: "dict[str, PixelCoordinate]"):
        self.config = config
        self.control_coordinates = control_coordinates
        self.fields = ["control",
                       "cumulative_points",
                       "time_split",
                       "distance",
                       "cumulative_time",
                       "cumulative_distance"
                       ]

    def parse_txt_results_directory(self) -> "dict[str, pd.Dataframe]":
        """
        Parse the original txt files of results into a dictionary of team_number:team_result
        """
        results = {}

        file_pattern = "*_*.txt"
        for filepath in Path(self.config["results_directory"]).glob(file_pattern):
            filename = filepath.name
            team_number = filename.split("_")[0]
            if team_number not in results:
                result = self._parse_txt_result(filepath)

                # calculate cumulative time
                result["cumulative_time"] = result.time_split.cumsum()
                result["cumulative_time"] = pd.to_timedelta(result["cumulative_time"])

                # calculate cumulative distance
                result["cumulative_distance"] = result.distance.cumsum()

                results[team_number] = result

        return results

    def _parse_txt_result(self, filepath: Path) -> pd.DataFrame:
        """
        Parse an individual txt result file and return a pandas dataframe
        """
        result = pd.DataFrame(columns=self.fields[:4])

        for line_num, line in enumerate(open(filepath)):
            # ignore first 3 lines, only descriptive info about file
            if line_num < 3:
                continue

            # ignore line starting with No and Distance and newline:
            if line.startswith("No") or line.startswith("Distance") or line == "\n":
                continue

            if line.lstrip().startswith("Late Penalty"):
                original_points = result.loc[len(result) - 1, "cumulative_points"]
                deduction = int(line.split()[-1])
                final_total = original_points + deduction
                control, cumulative_points, time_split = "HH", final_total, "00:00:00"

            else:
                # extract relevant fields
                _no, control, _time, _dist, _cm_dist, cumulative_points, time_split, *_other_fields = line.lstrip().split()

            # pad time with zero hours if necessary
            if time_split.count(":") == 1:
                time_split = "00:" + time_split

            # calculate distance travelled
            prev_control = ""
            if len(result) == 0:
                prev_control = "HH"
            else:
                prev_entry = result.loc[len(result) - 1]
                prev_control = prev_entry["control"]

            distance_travelled = self.calculate_distance_between_controls(prev_control, control)

            entry = [control, int(float(cumulative_points)), pd.Timedelta(time_split), distance_travelled]
            result.loc[len(result)] = entry

        return result

    def parse_csv_results_directory(self) -> "dict[str, pd.Dataframe]":
        """
        Parse the results from csv files generated by this class and return a dictionary of
        team_number:result
        """
        results = {}

        file_pattern = "*_result.csv"
        for filepath in Path(self.config["results_directory"]).glob(file_pattern):
            filename = filepath.name
            team_number = filename.split("_")[0]
            if team_number not in results:
                results[team_number] = self._parse_csv_result(filepath)

        return results

    def _parse_csv_result(self, filepath: Path) -> pd.DataFrame:
        """
        Parse an individual csv result and return a pandas dataframe
        """
        result = pd.read_csv(filepath)
        result.time_split = pd.to_timedelta(result.time_split)
        result.cumulative_time = pd.to_timedelta(result.cumulative_time)
        return result

    def write_csv_results(self, results: "dict[str, pd.Dataframe]") -> None:
        """
        Write the results dataframes as csv files
        """
        for team, result in results.items():
            filename = f"{team}_result.csv"
            filepath = Path(self.config["results_directory"]) / filename
            result.to_csv(filepath, index=False)

    def calculate_distance_between_controls(self, prev_control: str, curr_control: str) -> float:
        """
        Calculate the distance in km between the previous control and the current control
        """
        prev_control_coords = self.control_coordinates[prev_control]
        curr_control_coords = self.control_coordinates[curr_control]
        dx = prev_control_coords.x - curr_control_coords.x
        dy = prev_control_coords.y - curr_control_coords.y
        dist_pixels = math.sqrt(dx**2 + dy**2)

        # convert to km
        scale_str = self.config["map_scale_pixels"].split(":")
        ratio = int(scale_str[0]) / int(scale_str[1])
        dist_km = (dist_pixels / ratio) / 1000

        return dist_km

    def parse_control_statistics_txt(self) -> pd.DataFrame:
        """
        Parse a txt file containing the control statistics for the event and return a pandas dataframe
        """
        control_statistics = pd.DataFrame(columns=["control", "visit_count"])
        for line_num, line in enumerate(open(self.config["control_statistics"], "r")):
            if line_num == 0:
                continue

            line = line.split()
            if len(line[0]) == 2:
                entry = [line[0], line[1]]
                control_statistics.loc[len(control_statistics)] = entry
        return control_statistics

    def parse_control_statistics_csv(self) -> pd.DataFrame:
        """
        Parse a csv file containing the control statistics for the event and return a pandas dataframe
        """
        control_statistics = pd.read_csv(self.config["control_statistics"])
        return control_statistics

    def write_control_statistics_csv(self, control_statistics: pd.DataFrame, save_directory: str) -> None:
        """
        Write the control statistics dataframe as a csv file
        """
        filename = f"control-statistics.csv"
        filepath = Path(save_directory) / Path(filename)
        control_statistics.to_csv(filepath, index=False)

    def parse_leg_statistics_txt(self) -> pd.DataFrame:
        """
        Parse a txt file containing the leg statistics for the event and return a pandas dataframe
        """
        leg_statistics = pd.DataFrame(columns=["leg", "leg_count"])
        for line_num, line in enumerate(open(self.config["leg_statistics"], "r")):
            if line_num == 0:
                continue

            line = line.split()
            if len(line[0]) == 5:
                entry = [line[0], line[1]]
                leg_statistics.loc[len(leg_statistics)] = entry
        return leg_statistics

    def parse_leg_statistics_csv(self) -> pd.DataFrame:
        """
        Parse a csv file containing the leg statistics for the event and return a pandas dataframe
        """
        leg_statistics = pd.read_csv(self.config["leg_statistics"])
        return leg_statistics

    def write_leg_statistics_csv(self, leg_statistics: pd.DataFrame, save_directory: str) -> None:
        """
        Write the leg statistics dataframe as a csv file
        """
        filename = f"leg-statistics.csv"
        filepath = Path(save_directory) / Path(filename)
        leg_statistics.to_csv(filepath, index=False)
