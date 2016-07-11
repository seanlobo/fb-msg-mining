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

    # -----------------------------------------------   PUBLIC METHODS   --------------------------------------------- #
    def data_for_total_graph(self, contact=None, cumulative=False, forward_shift=0):
        data = self.msgs_graph(contact, cumulative, forward_shift)

        json = '[\n'
        for day, frequency in data:
            json += '[Date.UTC({0},{1},{2}),{3}],\n'.format(day.year(), day.month() - 1, day.day(), frequency)
        json = json[0:-2]
        json += '\n]'

        return json

    def data_for_msgs_by_day(self, contact=None):
        """Returns the data for use in html/ javascript"""
        data = self._raw_msgs_by_weekday(contact=contact)
        return str([ele * 100 for ele in data])

    def data_for_msgs_by_time(self, window=60, contact=None):
        data = self._raw_msgs_by_time(window=window, contact=contact)
        return str(data)

    def contains_contact(self, contact):
        if not isinstance(contact, str):
            return False
        contact = ' '.join(contact.split('_')).lower()
        return contact in self._people

    @staticmethod
    def to_contact_string(contact):
        if contact.lower() == 'none':
            return None
        return ' '.join(contact.split('_')).lower()
    # -----------------------------------------------   PUBLIC METHODS   --------------------------------------------- #

    #

    # ----------------------------------------------   INTERNAL METHODS   -------------------------------------------- #

    def msgs_graph(self, contact, cumulative, forward_shift):
        val = self._raw_msgs_graph(contact=contact, forward_shift=forward_shift)
        if not cumulative:
            return val
        else:
            for i in range(1, len(val)):
                val[i][1] = val[i - 1][1] + val[i][1]
            return val

    # ----------------------------------------------   INTERNAL METHODS   -------------------------------------------- #
