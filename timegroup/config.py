import sys
import os
from pathlib import Path
import yaml


def load_config(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).resolve().parent

config_path = os.path.join(base_path, "config.yaml")
config = load_config(config_path)
