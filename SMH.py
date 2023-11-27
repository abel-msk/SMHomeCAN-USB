# SMH.py

"""This module defines project-level constants."""

CAN_FR_BASE = 1
CAN_FR_EXT = 2
ACTION_WAIT = 1
ACTION_SEND = 2
ACT_TEXT_WAIT = "W"
ACT_TEXT_SEND = "S"

# FR_ID_TYPE_EXT = "ext"
# FR_ID_TYPE_BASE = "base"
# FR_TYPE_DATA = "data"
# FR_TYPE_REMOTE = "remote"

# FR_TYPE_ERR = "is_err"
# FR_TYPE_DATA = "is_data"

# FR_TYPE_EXT = "frame_type"  # FR_TYPE_DATA or FR_TYPE_REMOTE
FR_ID_EXT = "is_id_ext"  # FR_ID_TYPE_BASE or FR_ID_TYPE_EXT
FR_DATA = "is_data"
FR_ID = "id"
FR_DATA_LEN = "data_len"
FR_DATA_AR = "data"
FR_ERROR = "is_err"

FL_NAME = "name"
FL_DESCR = "descr"
FL_ID = "rule_id"
FL_MASK_EMPTY = "mask_empty"
FL_PARENT_ID = "parent_rule_id"
FL_FILTER_FR = "filter"
FL_MASK_FR = "mask"
FL_ACTION = "action"
FL_TIMEOUT = "timeout"
FL_USE_DATA = "use_data"
FL_SORT_ORDER = "sort_order"

BG_COLOR_MATCH = "#fffacc"
COLOR_MATCH = "#FFFFFF"
BG_COLOR_NORMAL = "#FFFFFF"


ST_COLOR_FILTERED_FG = 'filter_fg_color'
ST_COLOR_FILTERED_BG = 'filter_bg_color'
ST_COLOR_SEND_FG = 'send_fg_color'
ST_COLOR_SEND_BG = 'send_bg_color'
ST_COLOR_RCV_FG = 'rcv_fg_color'
ST_COLOR_RCV_BG = 'rcv_bg_color'
ST_FONT_CAPT = "capture_font"
ST_FONT_CAPT_SIZE = "capture_font_size"

