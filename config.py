import yaml
import logging
import sys
import os
from pathlib import Path
from logging import StreamHandler, Formatter

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
# handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(module)s-%(funcName)s: %(message)s'))
handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(module)s/%(funcName)s: %(message)s'))
logger.addHandler(handler)


class Config:
    def __init__(self):
        self.filename = ""
        self.data = {}
        self.config = None
        self.is_loaded = False
        self.is_changed = False

    def __bool__(self):
        return self.is_loaded

    def get_location(self):
        return self.filename

    def load(self, fn=""):
        if fn != "":
            self.filename = fn

        if self.filename != "":
            logger.debug("Load config file %s", self.filename)
            with open(self.filename) as f:
                self.data = yaml.load(f, Loader=yaml.FullLoader)
                self.is_loaded = True

    def has_value(self, name: str, section: str = "main"):
        if section not in self.data.keys():
            return False
        if not self.data[section] or (name not in self.data[section].keys()):
            return False

        return True

    def set_value(self, name: str, value, section: str = "main"):
        if section not in self.data or self.data[section] is None:
            self.data[section] = {}

        if (name not in self.data[section].keys()) or (self.data[section][name] != value):
            self.data[section][name] = value
            self.is_changed = True

    def get_value(self, name: str, section: str = "main"):
        if self.data is not None and section in self.data:
            if self.data[section] and (name is not None) and (name in self.data[section]):
                return self.data[section][name]
        return None

    def print_config(self):
        print(yaml.dump(self.data))

    def save(self):
        if not self.is_changed:
            logger.debug("Nothing to save. cancel procedure.")
            return

        if self.filename != "":
            if not os.path.isfile(self.filename):
                self.create_config(self.filename)

            try:
                # logger.debug("Save config file %s", self.filename)
                with open(self.filename, 'w') as yaml_file:
                    yaml.dump(self.data, yaml_file, default_flow_style=False)
                    logger.debug("Save config file to %s", self.filename)
                    self.is_changed = False

            except FileNotFoundError as err:
                logger.error("Config Not saved. Error: %s", err)

    def create_config(self, filename):
        self.filename = filename
        p = Path(filename)
        os.makedirs(str(p.parent), exist_ok=True)
        os.system("attrib +h " + str(p.parent))
