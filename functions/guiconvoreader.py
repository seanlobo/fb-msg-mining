import json
import os
import subprocess


from functions.customdate import CustomDate
from functions.baseconvoreader import BaseConvoReader
from functions.wordcloud import WordCloud


class GUIConvoReader(BaseConvoReader):
    def __init__(self, convo_name, convo_list, download_date, emojify=False):
        BaseConvoReader.__init__(self, convo_name, convo_list, 'gui', emojify=emojify)  # default value of gui for rank
        self._last_day = download_date

        self.people_by_messages = sorted(self.get_people(), key=lambda x: self.raw_messages(x), reverse=True)

    # -----------------------------------------------   PUBLIC METHODS   --------------------------------------------- #
    def data_for_total_graph(self, contact=None, cumulative=False, forward_shift=0):
        """Returns a json string representation of this conversation's total message data"""
        raw_data = self.msgs_graph(contact, cumulative, forward_shift)
        data = []
        for day, frequency in raw_data:
            data.append('[Date.UTC({0},{1},{2}),{3}]'.format(day.year(), day.month() - 1, day.day(), frequency))
        return json.dumps(dict(data=data))

    def data_for_msgs_by_day(self, contact=None):
        """Returns the data for use in html/ javascript"""
        raw_data = self.raw_msgs_by_weekday(contact=contact)
        raw_data = [ele * 100 for ele in raw_data]

        data = [dict(name=CustomDate.WEEK_INDEXES_TO_DAY_OF_WEEK[i], y=ele) for i, ele in enumerate(raw_data)]
        return json.dumps(dict(data=data))

    def data_for_msgs_by_time(self, window=60, contact=None):
        raw_data = self.raw_msgs_by_time(window=window, contact=contact)

        categories = []
        for i in range(len(raw_data)):
            categories.append(raw_data[i][0] + "-" + raw_data[(i + 1) % len(raw_data)][0])
        data = [freq for _, freq in raw_data]
        if contact is None:
            contact = "Aggregate"
        else:
            contact = contact.title()
        final_data = [dict(name=contact, data=data)]

        return json.dumps(dict(categories=categories, data=final_data))

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

    @staticmethod
    def data_for_all_messages(raw_data):
        data = []
        for day, frequency in raw_data:
            data.append('[Date.UTC({0},{1},{2}),{3}]'.format(day.year(), day.month() - 1, day.day(), frequency))

        return json.dumps(dict(data=data))

    def person_rank(self, person) -> int:
        """Returns the order person is in chat frequency for this chat, with 1 being the most frequent poster and
        len(self) being the least
        Parameters:
            person: A string representing the person desired
        Return:
            An Integer, The rank of this person in the conversation by number of messages sent, with 1 being the most
            messages sent and len(self) being the last
        """
        assert isinstance(person, str), "person must be a string"
        person = self._assert_contact(person)[0]
        for i, p in enumerate(self.people_by_messages):
            if p == person:
                return i + 1

    def setup_new_word_cloud(self, preferences):
        """Cleans up data from html form to work with kumo"""
        for key in WordCloud.integer_fields():
            if key in preferences and isinstance(preferences[key], str):
                try:
                    preferences[key] = int(preferences[key])
                except ValueError:
                    pass

        if 'excluded_words' in preferences and isinstance(preferences['excluded_words'], str):
            if preferences['excluded_words'] == 'None':
                preferences['excluded_words'] = []
            else:
                preferences['excluded_words'] = [preferences['excluded_words']]

        num_colors = preferences.get('num_colors')
        if num_colors is not None:
            colors = []
            for i in range(1, num_colors + 1):
                colors.append(list(WordCloud.hex_to_rgb(preferences['color{}'.format(str(i))])))
            preferences['colors'] = colors
        else:
            preferences['colors'] = WordCloud.DEFAULT_COLORS

        if 'output_name' in preferences and preferences['output_name'] == 'current_time.png':
            preferences['output_name'] = WordCloud.DEFAULT_OUTPUT_NAME

        if 'shape' in preferences and preferences['shape'] != 'image':
            preferences['image_name'] = 'None'

        return BaseConvoReader.setup_new_word_cloud(self, preferences)

    def ready_for_word_cloud(self):
        return self._word_cloud.ready()

    def create_word_cloud(self):
        """Calls the java kumo program, assuming that all conditions are met"""
        assert isinstance(self._word_cloud, WordCloud) and self._word_cloud.ready(), (
            "Word cloud preferences have either not been set or have unfixed issues. "
            "Run setup_new_word_cloud to continue"
        )
        # grabbed from http://stackoverflow.com/questions/438594/how-to-call-java-objects-and-functions-from-cpython
        # with additions by http://stackoverflow.com/questions/11269575/how-to-hide-output-of-subprocess-in-python-2-7k
        # devnull = open(os.devnull, mode='w')
        p = subprocess.Popen("java -jar data/word_clouds/wordclouds.jar", shell=True)
        sts = os.waitpid(p.pid, 0)

    # -----------------------------------------------   PUBLIC METHODS   --------------------------------------------- #

    #

    # ----------------------------------------------   INTERNAL METHODS   -------------------------------------------- #

    def msgs_graph(self, contact, cumulative, forward_shift):
        val = self.raw_msgs_graph(contact=contact, forward_shift=forward_shift)
        while val[-1][0].date != self._last_day.date:
            val.append([val[-1][0].plus_x_days(1), 0])
        if not cumulative:
            return val
        else:
            for i in range(1, len(val)):
                val[i][1] = val[i - 1][1] + val[i][1]
            return val

    # ----------------------------------------------   INTERNAL METHODS   -------------------------------------------- #
