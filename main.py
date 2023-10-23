from pathlib import Path
import sys

import easygui

from results_reader import results_reader
from map_reader import map_reader 
from results_plotter import results_plotter
from utils import get_config, get_control_coordinates

ret_val = easygui.msgbox("Welcome to the Rogaining Plotting Tool\nSource: https://github.com/chrisharris000/rogaine-plotter")

while True:
    msg ="Create config (first time user) or Load Config\nPress <cancel> to exit."
    title = "Config selection"
    choices = ["Create Config", "Load Config"]
    choice = easygui.choicebox(msg, title, choices)
    if choice is None:
        sys.exit(0)

    if choice == "Create Config":
        sys.exit(0)

    elif choice == "Load Config":
        msg = "Select the config for results plotter"
        title = "Config selection"
        filetypes = ["*.yml", "*.yaml"]
        file_str = easygui.fileopenbox(msg, title, filetypes=filetypes)
        if file_str is not None:
            file = Path(file_str)
            break

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