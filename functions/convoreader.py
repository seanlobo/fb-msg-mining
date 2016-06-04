from colorama import init, Fore, Back, Style
from collections import Counter
import os
import re

from functions.baseconvoreader import BaseConvoReader
from functions.customdate import CustomDate
import functions.emojis as emojis


init(autoreset=True)


class ConvoReader(BaseConvoReader):
    def __init__(self, convo_name, convo_list):
        """Constructor for ConvoReader, important instance variables summarized below:
        name  String - this conversation's name, all people in the conversation concatenated together
                        separated by commas and a space. E.g. "swetha raman, sean lobo"
        convo List<Tuple> - a list holding the entire conversation. Each tuple contains the information for
                            one message, organized in the form ---> (person_speaking, msg_content, date-time_sent_at)
                            Example) accessing the 5th message would be self.convo[4], accessing the actual content
                            would be self.convo[4][1]
        people List<String> - A list of all people in the conversation. E.g. ["swetha raman", "sean lobo"]
        """
        BaseConvoReader.__init__(self, convo_name, convo_list)

        self.path = 'data/' + self._set_path()
        self.preferences = self._load_preferences()
        # preferences_choices = {'personal': {"Name": val, "Message": val, "Date" : val},
        #                        'global': {'new_convo_time': val} }
        self.COLOR_CHOICES = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE",
                              "LIGHTBLACK_EX", "LIGHTBLUE_EX", "LIGHTCYAN_EX", "LIGHTGREEN_EX",
                              "LIGHTMAGENTA_EX", "LIGHTRED_EX", "LIGHTWHITE_EX", "LIGHTYELLOW_EX"]

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

    def prettify(self, start=None, end=None):
        """Prints a "pretty" version of the conversation history"""
        BaseConvoReader._assert_dates(start, end)
        if start is not None:
            start = CustomDate.from_date_string(start)
            assert start.date >= self.convo[0][2].date, \
                "Your conversations only begin after {0}".format(self.convo[0][2].full_date)
            start = CustomDate.bsearch_index(self.convo, start, key=lambda x: x[2])
        else:
            start = 0
        if end is not None:
            end = CustomDate.from_date(CustomDate.from_date_string(end) + 1)
            assert end.date <= self.convo[-1][2].date,\
                "Your conversations ends on {0}".format(self.convo[-1][2].full_date)
            end = CustomDate.bsearch_index(self.convo, end, key=lambda x: x[2])
        else:
            end = len(self.convo)

        # for person, msg, date in self.convo:
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
            msgs_freq = self._raw_msgs_graph(contact)
            BaseConvoReader._assert_dates(start, end)
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
        by_weekday = self._raw_msgs_by_weekday()
        for day, freq in enumerate(by_weekday):
            print("{0}: {1}%".format(CustomDate.days_of_week[day], str(freq * 100)[:5]))
        print()

    def msgs_by_time(self, window=60, contact=None, threshold=None):
        """Prints to the screen a graphical result of msgs_by_time
        Parameters:
            window (optional): The length of each bin in minutes (default, 60 minutes, or 1 hour)
            contact (optional): The contact you are interested in. (default, all contacts)
            threshold (optional): The minimum threshold needed to print one '#'
        """
        try:
            frequencies = self._raw_msgs_by_time(window, contact)
        except AssertionError as e:
            print(e)
            return

        if threshold is None:
            threshold = window / 120
        else:
            try:
                assert threshold > 0, "Threshold must be a positive number"
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

        os.makedirs(self.path[0:-1], exist_ok=True)
        for person, counter in self.individual_words.items():
            split = person.split()
            pers = ''
            for i in range(len(split) - 1):
                pers += split[i]
                pers += '-'
            pers += split[-1]
            with open(self.path + pers + '_word_freq.txt', mode='w', encoding='utf-8') as f:
                lst = []
                for key, val in counter.items():
                    lst.append((key, val))
                for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
                    f.write("{0}: {1}".format(key, val) + "\n")
        count = Counter()
        for key, val in self.individual_words.items():
            count += val
        with open(self.path + 'total.txt', mode='w', encoding='utf-8') as f:
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
                    if 'Name' in self.preferences[person]:
                        # is the name quality in our preferences?
                        try: # if so we try to use it. Must put in a try statement
                            # in case we have bad values (as in a user modified the file)
                            print(eval('Fore.{0}'.format(self.preferences[person]['Name'])) + "{0}) {1}"
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
                # Colorama choices supported are (https://pypi.python.org/pypi/colorama)
                # see self.color_choices
                options = ["Name", "Message", "Date"]
                print()
                for i, option in enumerate(options):
                    print("{0}) {1}".format(str(i + 1), option))
                value_conditional = True
                print('\nSelect your attribute')
                while value_conditional:
                    value_choice = input("> ")
                    value_conditional = value_choice not in [str(i) for i in range(1, 4)]

                color = self._pick_color(choice)
                self.preferences[self.people[choice - 1]][options[int(value_choice) - 1]] = self.COLOR_CHOICES[color]

        print('Would you like to save your preferences? [Y/n]: ', end="")
        should_save = input()
        while should_save.lower() != 'y' and should_save.lower() != 'yes' \
                and should_save.lower() != 'n' and should_save.lower() != 'no':
            should_save = input('[Y/n]: ')
        if should_save.lower() in ['yes', 'y']:
            self.save_preferences()

    def save_preferences(self):
        os.makedirs(self.path[0:-1], exist_ok=True)
        with open(self.path + 'preferences.txt', mode='w', encoding='utf-8') as f:
            f.write(repr(self.preferences))

    def find(self, query, ignore_case=False, regex=False):
        """Prints to the console the results of searching for the query string
            Parameters:
                ignore_case (optional): Whether the query string is case sensitive
                regex (optional): Whether the query is a regular expression to be fully matched
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

    def times(self, query, ignore_case=False, regex=False):
        """Returns the number of times a message matching the query string occurs in the conversation
            Parameters:
                ignore_case (optional): Whether the query string is case sensitive
                regex (optional): Whether the query is a regular expression to be fully matched
        """

        indexes = self._match_indexes(query, ignore_case=ignore_case) if regex \
            else self._find_indexes(query, ignore_case=ignore_case)
        return len(indexes)

    @staticmethod
    def get_emoji(text):
        """Returns the emoji corresponding to the src value passed,
        or the string passed if appropriate emojis isn't found
        """
        return emojis.src_to_emoiji(text)

    def _raw_convo_starter(self):
        """Percent of time each person starts the conversation according to a threshold number of minutes passed"""
        threshold = 4 * 60  # 4 hours worth of minutes
        convo_start_freq = Counter()
        for person in self.people:
            convo_start_freq[person] = 0
        for i in range(self.len):
            curr_date = self.convo[i][2]
            prev_date = self.convo[i - 1][2]
            if curr_date.distance_from(prev_date) > threshold:
                convo_start_freq[self.convo[i][0]] += 1
        return convo_start_freq

    def _pick_color(self, choice):
        color = None
        while color not in [str(i) for i in range(len(self.COLOR_CHOICES))]:
            print("The following are color choices for the ForeGround for {0}:"
                  .format(self.people[choice - 1]))
            print()
            for i in range(len(self.COLOR_CHOICES)):
                print(eval('Fore.{0}'.format(self.COLOR_CHOICES[i])) + '{0}) {1}'
                      .format(i, self.COLOR_CHOICES[i]))
            color = input('\nSelect your option\n> ')
        return int(color)

    def _load_preferences(self):
        try:
            with open(self.path + 'preferences.txt', mode='r', encoding='utf-8') as f:
                return eval(f.read())
        except FileNotFoundError:
            return {person: dict() for person in self.people}

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
        if person not in self.preferences:
            print(person.title() + ":" + padding + msg + " | " + str(date))
            return
        if 'Name' in self.preferences[person]:
            try:
                print(eval('Fore.{0}'.format(self.preferences[person]['Name'])) + person.title(),
                      end=": " + padding)
            except AttributeError:
                print(person.title(), end=": " + padding)
        else:
            print(person.title(), end=": " + padding)
        if 'Message' in self.preferences[person]:
            try:
                print(eval('Fore.{0}'.format(self.preferences[person]['Message'])) + msg, end="")
            except AttributeError:
                print(msg, end="")
        else:
            print(msg, end="")
        if 'Date' in self.preferences[person]:
            try:
                print( " | " + eval('Fore.{0}'.format(self.preferences[person]['Date'])) + str(date))
            except AttributeError:
                print(" | " + str(date))
        else:
            print(" | " + str(date))

    def _set_path(self):
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

        return name + '/'

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
