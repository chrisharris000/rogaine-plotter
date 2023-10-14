from typing import TypedDict
import yaml

import pandas as pd

CONFIG = {}

class TeamResult(TypedDict):
    """
    key: team_number is the unique ID of the team
    value: result is a dataframe with the following columns
        idx - unique index of indicating order in which controls were visited, int
        control - number of the control visited, int
        cumulative_points, total points after arriving at the control, int
        time_split, time taken to travel from the previous control to the current control, Timedelta
        distance_travelled, straight-line distance travelled between previous and current control, float
    """
    team_number: int
    result: pd.DataFrame

# read config
with open("config.yml", "r") as config_fp:
    CONFIG = yaml.safe_load(config_fp)
