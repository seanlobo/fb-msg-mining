from collections import Counter
from math import ceil
import re
import os


from functions.customdate import CustomDate
import functions.emojis as emojis
from functions.wordcloud import WordCloud


class BaseConvoReader:
    """Provides base analysis of conversations, extended by ConvoReader and GUIConvoReader classes"""

    BASE_PATH = 'data/conversation_data/'

    def __init__(self, convo_name, convo_list, rank, emojify=True):
        """Parameters:
            convo_name: A string for the conversation name, found in your facebook archive
            convo)list: A 2D list with inner lists of the format [person_name (str), message (str), date-time (str)]
            emojify: A boolean, whether to convert python src encodings for emoji in message to unicode
            """
        self._name = convo_name.lower()
        if emojify:
            self._convo = [[name.lower(), emojis.emojify(msg), CustomDate(date)] for name, msg, date in convo_list]
        else:
            self._convo = [[name.lower(), msg, CustomDate(date)] for name, msg, date in convo_list]
        self._people = self.get_people()
        self._kicked_or_left = [person for person in self._people if person not in self._name.split(', ')]
        self._individual_words = self._cleaned_word_freqs()
        self._len = len(self._convo)
        self._path = BaseConvoReader.BASE_PATH + str(rank) + '/'
        self._word_cloud = None

    # -----------------------------------------------   PUBLIC METHODS ---------------------------------------------- #

    def get_people(self) -> list:
        """Returns a list of lower case names for the individuals in this conversation. Does not include DUPLICATE #X
        if the conversation name includes that.
        """
        if hasattr(self, '_people'):
            return self._people

        duplicate = re.compile("duplicate #\d+", re.IGNORECASE)
        people = []
        for person in sorted(self._name.split(', ')):
            if duplicate.fullmatch(person) is None:
                people.append(person)
        for person, msg, date in self._convo:
            if person.lower() not in people:
                people.append(person.lower())
        return sorted(people)

    def save_word_freq(self, path=None):
        """Saves to a file the ordered rankings of word frequencies by person and aggregate for the chat
        Parameters:
            path (optional): a string path representing the relative path to save files at
        """
        path = self._path if path is None else path
        os.makedirs(path[0:-1], exist_ok=True)
        for person, counter in self._individual_words.items():
            split = person.split()
            pers = ''
            for i in range(len(split) - 1):
                pers += split[i]
                pers += '-'
            pers += split[-1]
            with open(path + pers + '_word_freq.txt', mode='w', encoding='utf-8') as f:
                lst = []
                for key, val in counter.items():
                    lst.append((key, val))
                for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
                    f.write("{0}: {1}".format(key, val) + "\n")
        count = Counter()
        for key, val in self._individual_words.items():
            count += val
        with open(path + 'total.txt', mode='w', encoding='utf-8') as f:
            for key, val in count.most_common():
                f.write("{0}: {1}".format(key, val) + "\n")

    def raw_characters(self, person=None) -> Counter:
        """Returns character frequencies in a Counter object
        Parameters:
            person (optional): The name of the person as a string whose character data you would like. Defaults to None,
                               or data for the aggregate conversation
        Return:
            Counter
        """
        if person is not None:
            assert type(person) is str, "Optional parameter person must be a string"
            person = person.lower()
            assert person in self._people, "{0} isn't in this conversation; this conversation is for" \
                                           " {1}".format(person, str(self._people))
        res = Counter()
        for pers, msg, date in self._convo:
            if person is None or pers == person:
                res.update(msg)
        return res

    def raw_emojis(self, person=None) -> Counter:
        """Returns emoji frequency for the conversation in a Counter object
        Parameter:
            person (optional): the name of the person whose emoji frequencies you would like. If left to default
                None, an aggregate total for the conversation is returned
        Return:
            Counter
        """
        chars = self.raw_characters(person=person)
        res = Counter()
        for key, val in chars.most_common():
            if '\\U000' in repr(key) and key is not None:
                try:
                    temp_emoji = emojis.src_to_emoiji(key)
                    if temp_emoji in res:
                        res[temp_emoji] += val
                    else:
                        res[temp_emoji] = val
                except KeyError:
                    res[key] = val
            else:
                for unicode_emoji in emojis.UNICODE_EMOJI:
                    if unicode_emoji == key:
                        if key in res:
                            res[key] += val
                        else:
                            res[key] = val
        return res

    def raw_messages(self, name=None):
        """Returns information about the number of messages in the chat. Return type depends on parameters passed
        Parameters:
            name (optional): The name (as a string) of the person you are interested in. Defaults to None
        Return:
            If name is left to default a Counter object with names of people as keys and the number of messages as
            values. Otherwise an integer representing the number of messages for the person passed
        """
        if name is None:
            return self.__msgs_per_person()
        else:
            return self.__msgs_spoken(name)

    def raw_words(self, name=None):
        """Returns information about the number of words in the chat. Return type depends on parameters passed
        Parameters:
            name (optional): The name (as a string) of the person you are interested in. Defaults to None
        Return:
             If name is left to default a Counter object with names of people as keys and the number of words as values.
             Otherwise an integer representing the number of messages for the person passed
        """

        if name is None:
            return self.__words_per_person()
        else:
            return self.__words_spoken(name)

    def raw_ave_words(self, name=None):
        """Average number of words for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in. Defautls to None
        Return:
            If name is left to default a Counter object with names of people as keys and the average words/message as
            values. Otherwise a float representing the average number of words/ message for the person passed.
        """

        if name is None:
            return self.__ave_words_per_person()
        else:
            return self.__ave_words(name)

    def raw_msgs_graph(self, contact=None, forward_shift=0):
        """The raw data used by print_msgs_graph to display message graphs
        Parameters:
            contact (optional): the name (as a string) of the person you are interested in
                (default: all contacts)
            forward_shift (optional): The number of minutes past 12 midnight that should count as the previous day
        Return:
            A 2D list with inner lists being of the form [ CustomDate(), num-messages]. The CustomDate object represents
            12:00am of a date, and num-messages is the integer number of messages sent and/ or received that day.
        """
        contact = self._assert_contact(contact)
        assert isinstance(forward_shift, int), "Forward shift must be an integer"
        assert -60 * 24 < forward_shift < 60 * 24, "Forward shift must be between {0} and {1}, not including them" \
            .format(-60 * 24, 60 * 24)

        if contact is not None:
            filt = lambda x: x in contact
        else:
            filt = lambda x: True

        start = self._convo[0][2]
        end = self._convo[-1][2]
        days = end - start

        msg_freq = [[None, 0] for i in range(days + 1)]
        for person, msg, date in self._convo:
            if filt(person.lower()):
                if date.minutes() < forward_shift:  # if we are counting this time as the previous day
                    msg_freq[max(0, date - start - 1)][1] += 1
                else:  # this time is ahead of the shift, so it is counted as the right day
                    msg_freq[date - start][1] += 1

        for day in range(len(msg_freq)):
            msg_freq[day][0] = CustomDate.from_date(start + day)

        return msg_freq

    def raw_msgs_by_weekday(self, contact=None):
        """Returns a list containing frequency of chatting by days
        of week, ordered by index, with 0 being Monday, 1 Tuesday.. and 6 Sunday
        """
        contact = self._assert_contact(contact)

        if contact is None:
            key = lambda x: True
        else:
            key = lambda x: x in contact

        weekday_freq = [0 for _ in range(7)]
        for p, m, d in self._convo:
            if key(p):
                weekday_freq[d.weekday()] += 1

        weekday_total = sum(weekday_freq)
        if weekday_total == 0:  # If this conversation has no messages
            return [0 for _ in weekday_freq]
        return [day / weekday_total for day in weekday_freq]

    def raw_msgs_by_time(self, window=60, contact=None):
        """The percent of conversation by time of day
        Parameters:
            window (optional): The time length of each bin in minutes (default, 60 minutes, or 1 hour)
            contact (optional): The contact you are interested in. (default, all contacts)
        Return:
            a list containing average frequency of chatting by
            times in days, starting at 12:00 am. Default window is 60 minute
            interval. If time less than the passed window is left at the end,
            it is put at the end of the list in it's own window.
            e.g. if window=60, the  list returned is of length 24, with each index representing one hour of chatting
            if window=61 the list returned is still of length 24, but indexes 0-22 representing 61 minutes,
                                                                  and index 23 representing 37 minutes
        """
        contact = self._assert_contact(contact)

        if contact is not None:
            filt = lambda x: x in contact
        else:
            filt = lambda x: True

        total_msgs = 0
        msg_bucket = [[CustomDate.minutes_to_time(i * window), 0] for i in range(ceil(60 * 24 / window))]

        for person, msg, date in self._convo:
            if filt(person.lower()):
                index = (date.minutes() // window) % (len(msg_bucket))
                msg_bucket[index][1] += 1
                total_msgs += 1
        for i in range(len(msg_bucket)):
            msg_bucket[i][1] /= (total_msgs / 100)
        return msg_bucket

    def raw_frequency(self, person=None, word=None):
        """Frequency of word use for people in the chat
        Parameters:
            person (optional): The name (as a string) of the person you are interested in
            word (optional): The word (as a string) you are interested in
        Return:
            There are 4 different return types depending on the arguments passed:
            Yes person and Yes word: the number of times the specified person has said the specified word
            Yes person and No word: A counter object of words mapped to their frequency for the specified person
            No person and Yes word: The number of times the specified word has been said by anyone in the chat
            No person and No word: A dictionary with keys being the names of people in the conversation
                and values being counter objects of words mapped to their frequency
        """
        if person is not None:
            person = person.lower()
            assert person in self._name, "\"{0}\" is not in this conversation".format(person.title())
        if word is not None:
            word = word.lower()
        if person is not None:
            try:
                if word is not None:
                    return self._individual_words[person][word]
                else:
                    return self._individual_words[person]
            except KeyError:
                return Counter() if word is None else 0
        else:
            if word is not None:
                res = 0
                for key, val in self._individual_words.items():
                    res += self._individual_words[key][word]
                return res
            else:
                return self._individual_words

    def raw_convo_starter_freqs(self, threshold):
        """Returns the frequency that each participant begins conversations as percents
        Parameter:
            threshold: the number of minutes lag that counts as the threshold for starting a new conversation.
        Return:
            A Counter of names mapped to frequencies of conversation starting (as percents)
        """
        raw_freqs = self._raw_convo_starter(threshold)
        total = sum(len(freq) for _, freq in raw_freqs.items())
        if total == 0:
            return raw_freqs
        res = Counter()
        for key, freq in raw_freqs.items():
            res[key] = len(freq) / total * 100
        return res

    def raw_convo_killer_freqs(self, threshold):
        """Returns the frequency (as percents) that each participant 'kills' conversations, where killing is defined as
        being the last person to send a message with no replies for at least threshold minutes
        Parameters:
            threshold: the number of minutes lag that counts as the threshold for starting a new conversation.
        Return:
            A Counter of names mapped to frequencies of conversation killing (as percents)
        """
        raw_freqs = self._raw_convo_killer(threshold)
        total = sum(len(freq) for _, freq in raw_freqs.items())
        if total == 0:
            return raw_freqs
        res = Counter()
        for key, freq in raw_freqs.items():
            res[key] = len(freq) / total * 100
        return res

    def raw_find_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that contain the passed message
        Parameters:
            query: The string query to search for
            ignore_case (optional): Whether to search by case sensitive
        Return:
            A list sorted list of indexes for messages containing query
        """
        # python re cheat sheet: https://www.debuggex.com/cheatsheet/regex/python

        assert isinstance(query, str), "query must be a string"
        key = lambda x: x
        if ignore_case:
            key = lambda x: x.lower()
        indexes = []
        for i in range(len(self._convo)):
            if query in key(self._convo[i][1]):
                indexes.append(i)
        return indexes

    def raw_match_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that match the passed message
        Parameters:
            query: The string query to search for
            ignore_case (optional): Whether to search by case sensitive
        Return:
            A list sorted list of indexes for messages matching query
        """
        # python re cheat sheet: https://www.debuggex.com/cheatsheet/regex/python

        indexes = []
        try:
            r = re.compile(query, re.IGNORECASE) if ignore_case else re.compile(query)
            for i in range(len(self._convo)):
                if r.fullmatch(self._convo[i][1]) is not None:
                    indexes.append(i)
            return indexes
        except re.error:
            raise re.error("\"{0}\" is not a valid regex string".format(query))

    def raw_longest_messages(self, num=None) -> list:
        """Returns a list of integers corresponding to message indexes, sorted in reverse order based on length (longest
        message index first)
        Parameters:
            num (optional): (int|None) the number of messages to include, or None to include all
        """
        assert num is None or isinstance(num, int), (
            "num must be None or an integer representing the number of messages desired"
        )
        num = min(num, len(self)) if num is not None else len(self)

        order = Counter({index: len(self._convo[index][1]) for index in range(len(self))})
        return order.most_common(num)

    # -----------------------------------------------   PUBLIC METHODS ---------------------------------------------- #

    # -----------------------------------------------   PRIVATE METHODS ---------------------------------------------- #

    @staticmethod
    def list_to_combined_string(list_of_people):
        """Combines a list of people into a single string, converting each perons's name to lowercase, separating
        first/middle/last name(s) with hyphens (-) and various individual's names with underscores (_). Cuts off a
        string past 255 raw_characters
        """
        name = ""
        for person in list_of_people:
            split = person.split(' ')
            for i in range(len(split) - 1):
                name += split[i]
                name += '-'
            name += split[-1]
            name += '_'
        name = name[:-1]
        if len(name) > 255:
            name = name[:255]
        else:
            name = name

        return name + '/'

    def _setup_new_word_cloud(self, preferences):
        """Takes in all the preferences for a word cloud, and writes everything to files"""
        assert 'type' in preferences, "You must pass a type argument"
        assert preferences['type'] in WordCloud.WORD_CLOUD_TYPES, "invalid type, {0} is not in {1}"\
            .format(preferences['type'], WordCloud.WORD_CLOUD_TYPES)

        # Creates wordcloud with directory
        wc_type = preferences['type']
        self._word_cloud = WordCloud(wc_type, preferences)
        self.save_word_freq(path=WordCloud.WORD_CLOUD_INPUT_PATH)

        # Returns the results from verifying settings for this wordcloud
        return self._word_cloud.verify_word_cloud_setup()

    def _raw_convo_starter(self, threshold, start=None, end=None):
        """Returns a Counter"""
        CustomDate.assert_dates(start, end)

        # Sets the start and end dates, finds the appropriate
        #  message number if start/ end are not None, else index 1 for start and len(convo) for end
        start_date_index = CustomDate.bsearch_index(self._convo, start, key=lambda x: x[2]) if start is not None else 1
        end_date_index = CustomDate.bsearch_index(self._convo, end, key=lambda x: x[2]) \
            if start is not None else self._len

        convo_start_freq = dict()
        for person in self._people:
            convo_start_freq[person] = []
        convo_start_freq[self._convo[start_date_index - 1][0]].append(start_date_index - 1)
        for i in range(start_date_index, end_date_index):
            curr_date = self._convo[i][2]
            prev_date = self._convo[i - 1][2]
            if curr_date.distance_from(prev_date) >= threshold:
                convo_start_freq[self._convo[i][0]].append(i)
        return Counter(dict((key.title(), val) for key, val in convo_start_freq.items()))

    def _raw_convo_killer(self, threshold, start=None, end=None):
        """Returns a Counter"""
        CustomDate.assert_dates(start, end)

        # Sets the start and end dates, finds the appropriate
        #  message number if start/ end are not None, else index 1 for start and len(convo) for end
        start_date_index = CustomDate.bsearch_index(self._convo, start, key=lambda x: x[2]) if start is not None else 0
        end_date_index = CustomDate.bsearch_index(self._convo, end, key=lambda x: x[2]) \
            if start is not None else self._len - 1

        convo_start_freq = dict()
        for person in self._people:
            convo_start_freq[person] = []
        convo_start_freq[self._convo[start_date_index - 1][0]].append(start_date_index - 1)
        for i in range(start_date_index, end_date_index):
            curr_date = self._convo[i][2]
            next_date = self._convo[i + 1][2]
            if next_date.distance_from(curr_date) >= threshold:
                convo_start_freq[self._convo[i][0]].append(i)
        return Counter(dict((key.title(), val) for key, val in convo_start_freq.items()))

    def _raw_word_freqs(self):
        """Returns a dictionary that maps names of people in the conversation
        to a Counter object of their raw word frequencies
        """
        raw_word_freq = dict()
        for person, msg, date in self._convo:
            if person not in raw_word_freq:
                raw_word_freq[person] = Counter()
            raw_word_freq[person].update(msg.lower().split(' '))
        return raw_word_freq

    def _cleaned_word_freqs(self):
        raw_words = self._raw_word_freqs()
        cleaned_words = dict()
        for key, val in raw_words.items():
            cleaned_words[key] = Counter()
            for word, freq in val.most_common():
                striped_word = word.strip('.!123456789-+?><}{][()\'\""\\ /*#$%^&#@,')
                if striped_word < 'z' * 10:
                    if '.com' not in striped_word and 'www.' not in striped_word \
                            and 'http' not in striped_word and '.io' not in striped_word \
                            and '.edu' not in striped_word:
                        if striped_word not in cleaned_words[key]:
                            cleaned_words[key][striped_word] = freq
                        else:
                            cleaned_words[key][striped_word] += freq
        return cleaned_words

    def __msgs_per_person(self):
        res = dict()
        for person, msg, date in self._convo:
            if person not in res:
                res[person] = 1
            else:
                res[person] += 1
        return Counter(res)

    def __msgs_spoken(self, name):
        name = name.lower()
        if name not in self._people:
            raise Exception("Invalid name passed")
        num = 0
        for person, msg, date in self._convo:
            if person == name:
                num += 1
        return num

    def __words_per_person(self):
        res = dict()
        for person, msg, date in self._convo:
            if person not in res:
                res[person] = len(msg.split())
            else:
                res[person] += len(msg.split())
        return Counter(res)

    def __words_spoken(self, name):
        name = name.lower()
        if name not in self._people:
            raise Exception("Invalid name passed")
        num = 0
        for person, msg, date in self._convo:
            if person == name:
                num += len(msg.split())
        return num

    def __ave_words_per_person(self):
        words = []
        for name in self._people:
            msgs = float(self.__msgs_spoken(name))
            tot_words = float(self.__words_spoken(name))
            if msgs > 0:
                words.append((name, tot_words / msgs))
        res = Counter()
        for name, ave in words:
            res[name] = ave
        return res

    def __ave_words(self, name):
        name = name.lower()
        if name not in self._people:
            return -1
        if self.__msgs_spoken(name) == 0:
            return 0
        return self.__words_spoken(name) / self.__msgs_spoken(name)

    def _assert_contact(self, contact):
        assert type(contact) in [type(None), str, list], "Contact must be of type string or a list of strings"
        if type(contact) is list:
            for i, ele in enumerate(contact):
                assert type(ele) is str, "Each element in contact must be a string"
                contact[i] = ele.lower()
            for ele in contact:
                assert ele in self._people, "{0} is not in the list of people for this conversation:\n{1}".format(
                    ele, str(self._people))
        elif type(contact) is str:
            assert contact in self._people, "{0} is not in the list of people for this conversation:\n{1}".format(
                contact, str(self._people))
            contact = [contact]

        return contact

    # -----------------------------------------------   PRIVATE METHODS ---------------------------------------------- #

    def __getitem__(self, index):
        """Returns the tuple (person, message, datetime) for the corresponding index"""
        if type(index) is not int:
            raise TypeError
        elif index >= len(self) or index < -len(self):
            raise IndexError
        else:
            return self._convo[index] if index >= 0 else self._convo[len(self) + index]

    def __len__(self):
        """Returns the number of messages in self"""
        return self._len

    def __str__(self):
        """Returns a string with the alphabetically sorted names of people
        in this conversation
        """
        return "Conversation for " + self._name.title()

    def __iter__(self):
        return (message for message in self._convo)

