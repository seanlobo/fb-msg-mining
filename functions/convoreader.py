from collections import Counter
import inspect
import os
import re
import subprocess
from colorama import init, Fore, Back, Style


from functions.baseconvoreader import BaseConvoReader
from functions.wordcloud import WordCloud
from functions.customdate import CustomDate
import functions.emojis as emojis
from functions.setup_functions import clear_screen


init(autoreset=True)


class ConvoReader(BaseConvoReader):
    def __init__(self, convo_name: str, convo_list: list):
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

        self._preferences = self._load_preferences()
        # preferences_choices = {'personal': {"Name": val, "Message": val, "Date" : val},
        #                        'global': {'new_convo_time': val} }
        self._COLOR_CHOICES = ["BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE",
                              "LIGHTBLACK_EX", "LIGHTBLUE_EX", "LIGHTCYAN_EX", "LIGHTGREEN_EX",
                              "LIGHTMAGENTA_EX", "LIGHTRED_EX", "LIGHTWHITE_EX", "LIGHTYELLOW_EX"]

    def print_people(self):
        """Prints to the screen an alphabetically sorted list of people
        in the conversation
        """
        res = ""
        for i, pers in enumerate(self._people):
            res += "{0}) {1}\n".format(i + 1, pers.title())
        print(res)

    def messages(self, name=None):
        """Prints to the console the number of messages sent for people in the chat
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_messages(name)
        title_case_values = Counter({key.title(): val for key, val in value.items()})
        if type(value) is int:
            print(value)
        else:
            self.print_counter(title_case_values)
        print('Total: {0}'.format(sum(val for key, val in value.items())))

    def words(self, name=None):
        """Prints to the console the number of words sent by each person
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_words(name)
        title_case_values = Counter({key.title(): val for key, val in value.items()})
        if type(value) is int:
            print(value)
        else:
            self.print_counter(title_case_values)
        print('Total: {0}'.format(sum(val for key, val in value.items())))

    def ave_words(self, name=None):
        """Prints to the console the average number of words / message each person in the conversation uses
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_ave_words(name)
        if isinstance(value, int) or isinstance(value, float):
            print(value)
        else:
            for person, msgs in value.most_common():
                print("{0}: {1}".format(person, msgs))
        print()

    def emojis(self, person=None, limit=None):
        """Prints the rankings of emojis for this conversation. Can specify a limit for number of emojis to print, and
        a single individual to count emojis for (default is everyone's aggregate total)
        Parameters:
            person (optional): A string representing the person whose emojis you would like to analyze
            limit (optional): an integer representing the number of entries to print
        """
        ranking = self.raw_emojis(person=person)
        try:
            self.print_counter(ranking, limit=limit)
        except AssertionError as e:
            print(e)
            return

    def characters(self, person=None, limit=None):
        """Prints the rankings of characters for this conversation. Can specify a limit for number of characters
         to print, and a single individual to count charactesr for (default is everyone's aggregate total)
            Parameters:
                person (optional): A string representing the person whose characters you would like to analyze
                limit (optional): an integer representing the number of entries to print
            """
        ranking = self.raw_characters(person=person)
        try:
            self.print_counter(ranking, limit=limit)
        except AssertionError as e:
            print(e)
            return

    def frequency(self, person=None, word=None, limit=True):
        """Prints to the console the frequency that people in this chat use various words. Can be used
        to search for specific words and/ or people.
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

    def word_clouds(self, **preferences):
        """Interactive method for users to set preferences for word cloud generation. Utilizes the java library Kumo
             -------------------------------------
        ---> | https://github.com/kennycason/kumo | <--- Good stuff
             -------------------------------------

         Accepts keyword arguments, all optional.
         Parameters:
            type                      -  A string representing the type of word cloud. Must be from
                                         WorldCloud.WORD_CLOUD_TYPES
                                           e.g. type="circular"
            output_name               -  A string representing the output name of the wordcloud picture
                                           e.g. output_name="my_word_cloud.png"
            set_num_words_to_include  -  An integer representing the number of words to be included (1000 is
                                         a reasonable value, but it depends on the dimensions)
                                           e.g. set_num_words_to_include=1000
            min_cutoff_freq           -  An integer specifying the minimum frequency of words to be included

            * Mainly for Circular/ rectangular ones *
            colors      -  A list of rgb colors (each rbg color must be either a list or tuple of length 3)
                            e.g. colors=[ [255,255,0], [0,255,0] ]
            dimensions  -  A list representing the pixel values of the height and width, respectively
                            e.g. dimensions=[100, 100]
        """
        clear_screen()

        # Getting the user's type, this is mandatory
        if 'type' in preferences and preferences['type'] in WordCloud.WORD_CLOUD_TYPES:
            wc_type = preferences['type']
        else:
            wc_type = self._word_cloud_get_from_list('type')

        # Getting the user's output_name for the wordcloud, this is also mandatory
        try:
            if 'output_name' in preferences:
                WordCloud.assert_output_name_for_wc(preferences['output_name'])
                output_name = preferences['output_name']
            else:
                output_name = self._word_cloud_get_one_liner('output_name')
        except AssertionError as e:
            output_name = self._word_cloud_get_one_liner('output_name')

        clear_screen()

        if wc_type == 'circular' or wc_type == 'rectangular':
            # Gets user input for preferences and then calls the setup function
            preferences = self._word_clouds_get_all(['set_num_words_to_include', 'min_cutoff_freq'])
            preferences['output_name'] = output_name
            preferences['type'] = wc_type
            preferences['input_name'] = self._word_cloud_get_from_list('input_name')

            ready = self._setup_new_word_cloud(preferences)
        else:
            raise Exception("Invalid type for wordcloud specified")

        if len(ready) == 0:
            # ready is a dictionary that contains mappings of preference types ('type', 'output_name' etc.) mapped
            # to errors associated with them from checking user values. iff ready is empty is the word cloud created
            self.__start_kumo()
        else:
            return ready

    def prettify(self, mode=None, **kwargs):
        """Prettily prints messages to the screen in 3 different modes
        Parameters:
            mode: If not one of the below, prints this docstring to the screen
            1) mode="num"
                    start (int) - Start index of messages to print
                    end   (int) - End index of messages to print
                    if start or end is left out, prints from beginning or to end, respectively
            2) mode="date"
                    start (string) - Start date to print from, in form {month}/{day}/{year}
                    end   (string) - End date to print from, same form
                    if start or end is left out, prints from beginning or to end, respectively
            3) mode="clusters"
                    centers (List<int>) - A list of indexes corresponding to the centers
                        of message clusters to be printed
                    padding    (int)    - The amount of padding each center should get
        Usage:
            prettify() # To get help
            prettify(mode="num", start=15000, end=16500) # print messages 15,000 through 16,500
            prettify(mode="date", start='2/24/16', end='3/16/16') # prints messages between February 24th, 2016
                                                                  # and March 16th, 2016
            prettify(mode="clusters", centers=[100, 17690, 100031], padding=300)
                        # prints messages 0-400, 17,390-17,990 and 99,731-100,331
        """
        if mode == "num":
            start = kwargs['start'] if 'start' in kwargs else None
            end = kwargs['end'] if 'end' in kwargs else None
            self._print_messages(start, end)
            return
        elif mode == "date":
            start = kwargs['start'] if 'start' in kwargs else None
            end = kwargs['end'] if 'end' in kwargs else None
            self._print_message_dates(start, end)
            return
        elif mode == "clusters":
            assert "centers" in kwargs, "When calling prettify wtih mode=\"clusters\" " \
                                        "you must pass in a centers argument"
            centers = kwargs["centers"]
            padding = kwargs['padding'] if 'padding' in kwargs else None
            self._print_selected_messages(centers, padding=padding)
            return
        else:
            print(Fore.LIGHTGREEN_EX + "Usage of prettify() is shown below")
            print(Fore.WHITE + inspect.getdoc(self.prettify))
            print()
            return

    def set_time_threshold(self, threshold: int):
        """Sets a new value for threshold, the number of minutes that signify a break in a conversation"""
        try:
            assert isinstance(threshold, int), "threshold should be an integer, not a {0}".format(type(threshold))
            assert threshold > 0, "threshold should be greater than 0 minutes"
        except AssertionError as e:
            print(e)
            return
        # Making sure user input is good
        self._preferences['global']['threshold'] = threshold

    def msgs_graph(self, contact=None, start=None, end=None, forward_shift=0):
        """Prettily prints to the screen the message history of a chat; a bar graph of date / number of messages
        Parameter:
            contact (optional): the name (as a string) of the person you are interested in.
                (default: all contacts)
            start (optional): the date to start the graph from. Defaults to the date of the first message
            end (optional): the date to end the graph with. Defaults to the last message sent
            forward_shift (optional): The number of minutes past 12:00am that are counted as part of the previous day
        """
        try:
            msgs_freq = self._raw_msgs_graph(contact, forward_shift)
            CustomDate.assert_dates(start, end)
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
        """Prints out chat frequency by day of week"""
        by_weekday = self._raw_msgs_by_weekday()
        for day, freq in enumerate(by_weekday):
            print("{0}: {1}%".format(CustomDate.WEEK_INDEXES_TO_DAY_OF_WEEK[day], str(freq * 100)[:5]))
        print()

    def msgs_by_time(self, window: int=60, contact: str=None, threshold: int=None):
        """Prints to the screen a graphical result of message frequency by time of day; a bar graph with
        % of total messages sent by intervals throughout the day
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

    def set_preferences(self):
        """Allows users to set the preferences of this chat, such as color for printing output"""

        # The following idea is used in this method
        # >>> black = 'BLACK'
        # >>> Fore.BLACK
        # '\x1b[30m'
        # >>> eval('Fore.{0}'.format(black))
        # '\x1b[30m'
        # >>>

        choice = None
        while choice != -1:
            while choice not in [str(ele) for ele in range(-1, len(self._people) + 1)]:
                print('\n-1) Cancel/Finish preferences')
                print(' 0) View current preferences\n')

                max_len = len(str(len(self._people))) + 1
                for i, person in enumerate(self._people):
                    if 'Name' in self._preferences[person]:
                        # is the name quality in our preferences?
                        try: # if so we try to use it. Must put in a try statement
                            # in case we have bad values (as in a user modified the file)
                            print(eval('Fore.{0}'.format(self._preferences[person]['Name'])) + "{0}) {1}"
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
                print(self._preferences)
            elif choice in range(1, len(self._people) + 1):
                # Colorama choices supported are (https://pypi.python.org/pypi/colorama)
                # see self.COLOR_CHOICES
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
                self._preferences[self._people[choice - 1]][options[int(value_choice) - 1]] = self._COLOR_CHOICES[color]

        print('Would you like to save your preferences? [Y/n]: ', end="")
        should_save = input()
        while should_save.lower() != 'y' and should_save.lower() != 'yes' \
                and should_save.lower() != 'n' and should_save.lower() != 'no':
            should_save = input('[Y/n]: ')
        if should_save.lower() in ['yes', 'y']:
            self.save_preferences()

    def save_preferences(self):
        """Saves user preferences by writing them to the file "preferences.txt" in user's data folder"""
        if os.path.isfile(self._path + 'preferences.txt'):
            print(Fore.LIGHTBLACK_EX + open(self._path + 'preferences.txt').read())
            print("Previous preferences have been found (printed above), "
                  "are you sure you would like to override them? [Y/n]")
            if user_says_yes():
                return
        os.makedirs(self._path[0:-1], exist_ok=True)
        with open(self._path + 'preferences.txt', mode='w', encoding='utf-8') as f:
            f.write(repr(self._preferences))

    def find(self, query: str, ignore_case=False, regex=False):
        """Prints to the console every message that contains (or matches, if regex=True) the query string
            Parameters:
                query: The string query searched for
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

    def times(self, query: str, ignore_case=False, regex=False):
        """Returns the number of times a message matching the query string occurs in the conversation
            Parameters:
                query: The string query searched for
                ignore_case (optional): Whether the query string is case sensitive
                regex (optional): Whether the query is a regular expression to be fully matched
        """

        indexes = self._match_indexes(query, ignore_case=ignore_case) if regex \
            else self._find_indexes(query, ignore_case=ignore_case)
        return len(indexes)

    def help(self):
        """Method to give users help / tips on how to use ConvoReaders"""
        clear_screen()
        print("Welcome to the help function for ConvoReader\n\n")

        print('Below is a list of the most important data-analyzing functions you can perform on conversations.')
        print('Select one of the following to view more details')

        # The methods I think are the most important to explain
        most_important = [ConvoReader.find, ConvoReader.frequency, ConvoReader.prettify, ConvoReader.print_people,
                          ConvoReader.msgs_graph, ConvoReader.save_word_freq, ConvoReader.set_preferences,
                          ConvoReader.word_clouds]

        secondary = [ConvoReader.ave_words, ConvoReader.emojis, ConvoReader.messages,
                     ConvoReader.msgs_by_time, ConvoReader.msgs_by_weekday, ConvoReader.times, ConvoReader.words]
        while True:
            print('\n0) Exit\n')

            # Prints out each of the methods
            print("The most important methods (in my opinion)")
            len_longest_str = len(str(len(most_important) + len(secondary)))
            for i, method in enumerate(most_important):
                method_name = color_method(method.__name__)
                print('{0}){1}{2}'.format(str(i + 1), ' ' * (len_longest_str - len(str(i + 1)) + 1), method_name))

            # Secondary methods
            print('\nSome more methods that might be useful')
            for i, method in enumerate(secondary):
                method_name = color_method(method.__name__)
                print('{0}){1}{2}'.format(str(i + 1 + len(most_important)),
                                          ' ' * (len_longest_str - len(str(i + 1 + len(most_important))) + 1),
                                          method_name))

            print('\nSelect your choice')
            while True:
                choice = input('> ')
                if choice in [str(i) for i in range(len(most_important) + len(secondary) + 1)]:
                    break
            # above get's user's choice of method

            # if the user wants to exit let them
            choice = int(choice) - 1
            if choice == -1:
                return

            if choice >= len(most_important):
                choice -= len(most_important)
                methods = secondary
            else:
                methods = most_important

            print('\n')

            if 'return' in methods[choice].__annotations__:
                # in the form '(self, person=None) -> collections.Counter'
                annotation = str(inspect.signature(methods[choice]))
                # the part of the annotation up until the signature ends
                end_method = annotation.find(' ->')
                name = color_method(methods[choice].__name__ + annotation[:end_method])
                name += color_method(annotation[end_method:])
            else:
                name = color_method(methods[choice].__name__ + str(inspect.signature(methods[choice])))

            print(name)
            print(inspect.getdoc(methods[choice]))

            print()

            print("View help again? [Y/n] ")
            again = user_says_yes()

            if not again:
                return

            clear_screen()

    @staticmethod
    def get_emoji(text: str) -> str:
        """Returns the emoji corresponding to the src value passed,
        or the string passed if appropriate emojis isn't found
        """
        return emojis.src_to_emoiji(text)

    @staticmethod
    def print_counter(counter, limit=None):
        """Prints the ranking of a counter object to the console, stopping at limit if it is an integer.
        """
        if limit is not None:
            assert isinstance(limit, int), "Limit must be an integer"
            assert limit > 0, "Now it'd be pretty boring if we printed 0 (or fewer!) elements, wouldn't it? " \
                              "(limit must be > 0)"
        else:
            limit = len(counter)
        values = counter.most_common()
        MAX_LENGTH = len(str(limit)) + 1
        for i in range(1, limit + 1):
            print("{0}){1}{2}   - ({3})".format(i,
                                                ' ' * (MAX_LENGTH - len(str(i))),
                                                values[i - 1][0],
                                                values[i - 1][1]))

    def _pick_color(self, person: int) -> int:
        """Helper method to get user input for picking a color of text
        Parameters:
            person: the index + 1 of self._people corresponding to the user
            specified person whose settings are being modified
        """
        color = None
        while color not in [str(i) for i in range(len(self._COLOR_CHOICES))]:
            print("The following are color choices for the ForeGround for {0}:"
                  .format(self._people[person - 1]))
            print()
            for i in range(len(self._COLOR_CHOICES)):
                print(eval('Fore.{0}'.format(self._COLOR_CHOICES[i])) + '{0}) {1}'
                      .format(i, self._COLOR_CHOICES[i]))
            color = input('\nSelect your option\n> ')
        return int(color)

    def _load_preferences(self):
        """Searches for preferences.txt in the data folder and loads data if file exists and is clean"""
        try:
            with open(self._path + 'preferences.txt', mode='r', encoding='utf-8') as f:
                preferences = eval(f.read())
                good = False  # Are the preferences good
                try:
                    assert isinstance(preferences, dict), "Please don\'t modify any files in /data/"
                    for person in self._people:
                        assert person in preferences, "{0} is missing from preferences".format(person)
                    assert 'global' in preferences and 'threshold' in preferences['global'],\
                        "You are missing global parameters in preferences"
                    good = True
                except AssertionError as e:
                    print(e)
                # Clean data, making sure loaded preferences are actually in the format we expect

                if good:
                    return preferences
                else:
                    print('To get rid of this warning either execute \"save_preferences()\", or figure out what the '
                          'issue is in {0} and fix that'.format(self._path + 'preferences.txt'))
                # returning the preferences read from the file IF it is good
                # OTHERWISE passes on to return a default version

        except FileNotFoundError:
            pass
        except Exception as e:
            print("A {0} error was encountered when loading preferences: {1}".format(e, str(e)))
            print('\nThis most likely means you have modified the preferences.txt file in {0}'.format(self._path))
            print('To get rid of this warning, execute the command \"save_preferences()\"')

        # Only executes if an exception occured or an assertion was raised
        print("Using default settings")
        preferences = {person: dict() for person in self._people}
        preferences['global'] = dict(threshold=240)
        return preferences

    def _print_message(self, number: int):
        """Helper method used to prettily print to the screen the person, message and date
        corresponding to the passed parameter number
        Parameter:
            number: The message number to print, must be 0 < num < len(self)
        """
        try:
            assert type(number) is int, "number must be an integer"
            assert number in range(len(self._convo)), "number must be in range({0})".format(len(self._convo))
        except AssertionError as e:
            raise e

        person, msg, date = self._convo[number]
        # the length of the longest name in self.people
        max_len = len(max(self._people, key=lambda name: len(name)))
        padding = ' ' * (max_len - len(person))
        if person not in self._preferences:
            print(person.title() + ":" + padding + msg + " | " + str(date))
            return
        if 'Name' in self._preferences[person]:
            try:
                print(eval('Fore.{0}'.format(self._preferences[person]['Name'])) + person.title(),
                      end=": " + padding)
            except AttributeError:
                print(person.title(), end=": " + padding)
        else:
            print(person.title(), end=": " + padding)
        if 'Message' in self._preferences[person]:
            try:
                print(eval('Fore.{0}'.format(self._preferences[person]['Message'])) + msg, end="")
            except AttributeError:
                print(msg, end="")
        else:
            print(msg, end="")
        if 'Date' in self._preferences[person]:
            try:
                print( " | " + eval('Fore.{0}'.format(self._preferences[person]['Date'])) + str(date))
            except AttributeError:
                print(" | " + str(date))
        else:
            print(" | " + str(date))

    def _print_messages(self, start=None, end=None):
        """Prints to the screen the messages between start and end
        Parameters:
            start: The start index
            end: The end index
        """
        start = 0 if start is None else start
        end = len(self) - 1 if end is None else end
        try:
            assert isinstance(start, int), "Start needs to be an integer"
            assert isinstance(end, int), "End needs to be an integer"
            assert 0 <= start < len(self), "Start needs to be between 0 and {0}".format(len(self))
            assert 0 <= end < len(self), "End needs to be between 0 and {0}".format(len(self))
            assert start <= end, "End should be greater than or equal to start"
        except AssertionError as e:
            print(str(e))
            return
        # Making sure user input is good

        MAX_LEN_INDEX = len(str(end)) + 2
        for i in range(start, end):
            if self._convo[i - 1][2].distance_from(self._convo[i][2]) < -self._preferences['global']['threshold']:
                print()
            print(str(i) + ' ' * (MAX_LEN_INDEX - len(str(i))), end="")
            self._print_message(i)

    def _print_selected_messages(self, *args, padding=None):
        """Prints to the screen all message numbers in args padded by padding amount
        Parameters:
            *args: An arbitrary number of integers representing conversation #s to view
            padding (optional): The number of messages to pad each query by
        """

        def get_range(center, padding):
            """Returns a range object with a padded center, and with a minimum of 0 and maximum of len(self)"""
            assert isinstance(center, int), "Center needs to be an integer"
            assert isinstance(padding, int), "Padding neesd to be an integer"
            assert 0 <= center < len(self), "Passed value must be between 0 and {0}".format(len(self))
            assert padding >= 0, "Padding needs to be greater than or equal to 0"
            return range(max(0, center - padding), min(len(self), center + padding + 1))

        padding = 5 if padding is None else padding

        start_end_ranges = [get_range(num, padding) for num in args]
        MAX_LEN_INDEX = len(str(max(start_end_ranges, key=lambda x: len(str(x.stop))).stop)) + 1

        for start_end in start_end_ranges:
            for i in start_end:
                print(str(i) + ' ' * (MAX_LEN_INDEX - len(str(i))), end="- ")
                self._print_message(i)
            print('\n')

    def _print_message_dates(self, start=None, end=None):
        """Prints a "pretty" version of the conversation history"""
        try:
            CustomDate.assert_dates(start, end)
        except AssertionError as e:
            print(e)
            return
        # verifying user dates are correct form

        if start is not None:
            start = CustomDate.from_date_string(start)
            assert start.date >= self._convo[0][2].date, \
                "Your conversations only begin after {0}".format(self._convo[0][2].full_date)
            start = CustomDate.bsearch_index(self._convo, start, key=lambda x: x[2])
        else:
            start = 0
        if end is not None:
            end = CustomDate.from_date(CustomDate.from_date_string(end) + 1)
            assert end.date <= self._convo[-1][2].date, \
                "Your conversations ends on {0}".format(self._convo[-1][2].full_date)
            end = CustomDate.bsearch_index(self._convo, end, key=lambda x: x[2])
        else:
            end = len(self._convo)

        MAX_LEN_INDEX = len(str(end)) + 2
        for i in range(start, end):
            print(str(i) + ' ' * (MAX_LEN_INDEX - len(str(i))), end="")
            self._print_message(i)

    def __start_kumo(self):
        """Calls the java program, assuming that all conditions are met"""
        # grabbed from http://stackoverflow.com/questions/438594/how-to-call-java-objects-and-functions-from-cpython
        # with additions by http://stackoverflow.com/questions/11269575/how-to-hide-output-of-subprocess-in-python-2-7k
        devnull = open(os.devnull, mode='w')
        p = subprocess.Popen("java -jar data/wordclouds.jar", shell=True, stdout=devnull, stderr=subprocess.STDOUT)
        sts = os.waitpid(p.pid, 0)

    def _word_clouds_get_all(self, values):
        choices = sorted(values)
        res = dict()
        while True:
            print("Now selecting more specific features. Below are your preferences:")
            num_choices_max_length = len(str(len(choices)))
            print("{0}){1}Exit".format(0, ' ' * num_choices_max_length))
            for i in range(1, len(choices) + 1):
                print("{0}){1}{2} = {3}".format(i, ' ' * (num_choices_max_length + 1 - len(str(i))),
                                                choices[i - 1], res[choices[i - 1]] if choices[i - 1] in res
                                                else 'DEFAULT SETTINGS'))
            print()
            print("Choose which feature you would like to specify:")

            choice_range = [str(i) for i in range(len(choices) + 1)]
            while True:
                choice = input('> ')
                if choice in choice_range:
                    choice = int(choice) - 1
                    print()
                    break

            if choice == -1:  # User wants to exit
                print("Are you sure you would like to exit?")
                if user_says_yes():
                    clear_screen()
                    return res
            else:  # user continues selecting preferences
                user_choice = self._word_cloud_get_one_liner(choices[choice])
                res[choices[choice]] = user_choice

                print("Would you like to continue choosing preferences?")
                if not user_says_yes():  # Does the user want to quit?
                    clear_screen()
                    return res
            clear_screen()

    def _word_cloud_get_one_liner(self, attribute):
        if attribute == 'output_name':
            intro = "What name would you like for the output wordcloud file? It must end in '.png' and can't have spaces"
            assertion = WordCloud.assert_output_name_for_wc
            assertion_failure_string = '\nplease try again. Remember to end the name in \".png\", for example ' \
                                       '\"example.png\"'
        elif attribute == 'set_num_words_to_include':
            intro = "How many words would you like to include (at maximum) in your word cloud? Type an integer"
            assertion = lambda x: WordCloud.assert_num_words_to_include(int(x))
            assertion_failure_string = "Please try again, type an integer"
        elif attribute == 'min_cutoff_freq':
            intro = "What's the length of the smallest word you would like to include in the wordcloud?"

            def assertion(x):
                assert int(x) > 0, "X must be an integer greater than 0"

            assertion_failure_string = "Please try again, type an integer"
        else:
            raise ValueError("invalid value of attribute passed")
        while True:
            print(intro)
            name = input('> ')
            passed_assertion = False
            try:
                assertion(name)
                passed_assertion = True
            except Exception as e:
                print(e)
                print(assertion_failure_string)
            if passed_assertion:
                print("Would you like to confirm \"{0}\" as your {1}? [Y/n]".format(name, attribute))
                if user_says_yes():
                    if attribute == 'set_num_words_to_include' or attribute == 'min_cutoff_freq':
                        name = int(name)
                    return name

    def _word_cloud_get_from_list(self, attribute):
        if attribute == 'type':
            intro = "What type of word cloud would you like? Chose one from the following:"
            lst_of_choices = WordCloud.WORD_CLOUD_TYPES
        elif attribute == 'input_name':
            intro = "Which of the following files would you like to use for the word cloud?"

            def name_to_file(name):
                # Based on save_word_freq in baseconvoreader
                file_name = ""
                for part in name.split():
                    file_name += part + '-'
                file_name = file_name[:-1]
                return file_name + '_word_freq.txt'

            lst_of_choices = list(map(name_to_file, self.get_people())) + ['total.txt']
        else:
            raise ValueError("Invalid value of attribute")
        print(intro)
        # length of the string for the highest choice number
        num_choices_max_length = len(str(len(lst_of_choices)))
        for i in range(1, len(lst_of_choices) + 1):
            print("{0}){1}{2}".format(i, ' ' * (num_choices_max_length + 1 - len(str(i))),
                                      lst_of_choices[i - 1]))
        print()
        print("Choose which number you would like (between 1 and {0})".format(len(lst_of_choices)))
        choice_range = [str(i) for i in range(1, len(lst_of_choices) + 1)]
        while True:
            choice = input('> ')
            if choice in choice_range:
                return lst_of_choices[int(choice) - 1]

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
        return "Converation for " + self._name.title()

    def __repr__(self):
        """Returns a valid constructor for this object"""
        return "ConvoReader({0}, {1})".format(repr(self._name), repr(self._convo))


def color_method(string: str) -> str:
    """Colors a function call passed with one color, making the arguments / parameters another"""
    OUTER_CODE_COLOR = Fore.LIGHTGREEN_EX
    INNER_CODE_COLOR = Fore.CYAN

    result = "" + Back.BLACK

    if '(' in string:
        result += OUTER_CODE_COLOR + string[:string.find('(') + 1]
        result += INNER_CODE_COLOR + string[string.find('(') + 1:-1]
        result += OUTER_CODE_COLOR + ')' + Style.RESET_ALL
    else:
        result += INNER_CODE_COLOR + string + Style.RESET_ALL
    return result


def user_says_yes():
    """Returns True if the user types 'y' or 'yes' and False for 'no', 'n (ignoring case)'"""
    while True:
        choice = input('> ').lower()
        if choice in ['y','yes']:
            return True
        elif choice in ['no', 'n']:
            return False
