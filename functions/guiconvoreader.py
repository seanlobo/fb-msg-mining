import json


from functions.customdate import CustomDate
from functions.baseconvoreader import BaseConvoReader


class GUIConvoReader(BaseConvoReader):
    def __init__(self, convo_name, convo_list, download_date):
        BaseConvoReader.__init__(self, convo_name, convo_list)
        self._last_day = download_date

    # -----------------------------------------------   PUBLIC METHODS   --------------------------------------------- #
    def data_for_total_graph(self, contact=None, cumulative=False, forward_shift=0):
        raw_data = self.msgs_graph(contact, cumulative, forward_shift)

        data = []
        for day, frequency in raw_data:
            data.append('[Date.UTC({0},{1},{2}),{3}]'.format(day.year(), day.month() - 1, day.day(), frequency))

        return json.dumps(dict(data=data))

    def data_for_msgs_by_day(self, contact=None):
        """Returns the data for use in html/ javascript"""
        raw_data = self._raw_msgs_by_weekday(contact=contact)
        raw_data = [ele * 100 for ele in raw_data]

        data = [dict(name=CustomDate.WEEK_INDEXES_TO_DAY_OF_WEEK[i], y=ele) for i, ele in enumerate(raw_data)]
        return json.dumps(dict(data=data))

    def data_for_msgs_by_time(self, window=60, contact=None):
        data = self._raw_msgs_by_time(window=window, contact=contact)
        return json.dumps(dict(data=data))

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
        while val[-1][0].date != self._last_day.date:
            val.append([val[-1][0].plus_x_days(1), 0])
        if not cumulative:
            return val
        else:
            for i in range(1, len(val)):
                val[i][1] = val[i - 1][1] + val[i][1]
            return val

    # ----------------------------------------------   INTERNAL METHODS   -------------------------------------------- #
