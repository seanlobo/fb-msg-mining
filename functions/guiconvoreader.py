from collections import Counter
from math import ceil
import re
import os


from functions.baseconvoreader import BaseConvoReader
from functions.customdate import CustomDate
import functions.emojis as emojis


class GUIConvoReader(BaseConvoReader):
    def __init__(self, convo_name, convo_list):
        BaseConvoReader.__init__(convo_name, convo_list)
