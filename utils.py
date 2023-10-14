import csv
from dataclasses import dataclass

import pandas as pd
import yaml

CONFIG = {}
CONTROL_COORDINATES = {}

@dataclass
class PixelCoordinate:
    """
    x: x location pixel, 0 being left edge of pdf, positive rightwards
    y: y location of pixel, 0 being top edge of pdf, positive downwards
    """
    x: int
    y: int

# read config
with open("config.yml", "r") as config_fp:
    CONFIG = yaml.safe_load(config_fp)

# read control coordinates
with open(CONFIG["control_coordinates"]) as control_fp:
    csvreader = csv.reader(control_fp)
    _fields = next(csvreader)

    for row in csvreader:
        control_id, pixel_x, pixel_y = row
        CONTROL_COORDINATES[control_id] = PixelCoordinate(int(pixel_x), int(pixel_y))