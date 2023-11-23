import sys

import easygui
import yaml

from map_reader import map_reader

class UserGui:
    """
    Main user GUI
    """
    def __init__(self):
        self.config = {}
        self.config_save_dir = ""

    def show_homepage(self):
        """
        Initial screen users see when starting the program
        """
        easygui.msgbox("Welcome to the Rogaining Plotting Tool\nSource: https://github.com/chrisharris000/rogaine-plotter")

    def show_config_prompt(self) -> str:
        """
        Prompt user to either create a new config or load an existing config
        Returns either "Create Config" or "Load Config"
        """
        msg = "Create config (first time user) or Load Config\nPress <cancel> to exit."
        title = "Config selection"
        choices = ["Create Config", "Load Config"]
        choice = easygui.choicebox(msg, title, choices)
        if choice is None:  # user selected <cancel>, exiting program
            sys.exit(0)

        return choice
    
    def show_load_config_option(self):
        """
        Menu for when user elects to load existing config
        Loads the selected config and returns it as a dictionary
        """
        msg = "Select the config for results plotter"
        title = "Config selection"
        filetypes = ["*.yml", "*.yaml"]
        config_path = easygui.fileopenbox(msg, title, filetypes=filetypes)
        with open(config_path, "r") as config_fp:
            self.config = yaml.safe_load(config_fp)
    
    def show_create_config_option(self):
        """
        Menu for when user elects to create a new config
        Prompt user to enter:
        - team number and event length
        - path to directory containing results txt files
        - path to map
        - path to leg statistics txt file
        - path to control statistics txt file
        - path to directory to save control coordinates csv
        - path to save config file
        """
        # get team number and event length
        self._get_text_input()

        # get path to results directory
        self._get_results_directory()

        # get path to map
        self._get_map_path()

        # get path to control coordinates save directory
        self._get_control_coords_save_dir()

        # get path to leg statistics 
        self._get_leg_stats()

        # get path to control statistics 
        self._get_control_stats()

        # get path to save config
        self._get_config_save_location()

        # prompt user to identify control coordinates
        self._load_control_coordinates_identification()

        # prompt user to measure map scale
        self._load_user_map_scale_measure()

    def _get_text_input(self):
        """
        Get text input (team number and event length) for create config option
        """
        msg = "Enter Basic Event Details"
        title = "Event Details"
        field_names = ["Team Number", "Event Length (hrs)"]
        field_values = easygui.multenterbox(msg, title, field_names)
        if field_values is None:
            return {}

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

        self.config["team_number"] = team_number
        self.config["event_length"] = event_length

    def _get_results_directory(self) -> str:
        """
        Get path to results directory from user
        """
        msg = "Select the directory containing the results"
        title = "Results directory selection"
        results_dir = easygui.diropenbox(msg, title)
        self.config["results_directory"] = results_dir
    
    def _get_map_path(self):
        """
        Get path to map
        """
        msg = "Select the map"
        title = "Map selection"
        filetypes = ["*.png"]
        map_file = easygui.fileopenbox(msg, title, filetypes=filetypes)
        self.config["map_file"] = map_file

    def _get_control_coords_save_dir(self):
        """
        Get path to directory to save control coordinates
        """
        msg = "Select the directory to save the control coordinates to"
        title = "Control coordinates save directory selection"
        control_coords_dir = easygui.diropenbox(msg, title)
        self.config["control_coordinates"] = f"{control_coords_dir}/control-coordinates.csv"

    def _get_leg_stats(self):
        """
        Get path to leg statistics
        """
        msg = "Select the leg statistics file"
        title = "Leg statistics selection"
        filetypes = ["*.txt"]
        leg_stats_file = easygui.fileopenbox(msg, title, filetypes=filetypes)
        self.config["leg_statistics"] = leg_stats_file

    def _get_control_stats(self):
        """
        Get path to control statistics
        """
        msg = "Select the control statistics file"
        title = "Control statistics selection"
        filetypes = ["*.txt"]
        control_stats_file = easygui.fileopenbox(msg, title, filetypes=filetypes)
        self.config["control_statistics"] = control_stats_file
    
    def _get_config_save_location(self):
        """
        Get path to save location of config
        """
        msg = "Select the directory to save the config to"
        title = "Config save directory selection"
        config_save_dir = easygui.diropenbox(msg, title)
        self.config_save_dir = config_save_dir

    def _load_control_coordinates_identification(self):
        """
        Prompt user to identify control coordinates
        """
        coord_rdr = map_reader.ControlCoordinatesReader(self.config)
        coord_rdr.open_map()
        coord_rdr.write_coordinates()

    def _load_user_map_scale_measure(self):
        """
        Prompt user to measure map scale
        """
        scale_rdr = map_reader.ScaleReader(self.config)
        scale_rdr.open_map()
        pixels_to_km = scale_rdr.get_km_pixel_length()
        self.config["map_scale_pixels"] = f"{pixels_to_km}:1000"

    def save_config(self):
        """
        Save a config generated by the user through the Create Config option
        """
        config_save_file = f"{self.config_save_dir}/config.yml"
        with open(config_save_file, "w") as config_fp:
            yaml.dump(self.config, config_fp)
