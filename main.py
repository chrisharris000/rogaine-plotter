from user_interface import user_interface

ui = user_interface.UserGui()
# ui.show_homepage()
response = ui.show_config_prompt()

if response == "Create Config":
    ui.show_create_config_option()

elif response == "Load Config":
    ui.show_load_config_option()

ui.replay_event()

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
