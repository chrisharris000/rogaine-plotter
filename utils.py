from typing import TypedDict
import yaml

import pandas as pd

CONFIG = {}

class TeamResult(TypedDict):
    team_number: int
    result: pd.DataFrame

# read config
with open("config.yml", "r") as config_fp:
    CONFIG = yaml.safe_load(config_fp)
