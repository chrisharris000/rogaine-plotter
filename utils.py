import csv
from dataclasses import dataclass

import pandas as pd
import yaml

@dataclass
class PixelCoordinate:
    """
    x: x location pixel, 0 being left edge of pdf, positive rightwards
    y: y location of pixel, 0 being top edge of pdf, positive downwards
    """
    x: int
    y: int

def get_config():
    with open("config.yml", "r") as config_fp:
        return yaml.safe_load(config_fp)

def get_control_coordinates():
    control_coordinates = {}
    config = get_config()
    with open(config["control_coordinates"]) as control_fp:
        csvreader = csv.reader(control_fp)
        _fields = next(csvreader)

        for row in csvreader:
            control_id, pixel_x, pixel_y = row
            control_coordinates[control_id] = PixelCoordinate(int(pixel_x), int(pixel_y))

    return control_coordinates