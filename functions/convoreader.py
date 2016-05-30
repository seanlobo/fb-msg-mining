from colorama import init, Fore, Back, Style
from collections import Counter
from math import ceil
import re
import os

from functions.customdate import CustomDate, bsearch_index
import functions.emojis as emojis


init(autoreset=True)


class ConvoReader():
    def __init__(self, convo_name, convo_list):
        self.name = convo_name.lower()
        self.convo = [[name.lower(), emojis.emojify(msg), CustomDate(date)] for name, msg, date in convo_list]
        self.people = sorted(self.name.split(', '))
        self.individual_words = self._cleaned_word_freqs()
        self.len = len(self.convo)
        self.path = 'data/'
        self.preferences = {person: dict() for person in self.people}
        self.preferences_choices = {'personal': ['Fore'], 'global': ['new_convo_time', 'date_Fore_color']}

    def print_people(self):
        """Prints to the screen an alphabetically sorted list of people
        in the conversation
        """
        res = ""
        for i, pers in enumerate(self.people):
            res += "{0}) {1}\n".format(i + 1, pers.title())
        print(res)

    def messages(self, name=None):
        """Number of messages for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_messages(name)
        if type(value) is int:
            print(value)
        else:
            for person, msgs in value.most_common():
                print("{0}: {1}".format(person, msgs))
        print()

    def words(self, name=None):
        """Number of words for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        Return:
            A number if name is not passed, otherwise a Counter object storing the number
            of words as values paired with names of people as keys.
        """
        value = self._raw_words(name)
        if type(value) is int:
            print(value)
        else:
            for person, msgs in value.most_common():
                print("{0}: {1}".format(person, msgs))
        print()

    def ave_words(self, name=None):
        """Average number of words for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        Return:
            A number if name is not passed, otherwise a Counter object storing the average
            number of words as values paired with names of people as keys.
        """
        value = self._raw_ave_words(name)
        if type(value) is float:
            print(value)
        else:
            for person, msgs in value.most_common():
                print("{0}: {1}".format(person, msgs))
        print()

    def frequency(self, person=None, word=None, limit=True):
        """Frequency of words for people in the chat
        Parameters:
            person (optional): The name (as a string) of the person you are interested in
            word (optional): The word (as a string) you are interested in
            limit (optional): bool or int. If int desplays maximum that many words,
                if false desplays all words, if true desplays top 10. Should only be used
                if word is left out, and is ignored if a value for word is given
        """
        try:
            assert type(limit) in [type(True), type(False), int], "limit must be an int or boolean"
            value = self._raw_frequency(person=person, word=word)
        except AssertionError as e:
            print(e)
            return

        if type(value) is int:
            if person is not None and word is not None:  # specified a person and word
                string = ""
                string += person.title() + ": \n"
                string += "\t" + word.lower() + ": " + str(value)
                print(string)
                print()
            else:
                string = ""
                string += "Everyone in total: \n"
                string += "\t" + word.lower() + ": " + str(value)
                print(string)
                print()

        else:
            if type(value) is dict and type(value) is not Counter:
                for key, val in value.items():
                    if limit is True:
                        lim = 10
                    elif limit is False:
                        lim = len(val)
                    else:
                        lim = limit
                    i = 1
                    string = key + "\n"
                    for word, freq in val.most_common(lim):
                        string += "\t{0}) {1}: {2}\n".format(str(i), word, freq)
                        i += 1
                    print(string)
                    print()
            else:
                if limit is True:
                    limit = 10
                elif limit is False:
                    limit = len(value)
                string = person + "\n"
                i = 1
                for word, freq in value.most_common(limit):
                    string += "\t{0}) {1}: {2}\n".format(str(i), word, freq)
                    i += 1
                print(string)
                print()

    def characters(self, person=None):
        """Returns character frequency in conversation in a Counter object"""
        if person is not None:
            assert type(person) is str, "Optional parameter person must be a string"
            person = person.lower()
            assert person in self.people, "The person you said isn't in this conversation; this conversatin is for" \
                                          " {0}".format(str(self.people))
        res = Counter()
        for pers, msg, date in self.convo:
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

    def get_emoji(self, text):
        """Returns the emoji corresponding to the src value passed,
        or the string passed if appropriate emojis isn't found
        """
        return emojis.src_to_emoiji(text)

    def prettify(self, start=None, end=None):
        """Prints a "pretty" version of the conversation history"""
        self.__assert_dates(start, end)
        if start is not None:
            start = CustomDate.from_date_string(start)
            assert start.date >= self.convo[0][2].date, \
                "Your conversations only begin after {0}".format(self.convo[0][2].full_date)
            start = bsearch_index(self.convo, start, key=lambda x: x[2])
        else:
            start = 0
        if end is not None:
            end = CustomDate.from_date(CustomDate.from_date_string(end) + 1)
            assert end.date <= self.convo[-1][2].date,\
                "Your conversations ends on {0}".format(self.convo[-1][2].full_date)
            end = bsearch_index(self.convo, end, key=lambda x: x[2])
        else:
            end = len(self.convo)


        #for person, msg, date in self.convo:
        for i in range(start, end):
            self._print_message(i)


    def msgs_graph(self, contact=None, start=None, end=None):
        """Prettily prints to the screen the message history of a chat
        Parameter:
            contact (optional): the name (as a string) of the person you are interested in.
                (default: all contacts)
            start (optional): the date to start the graph from. Defaults to the date of the first message
            end (optional): the date to end the graph with. Defaults to the last message sent
        """
        try:
            msgs_freq = self._msgs_graph(contact)
            self.__assert_dates(start, end)
        except AssertionError as e:
            print(e)
            return

        if contact is not None:
            print('Graph for {0}'.format(str(contact.title())))

        if start is not None:
            start = CustomDate.from_date_string(start)
        else:
            start = msgs_freq[0][0]
        if end is not None:
            end = CustomDate.from_date_string(end)
        else:
            end = msgs_freq[-1][0]

        if not start <= end:
            print("The start date of the conversation must be before the end date")
            return


        start_index, end_index = 0, len(msgs_freq)
        for i in range(end_index):
            if msgs_freq[i][0].date == start.date:
                start_index = i
            if msgs_freq[i][0].date == end.date:
                end_index = i + 1

        max_msgs = max(msgs_freq, key=lambda x: x[1])[1]
        value = max_msgs / 50
        print("\nEach \"#\" referes to ~{0} messages".format(value))
        print()


        MAX_DATE_LEN = 12
        # The Maximum length of the string containing the longest date (with padding) i.e. '12/12/2012  '

        MAX_NUM_LENGTH = len(str(max(msgs_freq, key=lambda x: x[1])[1]))
        # The maximum length of the string containing the largest number of messages in a day i.e. "420"

        for i in range(start_index, end_index):
            day = msgs_freq[i][0].to_string()
            day += ' ' * (MAX_DATE_LEN - len(day))

            msg_num = str(msgs_freq[i][1])
            msg_num += " " * (MAX_NUM_LENGTH - len(msg_num))

            string = day + msg_num
            if i % 2 == 0:
                print(string + " |", end="")
            else:
                print(MAX_DATE_LEN * " " + msg_num + " |", end="")

            if msgs_freq[i][1] == 0:
                print("(none)")
            else:
                print('#' * int(msgs_freq[i][1] / value))
        print()

    def msgs_by_weekday(self):
        """Prints out chat frequency by day of week
        """
        by_weeday = self._raw_msgs_by_weekday()
        for day, freq in enumerate(by_weeday):
            print("{0}: {1}%".format(CustomDate.days_of_week[day], str(freq * 100)[:5]))
        print()

    def msgs_by_day(self, window=60, contact=None, threshold=None):
        """Prints to the screen a graphical result of msgs_by_day
        Parameters:
            window (optional): The length of each bin in minutes (default, 60 minutes, or 1 hour)
            contact (optional): The contact you are interested in. (default, all contacts)
            threshold (optional): The minimum threshold needed to print one '#'
        """
        try:
            frequencies = self._msgs_by_day(window, contact)
        except AssertionError as e:
            print(e)
            return

        if threshold is None:
            threshold = window / 120
        else:
            try:
                assert threshold > 0, "Threshold must be a possitive number"
            except AssertionError as e:
                print(e)
                return

        to_print = ''
        time_len = 9
        num_len = 6
        for time, freq in frequencies:
            time_str = time + (time_len - len(time) + 1) * ' '
            freq_str = str(freq)[:6]
            freq_str += (num_len - len(freq_str)) * '0' + '%'
            to_print += time_str
            to_print += freq_str
            to_print += ' |'

            to_print += '#' * int(freq / threshold)

            to_print += '\n'
        print(to_print)

    def save_word_freq(self):
        """Saves to a file the ordered rankings of word frequencies by person in the chat"""
        dir_name = ""
        for person in self.people:
            split = person.split(' ')
            for i in range(len(split) - 1):
                dir_name += split[i]
                dir_name += '-'
            dir_name += split[-1]
            dir_name += '_'
        dir_name = dir_name[:-1]
        if len(dir_name) > 255:
            name = dir_name[:255]
        else:
            name = dir_name

        os.makedirs(self.path + name, exist_ok=True)
        for person, counter in self.individual_words.items():
            split = person.split()
            pers = ''
            for i in range(len(split) - 1):
                pers += split[i]
                pers += '-'
            pers += split[-1]
            with open(self.path + name + '/' + pers + '_word_freq.txt', mode='w', encoding='utf-8') as f:
                lst = []
                for key, val in counter.items():
                    lst.append((key, val))
                for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
                    f.write("{0}: {1}".format(key, val) + "\n")
        count = Counter()
        for key, val in self.individual_words.items():
            count += val
        with open(self.path + name + '/' + 'total.txt', mode='w', encoding='utf-8') as f:
            for key, val in count.most_common():
                f.write("{0}: {1}".format(key, val) + "\n")

    def set_preferences(self):
        """Allows users to choice color preferences and stores values to
        self.preferences dictionary
        """

        # The following idea is used in this method
        # >>> black = 'BLACK'
        # >>> Fore.BLACK
        # '\x1b[30m'
        # >>> eval('Fore.{0}'.format(black))
        # '\x1b[30m'
        # >>>

        choice = None
        while choice != -1:
            while choice not in [str(ele) for ele in range(-1, len(self.people) + 1)]:
                print('\n-1) Cancel/Finish preferences')
                print(' 0) View current preferences\n')

                max_len = len(str(len(self.people))) + 1
                for i, person in enumerate(self.people):
                    if 'Fore' in self.preferences[person]:
                        # is the foreground quality in our preferences?
                        try: # if so we try to use it. Must put in a try statement
                            # in case we have bad values (as in a user modified the file)
                            print(eval('Fore.{0}'.format(self.preferences[person]['Fore'])) + "{0}) {1}"
                                  .format(' ' * (max_len - len(str(i + 1))) + str(i + 1), person))
                        except AttributeError:
                            # if we have a bad value an attribute error should occur from the eval call
                            print("{0}) {1}".format(' ' * (max_len - len(str(i + 1))) + str(i + 1), person))
                            # above print is identical to below in else
                    else:
                        print("{0}) {1}".format(' ' * (max_len - len(str(i + 1))) + str(i + 1), person))

                choice = input('\nSelect your option\n> ')

            choice = int(choice)
            if choice == 0:
                print(self.preferences)
            elif choice in range(1, len(self.people) + 1):
                # Colorama choices supported are below (https://pypi.python.org/pypi/colorama)
                color_choies = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE"]
                color = None
                while color not in [str(i) for i in range(len(color_choies))]:
                    print("The following are color choices for the ForeGround for {0}:"
                          .format(self.people[choice - 1]))
                    print()
                    for i in range(len(color_choies)):
                        print(eval('Fore.{0}'.format(color_choies[i])) + '{0}) {1}'
                              .format(i, color_choies[i]))
                    color = input('\nSelect your option\n> ')
                color = int(color)
                self.preferences[self.people[choice - 1]]['Fore'] = color_choies[color]


    def _print_message(self, number):
        try:
            assert type(number) is int, "number must be an integer"
            assert number in range(len(self.convo)), "number must be in range({0})".format(len(self.convo))
        except AssertionError as e:
            raise e

        person, msg, date = self.convo[number]
        # the length of the longest name in self.people
        max_len = len(max(self.people, key=lambda name: len(name)))
        padding = ' ' * (max_len - len(person))
        if 'Fore' in self.preferences[person.lower()]:
            try:
                print(eval('Fore.{0}'.format(self.preferences[person]['Fore'])) + person.title(),
                      end=": " + padding)
            except AttributeError:
                print(person.title(), end=": " + padding)
        else:
            print(person.title(), end=": " + padding)
        print(msg, end="")
        if 'date_Fore_color' in self.preferences:
            try:
                print('Fore.{0}'.format(self.preferences['date_Fore_color']) + " | " + str(date))
            except AttributeError:
                print(" | " + str(date))
        else:
            print(" | " + str(date))



    def find(self, query, ignore_case=False, regex=False):
        """Prints to the console the results of searching for the query string
            Parameters:
                case_sensitive (optional): Whether the query string is case sensitive
                regex (optional): Whether the query is a regular expression
        """
        # python re cheat sheet: https://www.debuggex.com/cheatsheet/regex/python

        try:
            indexes = self._match_indexes(query, ignore_case=ignore_case) if regex \
                else self._find_indexes(query, ignore_case=ignore_case)
        except re.error as e:
            print(e)
            return
        if len(indexes) == 0:
            print()
            return
        MAX_LEN_INDEX = len(max(map(str, indexes), key=len)) + 2
        for i in indexes:
            print(str(i) + ' ' * (MAX_LEN_INDEX - len(str(i))), end="")
            self._print_message(i)



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

    def _msgs_graph(self, contact=None):
        """The raw data used by print_msgs_graph to display message graphs
        Parameters:
            contact (optional): the name (as a string) of the person you are interested in
                (default: all contacts)
        Return:
            A 2D list with inner lists being of length 2 lists and storing a day as element 0
            and the number of total messages sent that day as element 1
        """
        contact = self.__assert_contact(contact)

        if contact is not None:
            filt = lambda x: x in contact
        else:
            filt = lambda x: True

        start = self.convo[0][2]
        end = self.convo[-1][2]
        days = end - start

        msg_freq = [[None, 0] for i in range(days + 1)]
        for person, msg, date in self.convo:
            if filt(person.lower()):
                msg_freq[date - start][1] += 1

        for day in range(len(msg_freq)):
            msg_freq[day][0] = CustomDate.from_date(start + day)

        return msg_freq

    def _msgs_by_day(self, window=60, contact=None):
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
        contact = self.__assert_contact(contact)

        if contact is not None:
            filt = lambda x: x in contact
        else:
            filt = lambda x: True

        total_msgs = 0
        msg_bucket = [[CustomDate.minutes_to_time(i * window), 0] for i in range(ceil(60 * 24 / window))]

        for person, msg, date in self.convo:
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
            assert person in self.name, "\"{0}\" is not in this conversation".format(person.title())
        if word is not None:
            word = word.lower()
        if person is not None:
            if word is not None:
                return self.individual_words[person][word]
            else:
                return self.individual_words[person]
        else:
            if word is not None:
                res = 0
                for key, val in self.individual_words.items():
                    res += self.individual_words[key][word]
                return res
            else:
                return self.individual_words

    def _raw_msgs_by_weekday(self):
        """Returns a list containing frequency of chatting by days
        of week, ordered by index, with 0 being Monday and 6 Sunday
        """
        weekday_freq = [0 for i in range(7)]
        check = self.convo[0][2]
        msgs = 0
        for person, msg, date in self.convo:
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
        for person, msg, date in self.convo:
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
                    if '.com' not in striped_word and 'www.' not in striped_word\
                    and 'http' not in striped_word and '.io' not in striped_word\
                    and '.edu' not in striped_word:
                        if striped_word not in cleaned_words[key]:
                            cleaned_words[key][striped_word] = freq
                        else:
                            cleaned_words[key][striped_word] += freq
        return cleaned_words

    def _find_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that contain the passed message
        Parameters:
            case_sensitive (optional): Whether to search by case sensitive
        """
        key = lambda x: x
        if ignore_case:
            key = lambda x: x.lower()
        indexes = []
        for i in range(len(self.convo)):
            if query in key(self.convo[i][1]):
                indexes.append(i)
        return indexes

    def _match_indexes(self, query, ignore_case=False):
        """Returns a list with the indexes of each message that match the passed message"""
        # python re cheat sheet: https://www.debuggex.com/cheatsheet/regex/python

        indexes = []
        try:
            r = re.compile(query, re.IGNORECASE) if ignore_case else re.compile(query)
            for i in range(len(self.convo)):
                if r.fullmatch(self.convo[i][1]) is not None:
                    indexes.append(i)
            return indexes
        except re.error:
            raise re.error("\"{0}\" is not a valid regex string".format(query))



    def __msgs_per_person(self):
        res = dict()
        for person, msg, date in self.convo:
            if person not in res:
                res[person] = 1
            else:
                res[person] += 1
        return Counter(res)

    def __msgs_spoken(self, name):
        name = name.lower()
        if name not in self.people:
            raise Exception("Invalid name passed")
        num = 0
        for person, msg, date in self.convo:
            if person == name:
                num += 1
        return num

    def __words_per_person(self):
        res = dict()
        for person, msg, date in self.convo:
            if person not in res:
                res[person] = len(msg.split())
            else:
                res[person] += len(msg.split())
        return Counter(res)

    def __words_spoken(self, name):
        name = name.lower()
        if name not in self.people:
            raise Exception("Invalid name passed")
        num = 0
        for person, msg, date in self.convo:
            if person == name:
                num += len(msg.split())
        return num

    def __ave_words_per_person(self):
        words = []
        for name in self.people:
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
        if name not in self.people:
            return -1
        return self.__words_spoken(name) / self.__msgs_spoken(name)

    def __assert_dates(self, start, end):
        # python re cheat sheet: https://www.debuggex.com/cheatsheet/regex/python

        assert type(start) in [type(None), str], "Start needs to be a date string"
        assert type(end) in [type(None), str], "End needs to be a date string"
        if type(start) is str:
            r = re.compile('\d{1,2}/\d{1,2}/\d{1,4}')
            assert r.fullmatch(start) is not None, ("\"{0}\" is not a valid date, it must be in the format ".format(start) + \
                                                    "{month}/{day}/{year}")
            r = re.compile('\d{1,2}/\d{1,2}/\d{3}')
            assert r.fullmatch(
                start) is None, "the {year} part of a date must be either 2 or 4 numbers (e.g. 2016 or 16)"
        if type(end) is str:
            r = re.compile('\d{1,2}/\d{1,2}/\d{1,4}')
            assert r.fullmatch(end) is not None, ("\"{0}\" is not a valid date, it must be in the format ".format(end) + \
                                                  "{month}/{day}/{year}")
            r = re.compile('\d{1,2}/\d{1,2}/\d{3}')
            assert r.fullmatch(end) is None, "the {year} part of a date must be either 2 or 4 numbers (e.g. 2016 or 16)"

    def __assert_contact(self, contact):
        assert type(contact) in [type(None), str, list], "Contact must be of type string or a list of strings"
        if type(contact) is list:
            for i, ele in enumerate(contact):
                assert type(ele) is str, "Each element in contact must be a string"
                contact[i] = ele.lower()
            for ele in contact:
                assert ele in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
                    ele, str(self.people))
        elif type(contact) is str:
            assert contact in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
                contact, str(self.people))
            contact = [contact]

        return contact

    def __getitem__(self, index):
        """Returns the tuple (person, message, datetime) for the corresponding index"""
        if type(index) is not int:
            raise TypeError
        elif index >= len(self) or index < -len(self):
            raise IndexError
        else:
            return self.convo[index] if index >= 0 else self.convo[len(self) + index]

    def __len__(self):
        """Returns the number of messages in self"""
        return self.len

    def __str__(self):
        """Returns a string with the alphabetically sorted names of people
        in this conversation
        """
        return "Converation for " + self.name.title()

    def __repr__(self):
        """Returns a valid constructor for this object"""
        return "ConvoReader({0}, {1})".format(repr(self.name), repr(self.convo))
