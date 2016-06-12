from collections import Counter
from math import ceil
import re
import os


from functions.baseconvoreader import BaseConvoReader
from functions.customdate import CustomDate
import functions.emojis as emojis


class GUIConvoReader(BaseConvoReader):
    def __init__(self, convo_name, convo_list):
        BaseConvoReader.__init__(self, convo_name, convo_list)

    def data_for_total_graph(self):
        data = self._raw_msgs_graph()

        json = '[\n'
        for day, frequency in data:
            json += '[Date.UTC({0},{1},{2}),{3}],\n'.format(day.year(), day.month() - 1, day.day(), frequency)
        json = json[0:-2]
        json += '\n]'

        return json
