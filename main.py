from user_interface import user_interface

ui = user_interface.UserGui()
ui.show_homepage()
response = ui.show_config_prompt()

if response == "Create Config":
    ui.show_create_config_option()
    ui.save_config()

elif response == "Load Config":
    ui.show_load_config_option()

ui.replay_event()
# ui.display_leg_stats()
