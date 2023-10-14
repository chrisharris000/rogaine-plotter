import yaml

CONFIG = {}

# read config
with open("config.yml", "r") as config_fp:
    CONFIG = yaml.safe_load(config_fp)
