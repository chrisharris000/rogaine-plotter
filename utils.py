from dataclasses import dataclass

import pandas as pd
import yaml

CONFIG = {}

@dataclass
class TeamResult:
    """
    team_number: the unique ID of the team
    result: a dataframe with the following columns
        control - number/name of the control visited, str
        cumulative_points, total points after arriving at the control, int
        time_split, time taken to travel from the previous control to the current control, Timedelta
        distance_travelled, straight-line distance travelled between previous and current control, float
    """
    team_number: int
    result: pd.DataFrame

# read config
with open("config.yml", "r") as config_fp:
    CONFIG = yaml.safe_load(config_fp)
