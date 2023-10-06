import sys
import getopt
import os
import io
import logging
import time
import traceback
from logging import StreamHandler, Formatter
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from SMH_AppWindow import AppWindow
from config import Config

basedir = os.path.dirname(__file__)

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = StreamHandler(stream=sys.stderr)
handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(module)s-%(funcName)s: %(message)s'))
logger.addHandler(handler)

HOME = os.getenv('HOME')
PROGNAME = "smhcanusb"
CONF_FNAME = PROGNAME + ".conf"


def find_config_file():
    config_path_list = [
        os.path.join(HOME, "." + PROGNAME, CONF_FNAME),
    ]
    argv = sys.argv[1:]
    options, args = getopt.getopt(argv, "c:i:", ["config =", "input ="])

    for name, value in options:
        if name in ['-c', '--conf']:
            config_path_list.insert(0, value)

    for fpath in config_path_list:
        logger.debug("Check config file path %s", fpath)
        if os.path.isfile(fpath):
            return fpath

    return ""


if __name__ == '__main__':

    config = Config()
    fpath = find_config_file()
    if fpath:
        config.load(fpath)
    else:
        config.create_config(os.path.join(HOME, "." + PROGNAME, CONF_FNAME))

    win_width = 1000 if not config or not config.has_value("width", "window") else config.get_value("width", "window")
    win_height = 600 if not config or not config.has_value("height", "window") else config.get_value("height", "window")
    x = 300 if not config or not config.has_value("x", "window") else config.get_value("x", "window")
    y = 150 if not config or not config.has_value("y", "window") else config.get_value("y", "window")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "main1.png")))
    window = AppWindow()
    window.resize(win_width, win_height)
    # logger.debug("Window position x=%s, y=%s", x, y)
    window.move(x, y)
    # window.config = config

    # if config and config.has_value(AppWindow.LAST_PROTO_FILE):
    #     logger.debug("load config file %s", config.get_value(AppWindow.LAST_PROTO_FILE))
    #     window.fRule_filename = config.get_value(AppWindow.LAST_PROTO_FILE)
    #     window.FTree.load_json_file(window.fRule_filename)
    #
    # if config and config.has_value(AppWindow.LAST_FRULE_FILE):
    #     logger.debug("load config file %s", config.get_value(AppWindow.LAST_FRULE_FILE) )
    #     window.fRule_filename = config.get_value(AppWindow.LAST_FRULE_FILE)
    #     window.FTree.load_json_file(window.fRule_filename)


    window.setup(config)


    # window.set_loader(ElLoader())  # Attach loader
    # window.config = config
    # window.tree_display()   # Generate and display main tree
    # if config and config.has_value(LAST_OPEN_FILE):
    #     window.load_data(config.get_value(LAST_OPEN_FILE))
    #     window.set_events()
    #
    # config.filename = os.path.join(HOME, "." + prog_name, conf_name)

    app.exec_()


