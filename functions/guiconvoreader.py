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

    def data_for_total_graph(self, contact=None, cumulative=False, forward_shift=0):
        data = self.msgs_graph(contact, cumulative, forward_shift)

        json = '[\n'
        for day, frequency in data:
            json += '[Date.UTC({0},{1},{2}),{3}],\n'.format(day.year(), day.month() - 1, day.day(), frequency)
        json = json[0:-2]
        json += '\n]'

        return json

    def msgs_graph(self, contact, cumulative, forward_shift):
        val = self._raw_msgs_graph(contact=contact, forward_shift=forward_shift)
        if not cumulative:
            return val
        else:
            for i in range(1, len(val)):
                val[i][1] = val[i - 1][1] + val[i][1]
            return val

