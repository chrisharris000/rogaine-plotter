from pathlib import Path
import sys

import easygui

from results_reader import results_reader
from map_reader import map_reader 
from results_plotter import results_plotter
from utils import get_config, get_control_coordinates

def create_or_load_config() -> str:
    """
    Prompt user to either create a new config or load an existing config
    """
    msg ="Create config (first time user) or Load Config\nPress <cancel> to exit."
    title = "Config selection"
    choices = ["Create Config", "Load Config"]
    choice = easygui.choicebox(msg, title, choices)
    if choice is None:  # user selected <cancel>, exiting program
        sys.exit(0)

    return choice

def create_config_option() -> dict:
    """
    Menu for when user elects to create a new config
    """
    config_values = {}

    msg = "Enter Basic Event Details"
    title = "Event Details"
    field_names = ["Team Number", "Event Length (hrs)"]
    field_values = easygui.multenterbox(msg, title, field_names)
    if field_values is None:
        return {}   # user selected <cancel>, returning to Create/Load Config screen

    # make sure that none of the fields were left blank
    while True:
        errmsg = ""
        for i, name in enumerate(field_names):
            if field_values[i].strip() == "":
                errmsg += "{} is a required field.\n\n".format(name)
        if errmsg == "":
            break   # all fields were filled in
        field_values = easygui.multenterbox(errmsg, title, field_names, field_values)
        if field_values is None:
            return {}   # user selected <cancel>
    team_number, event_length = field_values
    config_values["team_number"] = team_number
    config_values["event_length"] = event_length

    # get path to results directory
    msg = "Select the directory containing the results"
    title = "Results directory selection"
    dir_str = easygui.diropenbox(msg, title)
    if dir_str is not None:
        results_directory = Path(dir_str)
        config_values["results_directory"] = results_directory

    # get path to map
    msg = "Select the map"
    title = "Map selection"
    filetypes = ["*.png"]
    map_file_str = easygui.fileopenbox(msg, title, filetypes=filetypes)
    if map_file_str is not None:
        map_file = Path(map_file_str)
        config_values["map_file"] = map_file

    # get path to leg statistics 
    msg = "Select the leg statistics file"
    title = "Leg statistics selection"
    filetypes = ["*.txt"]
    leg_stats_str = easygui.fileopenbox(msg, title, filetypes=filetypes)
    if leg_stats_str is not None:
        leg_stats_file = Path(leg_stats_str)
        config_values["leg_statistics"] = leg_stats_file

    # get path to control statistics 
    msg = "Select the control statistics file"
    title = "Contorl statistics selection"
    filetypes = ["*.txt"]
    leg_stats_str = easygui.fileopenbox(msg, title, filetypes=filetypes)
    if leg_stats_str is not None:
        leg_stats_file = Path(leg_stats_str)
        config_values["control_statistics"] = leg_stats_file

    return config_values   # user successfully completed Create Config process

def load_config_option() -> Path:
    """
    Menu for when user elects to load existing config
    """
    msg = "Select the config for results plotter"
    title = "Config selection"
    filetypes = ["*.yml", "*.yaml"]
    file_str = easygui.fileopenbox(msg, title, filetypes=filetypes)
    if file_str is not None:
        file = Path(file_str)
        return file   # user successfully completed Load Config process

def main():
    easygui.msgbox("Welcome to the Rogaining Plotting Tool\nSource: https://github.com/chrisharris000/rogaine-plotter")

    # if user loads config
    file = ""

    # if user creates config
    config_values = {}

    choice = create_or_load_config()

    if choice == "Create Config":
        config_values = create_config_option()

    elif choice == "Load Config":
        file = load_config_option()

    print(f"{file=}")
    print(f"{config_values=}")

main()

# config = get_config()
# control_coords = get_control_coordinates()

# # read from txt
# res_rdr = results_reader.ResultsReader(config, control_coords)
# leg_stats = res_rdr.parse_leg_statistics_csv()

# # results = res_rdr.parse_txt_results_directory()

# # # write to csv
# # res_rdr.write_csv_results(results)

# # # read from csv
# # results = res_rdr.parse_csv_results_directory()

# # plot results
# results = results_reader.ResultsReader(config, control_coords).parse_csv_results_directory()
# pltr = results_plotter.ResultsPlotter(config, results, control_coords, leg_stats)
# pltr.plot_results()