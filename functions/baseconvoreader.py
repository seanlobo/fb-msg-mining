from collections import Counter
from math import ceil
import re


from functions.customdate import CustomDate
import functions.emojis as emojis


class BaseConvoReader():
    def __init__(self, convo_name, convo_list):
        self._name = convo_name.lower()
        self._convo = [[name.lower(), emojis.emojify(msg), CustomDate(date)] for name, msg, date in convo_list]
        self._people = self.get_people()
        self._individual_words = self._cleaned_word_freqs()
        self._len = len(self._convo)

    def characters(self, person=None):
        """Returns character frequency in conversation in a Counter object"""
        if person is not None:
            assert type(person) is str, "Optional parameter person must be a string"
            person = person.lower()
            assert person in self._people, "The person you said isn't in this conversation; this conversatin is for" \
                                           " {0}".format(str(self._people))
        res = Counter()
        for pers, msg, date in self._convo:
            if person is None or pers == person:
                res.update(msg)
        return res

    def emojis(self, person=None):
        """Returns emojis frequency for conversation in a Counter object
        Parameter:
            person (optional): the name of the person whose emojis you would like. If left to default
                None, an aggregate total for the conversation is returned
        """
        chars = self.characters(person)
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

    def get_people(self):
        duplicate = re.compile("duplicate #\d+", re.IGNORECASE)
        people = []
        for person in sorted(self._name.split(', ')):
            if duplicate.fullmatch(person) is None:
                people.append(person)
        return people

    def _raw_messages(self, name=None):
        """Number of messages for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        Return:
            A number if name is not passed, otherwise a Counter object storing the number
            of mesages as values paired with names of people as keys.
        """
        if name is None:
            return self.__msgs_per_person()
        else:
            return self.__msgs_spoken(name)

    def _raw_words(self, name=None):
        """Number of words for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        Return:
            A number if name is not passed, otherwise a Counter object storing the number
            of words as values paired with names of people as keys.
        """

        if name is None:
            return self.__words_per_person()
        else:
            return self.__words_spoken(name)

    def _raw_ave_words(self, name=None):
        """Average number of words for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        Return:
            A number if name is not passed, otherwise a Counter object storing the average
            number of words as values paired with names of people as keys.
        """

        if name is None:
            return self.__ave_words_per_person()
        else:
            return self.__ave_words(name)

    def _raw_msgs_graph(self, contact=None):
        """The raw data used by print_msgs_graph to display message graphs
        Parameters:
            contact (optional): the name (as a string) of the person you are interested in
                (default: all contacts)
        Return:
            A 2D list with inner lists being of length 2 lists and storing a day as element 0
            and the number of total messages sent that day as element 1
        """
        contact = self._assert_contact(contact)

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
                msg_freq[date - start][1] += 1

        for day in range(len(msg_freq)):
            msg_freq[day][0] = CustomDate.from_date(start + day)

        return msg_freq

    def _raw_msgs_by_time(self, window=60, contact=None):
        """The percent of conversation by time of day
        Parameters:
            window (optional): The length of each bin in minutes (default, 60 minutes, or 1 hour)
            contact (optional): The contact you are interested in. (default, all contacts)
        Return:
            a list containing average frequency of chatting by
            times in days, starting at 12:00 am. Default window is 60 minute
            interval.If time less than the passed window is left at the end,
            it is put at the end of the list
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

    def _raw_frequency(self, person=None, word=None):
        """Frequency of words for people in the chat
        Parameters:
            person (optional): The name (as a string) of the person you are interested in
            word (optional): The word (as a string) you are interested in
        Return:
            There are 4 different return types depending on the arguments passed:
            Yes person and Yes word: the number of times the specified person has
                said the specified word
            Yes person and No word: A counter object representing the frequency of words
                for the specified person
            No person and Yes word: The number of times the specified word has been said by
                anyone in the chat
            No person and No word: A dictionary with keys being the names of people in the conversation
                and values being counter objects with frequency of words
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

    def _raw_msgs_by_weekday(self):
        """Returns a list containing frequency of chatting by days
        of week, ordered by index, with 0 being Monday and 6 Sunday
        """
        weekday_freq = [0 for i in range(7)]
        check = self._convo[0][2]
        msgs = 0
        for person, msg, date in self._convo:
            if check - date == 0:
                msgs += 1
            else:
                weekday_freq[date.weekday()] += msgs
                msgs = 1

        return [day / sum(weekday_freq) for day in weekday_freq]

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

    def _find_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that contain the passed message
        Parameters:
            ignore_case (optional): Whether to search by case sensitive
        """
        key = lambda x: x
        if ignore_case:
            key = lambda x: x.lower()
        indexes = []
        for i in range(len(self._convo)):
            if query in key(self._convo[i][1]):
                indexes.append(i)
        return indexes

    def _match_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that match the passed message"""
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

    @staticmethod
    def _assert_dates(start, end):
        assert type(start) in [type(None), str], "Start needs to be a date string"
        assert type(end) in [type(None), str], "End needs to be a date string"
        if type(start) is str:
            r = re.compile('\d{1,2}/\d{1,2}/\d{1,4}')
            assert r.fullmatch(start) is not None, ("\"{0}\" is not a valid date, it must be in the format "
                                                    .format(start) + "{month}/{day}/{year}")
            r = re.compile('\d{1,2}/\d{1,2}/\d{3}')
            assert r.fullmatch(
                start) is None, "the {year} part of a date must be either 2 or 4 numbers (e.g. 2016 or 16)"
        if type(end) is str:
            r = re.compile('\d{1,2}/\d{1,2}/\d{1,4}')
            assert r.fullmatch(end) is not None, ("\"{0}\" is not a valid date, it must be in the format "
                                                  .format(end) + "{month}/{day}/{year}")
            r = re.compile('\d{1,2}/\d{1,2}/\d{3}')
            assert r.fullmatch(end) is None, "the {year} part of a date must be either 2 or 4 numbers (e.g. 2016 or 16)"

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

    def __iter__(self):
        return (message for message in self._convo)

