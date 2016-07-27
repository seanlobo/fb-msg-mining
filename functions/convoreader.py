from collections import Counter
import inspect
import os
import re
import subprocess
import copy
from colorama import init, Fore, Back, Style


from functions.baseconvoreader import BaseConvoReader
from functions.wordcloud import WordCloud
from functions.customdate import CustomDate
import functions.emojis as emojis
from functions.setup_functions import clear_screen, one_line, user_says_yes, color_method


init(autoreset=True)


class ConvoReader(BaseConvoReader):
    _CANCEL_WC_PREFERENCE = 'cancel'

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

    # -----------------------------------------------   PUBLIC METHODS ---------------------------------------------- #

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
        if type(value) is int:
            print('{:,}'.format(value))
            return
        else:
            title_case_values = Counter({key.title(): val for key, val in value.items()})
            self.print_counter(title_case_values)
            print('Total: {0:,}'.format(sum(val for key, val in value.items())))
            return

    def words(self, name=None):
        """Prints to the console the number of words sent by each person
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_words(name)
        if type(value) is int:
            print('{:,}'.format(value))
            return
        else:
            title_case_values = Counter({key.title(): val for key, val in value.items()})
            self.print_counter(title_case_values)
            print('Total: {0:,}'.format(sum(val for key, val in value.items())))
            return

    def ave_words(self, name=None):
        """Prints to the console the average number of words / message each person in the conversation uses
        Parameters:
            name (optional): The name (as a string) of the person you are interested in
        """
        value = self._raw_ave_words(name)
        if isinstance(value, int) or isinstance(value, float):
            print('{:,}'.format(value))
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

    def conversation_starters(self, threshold=240, max_decimal_places=2):
        """Prints to to console the frequency that all members of this conversation start conversations, where starting
        a conversation is defined as being the first to send a message after at least {threshold} minutes
        Parameter:
            threshold (optional): the number of minutes of inactivity that signal the start of a new conversation.
                                  defaults to 240 minutes, or 4 hours.
            max_decimal_places (optional): the number of decimal places to print out (at maximum). Default is 2
        """
        frequencies = self.raw_convo_starter_freqs(threshold)
        self.print_counter(frequencies, mode='freq', percent_length= max_decimal_places + 3)

    def conversation_killers(self, threshold=240, max_decimal_places=2):
        """Prints to to console the frequency that all members of this conversation kill conversations, where killing
        a conversation is defined as being the last to send a message for at least {threshold} minutes after
        Parameter:
            threshold (optional): the number of minutes of inactivity that signal the start of a new conversation.
                                  defaults to 240 minutes, or 4 hours.
            max_decimal_places (optional): the number of decimal places to print out (at maximum). Default is 2
        """
        frequencies = self.raw_convo_killer_freqs(threshold)
        self.print_counter(frequencies, mode='freq', percent_length=max_decimal_places + 3)

    def word_clouds(self, **preferences):
        """Interactive method for users to set preferences for word cloud generation. Utilizes the java library Kumo
             -------------------------------------
        ---> | https://github.com/kennycason/kumo | <--- Good stuff
             -------------------------------------

         Accepts keyword arguments, all optional.
         Parameters:
            shape                     -  A string representing the shape of word cloud. Must be from
                                         WorldCloud.WORD_CLOUD_SHAPES
                                           e.g. shape="circular"
            output_name               -  A string representing the output name of the wordcloud picture
                                           e.g. output_name="my_word_cloud.png"
            num_words_to_include      -  An integer representing the number of words to be included (1000 is
                                         a reasonable value, but it depends on the dimensions)
                                           e.g. set_num_words_to_include=1000

            * Mainly for Circular/ rectangular ones *
            colors      -  A list of rgb colors (each rbg color must be either a list or tuple of length 3)
                            e.g. colors=[ [255,255,0], [0,255,0] ]
            dimensions  -  A list representing the pixel values of the height and width, respectively
                            e.g. dimensions=[100, 100]
        """
        clear_screen()
        WordCloud.setup_word_cloud_starter_files()

        if 'type' in preferences and preferences['type'] in WordCloud.WORD_CLOUD_TYPES:
            wc_type = preferences['type']
        else:
            wc_type = self._get_type()

        word_cloud_preferences = WordCloud.get_default_preferences(wc_type)
        word_cloud_preferences['type'] = wc_type

        # Filter user preferences by valid responses, adding them to word_cloud_preferences
        if word_cloud_preferences['type'] == 'default':
            options = {
                'num_words_to_include': WordCloud.assert_num_words_to_include,
                'output_name': WordCloud.assert_output_name_for_wc,
                'dimensions': WordCloud.assert_dimensions_for_wc,
                'colors': WordCloud.assert_colors_for_wc,
                'shape': WordCloud.assert_shape_for_wc
            }
        elif word_cloud_preferences['type'] == 'polarity':
            options = {
                'num_words_to_include': WordCloud.assert_num_words_to_include,
                'output_name': WordCloud.assert_output_name_for_wc,
                'dimensions': WordCloud.assert_dimensions_for_wc,
                'color_set_1': WordCloud.assert_colors_for_wc,
                'color_set_2': WordCloud.assert_colors_for_wc,
                'shape': WordCloud.assert_shape_for_wc
            }
        elif word_cloud_preferences['type'] == 'layered':
            options = {
                'num_words_to_include': WordCloud.assert_num_words_to_include,
                'output_name': WordCloud.assert_output_name_for_wc,
                'dimensions': WordCloud.assert_dimensions_for_wc,
            }
        else:
            raise Exception("Invalid shape for wordcloud specified")

        for custom_preference in options.keys():
            if custom_preference in preferences:
                # if the user specified a preference, we run it through the appropriate assertion
                try:
                    options[custom_preference](preferences[custom_preference])
                except AssertionError:
                    pass
                else:
                    word_cloud_preferences[custom_preference] = preferences[custom_preference]

        if word_cloud_preferences['type'] == 'default':
            # The choices a user can specify
            preference_choices = {
                'num_words_to_include': self._get_num_words_to_include,
                'min_word_length': self._get_min_word_length,
                'max_word_length': self._get_max_word_length,
                'min_font_size': self._get_min_font_size,
                'excluded_words': self._get_excluded_words,
                'max_font_size': self._get_max_font_size,
                'output_name': self._get_output_name,
                'image_name': self._get_image_name,
                'input_name': self._get_input_name,
                'dimensions': self._get_dimensions,
                'font_type': self._get_font_type,
                'colors': self._get_colors,
                'shape': self._get_shape,
            }
        elif word_cloud_preferences['type'] == 'polarity':
            preference_choices = {
                'num_words_to_include': self._get_num_words_to_include,
                'min_word_length': self._get_min_word_length,
                'max_word_length': self._get_max_word_length,
                'min_font_size': self._get_min_font_size,
                'excluded_words': self._get_excluded_words,
                'max_font_size': self._get_max_font_size,
                'output_name': self._get_output_name,
                'color_set_1': self._get_colors,
                'color_set_2': self._get_colors,
                'text_set_1': self._get_input_name,
                'text_set_2': self._get_input_name,
                'dimensions': self._get_dimensions,
                'image_name': self._get_image_name,
                'font_type': self._get_font_type,
                'shape': self._get_shape,
            }
        elif word_cloud_preferences['type'] == 'layered':
            print('\n' + one_line() + '\n')

            num_layers = self._get_num_layers()
            text_sets, image_sets, color_sets = self._get_layered_text_image_colors(num_layers)
            word_cloud_preferences['text_sets'] = text_sets
            word_cloud_preferences['image_sets'] = image_sets
            word_cloud_preferences['color_sets'] = color_sets
            preference_choices = {
                'num_words_to_include': self._get_num_words_to_include,
                'min_word_length': self._get_min_word_length,
                'max_word_length': self._get_max_word_length,
                'min_font_size': self._get_min_font_size,
                'excluded_words': self._get_excluded_words,
                'max_font_size': self._get_max_font_size,
                'output_name': self._get_output_name,
                'dimensions': self._get_dimensions,
                'font_type': self._get_font_type,
                'text_sets': lambda previous: self._get_sets(previous, 'text_sets', self._get_input_name),
                'image_sets': lambda previous: self._get_sets(previous, 'image_sets', self._get_image_name),
                'color_sets': lambda previous: self._get_sets(previous, 'color_sets', self._get_colors),
            }
        else:
            raise Exception("Invalid shape for wordcloud specified")

        clear_screen()
        word_cloud_preferences.update(self._get_word_cloud_preferences(preference_choices,
                                                                       previous_choices=word_cloud_preferences))

        ready = self._setup_new_word_cloud(word_cloud_preferences)

        if len(ready) == 0:
            # ready is a dictionary that contains mappings of preference types ('type', 'output_name' etc.) mapped
            # to errors associated with them from checking user values. iff ready is empty is the word cloud created
            self.__start_kumo()
        else:
            print(Fore.LIGHTRED_EX + Back.BLACK + "Word Cloud creation failed due to the following issues:" +
                  Style.RESET_ALL)
            key_vals = [(key, val) for key, val in ready.items()]

            def key(x):
                return len(str(x[0]))
            max_len = key(max(key_vals, key=key)) + 1
            for key, val in key_vals:
                print(key + ' ' * (max_len - len(key)), end=": ")
                print(val)

    def duplicate_word_cloud(self, output_name=None):
        """Creates a new word cloud using the settings of the previous word cloud. Aborts if a previous word
        cloud's settings cannot be found
        Parameters:
            output_name (optional): The output name for the new word cloud
        """
        if output_name is not None:
            try:
                self._word_cloud.set_output_name(output_name)
            except AssertionError as e:
                print(e)
                return

        self.save_word_freq(path=WordCloud.WORD_CLOUD_INPUT_PATH)
        if len(self._word_cloud.verify_word_cloud_setup()) == 0:
            self.__start_kumo()

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
            assert "centers" in kwargs, "When calling prettify with mode=\"clusters\" " \
                                        "you must pass in a centers argument"
            centers = kwargs["centers"]
            padding = kwargs['padding'] if 'padding' in kwargs else None
            self._print_selected_messages(*centers, padding=padding)
            return
        else:
            print(Fore.LIGHTGREEN_EX + "Usage of {0} is shown below"
                  .format(ConvoReader.prettify.__name__ + str(inspect.signature(ConvoReader.prettify))))
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
        print("\nEach \"#\" refers to ~{0} messages".format(value))
        print()

        max_date_len = 12
        # The Maximum length of the string containing the longest date (with padding) i.e. '12/12/2012  '

        max_num_length = len(str(max(msgs_freq, key=lambda x: x[1])[1]))
        # The maximum length of the string containing the largest number of messages in a day i.e. "420"

        for i in range(start_index, end_index):
            day = msgs_freq[i][0].to_string()
            day += ' ' * (max_date_len - len(day))

            msg_num = str(msgs_freq[i][1])
            msg_num += " " * (max_num_length - len(msg_num))

            string = day + msg_num
            if i % 2 == 0:
                print(string + " |", end="")
            else:
                print(max_date_len * " " + msg_num + " |", end="")

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
                        try:  # if so we try to use it. Must put in a try statement
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

                print('\nSelect your attribute')
                value_choice = None
                choice_range = [str(i) for i in range(1, 4)]
                while value_choice not in choice_range:
                    value_choice = input("> ")

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
        max_len_index = len(max(map(str, indexes), key=len)) + 2
        for i in indexes:
            print(str(i) + ' ' * (max_len_index - len(str(i))), end="")
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

    # ----------------------------------------------   PUBLIC METHODS ---------------------------------------------- #

    # --------------------------------------------------   HELP   -------------------------------------------------- #

    @staticmethod
    def help():
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
            print()
            print(Fore.LIGHTRED_EX + Back.BLACK + '0) Exit' + Style.RESET_ALL + '\n')

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

            # get's user's choice of method
            print('\nSelect your choice')
            choice = None
            choice_range = [str(i) for i in range(len(most_important) + len(secondary) + 1)]
            while choice not in choice_range:
                choice = input('> ')

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

    # --------------------------------------------------   HELP   -------------------------------------------------- #

    # ------------------------------------------   PUBLIC STATIC METHODS   ------------------------------------------- #

    @staticmethod
    def get_emoji(text: str) -> str:
        """Returns the emoji corresponding to the src value passed,
        or the string passed if appropriate emojis isn't found
        """
        return emojis.src_to_emoiji(text)

    @staticmethod
    def print_counter(counter, limit=None, mode='raw', percent_length=5):
        """Prints the ranking of a counter object to the console, stopping at limit if it is an integer.
        """
        if limit is not None:
            assert isinstance(limit, int), "Limit must be an integer"
            assert limit > 0, "Now it'd be pretty boring if we printed 0 (or fewer!) elements, wouldn't it? " \
                              "(limit must be > 0)"
        else:
            limit = len(counter)

        assert mode in ['freq', 'raw'], "mode must either be 'raw' or 'freq'"

        values = counter.most_common()
        max_index_length = len(str(limit)) + 1
        lines = [("{0}){1}{2}".format(i, ' ' * (max_index_length - len(str(i))), values[i - 1][0]), values[i - 1][1])
                 for i in range(1, limit + 1)]
        max_line_length = len(max(lines, key=lambda x: len(x[0]))[0]) + 1

        for line in lines:
            print(line[0] + ' ' * (max_line_length - len(line[0])), end='- ')
            if mode == 'raw':
                print("({0:,})".format(line[1]))
            else:
                print("{0}%".format(str(round(line[1], ndigits=percent_length))[:percent_length]))

    # ------------------------------------------   PUBLIC STATIC METHODS   ------------------------------------------- #


    # -----------------------------------------------   PREFERENCES   ------------------------------------------------ #

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

        preferences = {person: dict() for person in self._people}
        preferences['global'] = dict(threshold=240)
        return preferences

    # -----------------------------------------------   PREFERENCES   ------------------------------------------------ #

    # -------------------------------------   PRINTING CONVERSATION TO CONSOLE   ------------------------------------- #

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
                print(" | " + eval('Fore.{0}'.format(self._preferences[person]['Date'])) + str(date))
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

        max_len_index = len(str(end)) + 2
        for i in range(start, end):
            if self._convo[i - 1][2].distance_from(self._convo[i][2]) < -self._preferences['global']['threshold']:
                print()
            print(str(i) + ' ' * (max_len_index - len(str(i))), end="")
            self._print_message(i)

    def _print_selected_messages(self, *args, padding=None):
        """Prints to the screen all message numbers in args padded by padding amount
        Parameters:
            *args: An arbitrary number of integers representing conversation #s to view
            padding (optional): The number of messages to pad each query by
        """

        def get_range(center, padding_amount):
            """Returns a range object with a padded center, and with a minimum of 0 and maximum of len(self)"""
            assert isinstance(center, int), "Center needs to be an integer"
            assert isinstance(padding_amount, int), "Padding neesd to be an integer"
            assert 0 <= center < len(self), "Passed value must be between 0 and {0}".format(len(self))
            assert padding_amount >= 0, "Padding needs to be greater than or equal to 0"
            return range(max(0, center - padding_amount), min(len(self), center + padding_amount + 1))

        padding = 5 if padding is None else padding

        start_end_ranges = [get_range(num, padding) for num in args]
        max_len_index = len(str(max(start_end_ranges, key=lambda x: len(str(x.stop))).stop)) + 1

        for start_end in start_end_ranges:
            for i in start_end:
                print(str(i) + ' ' * (max_len_index - len(str(i))), end="- ")
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
            end = CustomDate.from_date(end).plus_x_days(1)
            assert end.date <= self._convo[-1][2].date, \
                "Your conversations ends on {0}".format(self._convo[-1][2].full_date)
            end = CustomDate.bsearch_index(self._convo, end, key=lambda x: x[2])
        else:
            end = len(self._convo)

        self._print_messages(start=start, end=end)

    # --------------------------------------   PRINTING CONVERSATION TO CONSOLE   ------------------------------------ #

    # -----------------------------------------   WORD CLOUD PRIVATE METHODS   --------------------------------------- #

    @staticmethod
    def __start_kumo():
        """Calls the java program, assuming that all conditions are met"""
        # grabbed from http://stackoverflow.com/questions/438594/how-to-call-java-objects-and-functions-from-cpython
        # with additions by http://stackoverflow.com/questions/11269575/how-to-hide-output-of-subprocess-in-python-2-7k
        # devnull = open(os.devnull, mode='w')
        p = subprocess.Popen("java -jar data/word_clouds/wordclouds.jar", shell=True)
        sts = os.waitpid(p.pid, 0)

    @staticmethod
    def _get_word_cloud_preferences(attributes_to_fns: dict, previous_choices=None):
        """Returns a dictionary mapping preference type strings to their values"""
        attribute_choices = sorted(attributes_to_fns.keys())
        res = previous_choices.copy() if previous_choices is not None else dict()

        default_value_color = Fore.LIGHTGREEN_EX + Back.BLACK
        edited_value_color = Fore.LIGHTMAGENTA_EX + Back.BLACK
        while True:
            print("Now selecting more specific features. Below are your preferences:\n")
            num_choices_max_length = len(str(len(attribute_choices)))
            print(Fore.LIGHTRED_EX + Back.BLACK + "{0}){1}Create Word Cloud".format(0, ' ' * num_choices_max_length))
            for i in range(1, len(attribute_choices) + 1):
                # print("{index}{spaces}{attribute} = {current_value}")

                print(Fore.LIGHTCYAN_EX + Back.BLACK + "{0})".format(i) + Style.RESET_ALL, end="")
                print(' ' * (num_choices_max_length + 1 - len(str(i))), end="")
                print(attribute_choices[i - 1], end=" = ")

                current_value = res.get(attribute_choices[i - 1], 'does not exist')
                if current_value != 'does not exist' \
                        and current_value != previous_choices.get(attribute_choices[i - 1]):
                    print(edited_value_color +
                          str(res[attribute_choices[i - 1]])
                          if attribute_choices[i - 1] in res else 'DEFAULT SETTINGS' + Style.RESET_ALL)
                else:
                    print(default_value_color +
                          str(res[attribute_choices[i - 1]])
                          if attribute_choices[i - 1] in res else 'DEFAULT SETTINGS' + Style.RESET_ALL)
            # Prints out the list of preferences the user currently has

            print()

            print("Choose which feature you would like to specify: [0-{0}]".format(len(attribute_choices)))
            feature_index = get_user_choice_from_range(0, len(attribute_choices)) - 1  # Selects the user's choice

            if feature_index == -1:  # User wants to exit
                print("Are you sure you are done selecting preferences? [Y/n]")
                if user_says_yes():
                    clear_screen()
                    return res
                else:
                    continue
            else:  # continue selecting preferences
                print(one_line() + '\n')
                feature = attribute_choices[feature_index]

                # grabs the user preference associated with the preference from the index user previously specified
                if feature in ['text_sets', 'image_sets', 'color_sets']:
                    new_value = attributes_to_fns[feature](res[feature])
                else:
                    new_value = attributes_to_fns[feature]()

                # applies the new preference if the user did not ask to cancel preferences
                if new_value != ConvoReader._CANCEL_WC_PREFERENCE:
                    res[feature] = new_value
                else:
                    clear_screen()
                    continue
                print()

            print("Would you like to continue choosing preferences? [Y/n]")
            if not user_says_yes():  # Does the user want to quit?
                clear_screen()
                return res
            clear_screen()

    def _get_num_words_to_include(self):
        return self._word_cloud_get_one_liner('num_words_to_include')

    def _get_min_word_length(self):
        return self._word_cloud_get_one_liner('min_word_length')

    def _get_max_word_length(self):
        return self._word_cloud_get_one_liner('max_word_length')

    def _get_input_name(self):
        return self._word_cloud_get_from_list('input_name')

    def _get_output_name(self):
        return self._word_cloud_get_one_liner('output_name')

    def _get_shape(self):
        return self._word_cloud_get_from_list('shape')

    def _get_type(self):
        return self._word_cloud_get_from_list('type')

    def _get_min_font_size(self):
        return self._word_cloud_get_one_liner('min_font_size')

    def _get_max_font_size(self):
        return self._word_cloud_get_one_liner('max_font_size')

    def _get_font_type(self):
        return self._word_cloud_get_from_list('font_type')

    @staticmethod
    def _get_num_layers():
        max_layers = 5
        print("Please type the number of layers you would like to use for your word cloud. " +
              Fore.LIGHTRED_EX + Back.BLACK + "Type an integer between 2 and {0}".format(max_layers) + Style.RESET_ALL)
        while True:
            try:
                value = int(input("> "))
                if value < 2:
                    print("You need to have at least 2 layers")
                elif value > max_layers:
                    print("You can't have more than {0} layers".format(max_layers))
                else:
                    clear_screen()
                    return value
            except ValueError:
                print("Please type an integer")

    @staticmethod
    def _get_colors():
        result = []

        max_colors = 5
        print("How many colors would you like to choose?" + Fore.LIGHTGREEN_EX + Back.BLACK +
              "[0-{0}; 0 to keep the current preferences]".format(max_colors) + Style.RESET_ALL)
        num_colors = None
        while True:
            num_colors = input("> ")
            if num_colors in [str(i) for i in range(0, max_colors + 1)]:
                num_colors = int(num_colors)
                print()
                break
        # Get the number of colors the user would like
        if num_colors == 0:
            return ConvoReader._CANCEL_WC_PREFERENCE

        print("Specify your colors below as rgb values. They must be in the "
              "form of three comma and space separated numbers.")
        print(Fore.GREEN + Back.BLACK + "for example: 255, 0, 255")
        i = 0
        while i < num_colors:
            color = input('{0}) '.format(i + 1))
            try:
                cleaned_color = WordCloud.assert_color_string(color)
            except AssertionError as e:
                print(e)
                print()
            else:
                result.append(cleaned_color)
                i += 1

        return result

    @staticmethod
    def _get_dimensions():
        print("Specify the height and width you would like as integers (in pixels)." +
              Fore.LIGHTGREEN_EX + Back.BLACK + "Type 0 to keep previous settings" + Style.RESET_ALL)
        while True:
            while True:
                try:
                    width = int(input("width: "))
                    if width == 0:
                        return ConvoReader._CANCEL_WC_PREFERENCE
                    break
                except ValueError:
                    print("Must type an integer")
            while True:
                try:
                    height = int(input("height: "))
                    if height == 0:
                        return ConvoReader._CANCEL_WC_PREFERENCE
                    break
                except ValueError:
                    print("Must type an integer")
            try:
                WordCloud.assert_dimensions_for_wc([width, height])
                print('\nConfirm selection? [Y/n]')
                if user_says_yes():
                    return [width, height]
            except AssertionError as e:
                print(e)
                print('\n')

    @staticmethod
    def _get_excluded_words():
        lst_of_choices = [f for f in os.listdir(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH)
                          if os.path.isfile(os.path.join(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH, f))]
        full_paths = [os.path.join(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH, f) for f in lst_of_choices]
        # length of the string for the highest choice number
        num_choices_max_length = len(str(len(lst_of_choices)))
        choice_range = [str(i) for i in range(1, len(lst_of_choices) + 1)]
        selected = []
        selected_color = Fore.LIGHTBLUE_EX + Back.BLACK
        exit_color = Fore.LIGHTRED_EX + Back.BLACK
        while True:
            clear_screen()
            print("Which file(s) would you like to use as excluded words? Select an option to "
                  "toggle it selected / not selected")
            print(selected_color + "blue text" + Style.RESET_ALL +
                  " means this choice is already selected, and choosing it will unselect it\n")

            print(exit_color + "0) Exit" + Style.RESET_ALL)
            for i in range(1, len(lst_of_choices) + 1):
                if full_paths[i - 1] in selected:
                    print(selected_color + "{0}){1}{2}"
                          .format(i, ' ' * (num_choices_max_length + 1 - len(str(i))), lst_of_choices[i - 1]) +
                          Style.RESET_ALL)
                else:
                    print("{0}){1}{2}"
                          .format(i, ' ' * (num_choices_max_length + 1 - len(str(i))), lst_of_choices[i - 1]))
            print()
            print("Choose which number you would like (between 0 and {0})".format(len(lst_of_choices)))

            while True:
                choice = input('> ').lower()
                if choice in choice_range:
                    choice = int(choice) - 1
                    value = full_paths[choice]
                    if value in selected:
                        selected.remove(value)
                    else:
                        selected.append(value)
                    print('\n')
                    break
                elif choice == '0' or choice == 'exit':
                    return selected

    @staticmethod
    def _get_image_name():
        intro = "Which image would you like to use as a background?" + \
                Fore.LIGHTRED_EX + Back.BLACK + "\nNote this will cause the program to fail if your shape attribute " \
                                                "is not \"image\", or you aren't creating a layered word cloud\n" + \
                Style.RESET_ALL
        lst_of_choices = [f for f in os.listdir(WordCloud.WORD_CLOUD_IMAGE_PATH)
                          if os.path.isfile(os.path.join(WordCloud.WORD_CLOUD_IMAGE_PATH, f)) and
                          WordCloud.valid_picture(f)]
        assert len(lst_of_choices) > 0, "You need to add some pictures to {0}".format(WordCloud.WORD_CLOUD_IMAGE_PATH)

        print(intro)
        # length of the string for the highest choice number
        num_choices_max_length = len(str(len(lst_of_choices)))

        print(Fore.LIGHTGREEN_EX + Back.BLACK + "0) Keep previous settings" + Style.RESET_ALL)
        print("1) None (no image, for use with non 'image' word clouds)")
        for i in range(2, len(lst_of_choices) + 2):
            print("{0}){1}{2}".format(i, ' ' * (num_choices_max_length + 1 - len(str(i))),
                                      lst_of_choices[i - 2]))
        print()
        print("Choose which number you would like (between 0 and {0})".format(len(lst_of_choices) + 1))
        choice_range = [str(i) for i in range(0, len(lst_of_choices) + 2)]
        while True:
            choice = input('> ')
            if choice in choice_range:
                if choice == '0':
                    return ConvoReader._CANCEL_WC_PREFERENCE
                elif choice == '1':
                    return WordCloud.get_default_preferences('default')['image_name']
                return os.path.join(WordCloud.WORD_CLOUD_IMAGE_PATH, lst_of_choices[int(choice) - 2])

    @staticmethod
    def _word_cloud_get_one_liner(attribute):
        if attribute == 'output_name':
            intro = "What name would you like for the output " \
                    "wordcloud file? It must end in '.png' and can't have spaces"
            assertion = WordCloud.assert_output_name_for_wc
            assertion_failure_string = '\nplease try again. Remember to end the name in \".png\", for example ' \
                                       '\"example.png\"'

        elif attribute == 'num_words_to_include':
            intro = "How many words would you like to include (at maximum) in your word cloud? Type an integer. " \
                    "The default value is 1,000."

            def assertion(x):
                WordCloud.assert_num_words_to_include(int(x))
            assertion_failure_string = "Please try again, type an integer"

        elif attribute == 'min_word_length':
            intro = "What's the length of the smallest word you would like to include in the wordcloud?"

            def assertion(x):
                assert int(x) > 0, "X must be an integer greater than 0"
            assertion_failure_string = "Please try again, type an integer"

        elif attribute == 'max_word_length':
            intro = "What's the length of the largest word you would like to include in the wordcloud?"

            def assertion(x):
                assert int(x) > 0, "X must be an integer greater than 0"
            assertion_failure_string = "Please try again, type an integer"

        elif attribute == 'min_font_size':
            intro = "What would you like to set the minimum font size to? The default value is 10."

            def assertion(x):
                assert int(x) > 0, "must be an integer greater than 0"
            assertion_failure_string = "Please Try again, type an integer between 0 and max_font_size"

        elif attribute == 'max_font_size':
            intro = "What would you like to set the maximum font size to? The default value is 40."

            def assertion(x):
                assert int(x) > 0, "must be an integer greater than 0"
            assertion_failure_string = "Please Try again, type an integer above the min_font_size"
        else:
            raise ValueError("invalid value of attribute passed")
        # Above define standard assertions to test data with and strings to print for various cases

        while True:
            print(intro + Fore.LIGHTGREEN_EX + Back.BLACK + " Type 0 to keep previous settings" + Style.RESET_ALL)
            name = input('> ')
            if name == '0':
                return ConvoReader._CANCEL_WC_PREFERENCE
            try:
                assertion(name)
            except Exception as e:
                print(e)
                print(assertion_failure_string)
                print()
            else:
                print("Would you like to confirm \"{0}\" as your {1}? [Y/n]".format(name, attribute))
                if user_says_yes():
                    if attribute not in ['output_name', 'input_name']:
                        name = int(name)
                    return name

    def _word_cloud_get_from_list(self, attribute):
        if attribute == 'shape':
            intro = "What shaped word cloud would you like? Chose one from the following:"
            lst_of_choices = sorted(WordCloud.WORD_CLOUD_SHAPES)
        elif attribute == 'type':
            intro = "What type of word cloud would you like? Chose one from the following"
            lst_of_choices = sorted(WordCloud.WORD_CLOUD_TYPES)
        elif attribute == 'input_name':
            intro = "Which of the following files would you like to use as input for the word cloud?"

            def name_to_file(name):
                # Based on save_word_freq in baseconvoreader
                file_name = ""
                for part in name.split():
                    file_name += part + '-'
                file_name = file_name[:-1]
                return file_name + '_word_freq.txt'

            lst_of_choices = list(map(name_to_file, self.get_people())) + ['total.txt']
        elif attribute == 'font_type':
            intro = "What font type would you like?"
            lst_of_choices = WordCloud.WORD_CLOUD_FONT_TYPES
        else:
            raise ValueError("Invalid value of attribute")
        print(intro)
        # length of the string for the highest choice number
        num_choices_max_length = len(str(len(lst_of_choices)))
        if attribute != 'type':
            print(Fore.LIGHTGREEN_EX + Back.BLACK + "0) Keep previous settings" + Style.RESET_ALL)
        for i in range(1, len(lst_of_choices) + 1):
            print("{0}){1}{2}".format(i, ' ' * (num_choices_max_length + 1 - len(str(i))),
                                      lst_of_choices[i - 1]))
        print()
        print("Choose which number you would like (between 1 and {0})".format(len(lst_of_choices)))
        choice_range = [str(i) for i in range(0, len(lst_of_choices) + 1)]
        while True:
            choice = input('> ')
            if choice in choice_range:
                if choice == '0':
                    return ConvoReader._CANCEL_WC_PREFERENCE
                return lst_of_choices[int(choice) - 1]

    @staticmethod
    def _get_sets(previous, mode, fn):
        """Uses user input to grab either text_sets, image_sets or color_sets, depending on mode and fn
        Should only ever be used in word_clouds and resulting _get_word_cloud_preferences
        """
        same_color = Fore.LIGHTGREEN_EX + Back.BLACK
        diff_color = Fore.LIGHTMAGENTA_EX + Back.BLACK

        current = copy.copy(previous)
        longest_number = len(str(previous)) + 1
        while True:
            print("0) Exit {0} selection".format(mode))
            for i in range(1, len(previous) + 1):
                print("{0}){1}".format(i, ' ' * (longest_number - len(str(i)))), end="")
                print(current[i], end=" = ")

                if current[i] != previous[i]:
                    print(diff_color + current[i])
                else:
                    print(same_color + current[i])

            user_choice = get_user_choice_from_range(0, len(current))

            if user_choice == 0:
                if user_says_yes():
                    return current
                else:
                    continue

            current[user_choice] = fn()

    def _get_layered_text_image_colors(self, num_layers, previous=None):
        def is_duplicate(preference_type, index, grid):
            for j in range(len(grid[preference_type])):
                if grid[preference_type][j] == grid[preference_type][index] and j != index:
                    return True
            return False

        same_color = Fore.LIGHTGREEN_EX + Back.BLACK
        diff_color = Fore.LIGHTMAGENTA_EX + Back.BLACK
        duplicate_color = Fore.LIGHTBLUE_EX + Back.BLACK

        # a 2D list containing inner lists of string, string then a list for the colors
        if previous is None:
            text_image_colors = [[WordCloud.DEFAULT_INPUT_NAME for _ in range(num_layers)],
                                 ['' for _ in range(num_layers)],
                                 [WordCloud.DEFAULT_COLORS for _ in range(num_layers)]]
        else:
            text_image_colors = copy.deepcopy(previous)

        clear_screen()
        longest_num = len(str(num_layers * 3 + 1))
        while True:
            print("Select values for each of the {0} options below. A " + duplicate_color + "blue" + Style.RESET_ALL +
                  " value represents values that are duplicated across layers, a " + diff_color + "magenta" +
                  Style.RESET_ALL + " value represents a unique edited value, and a " + same_color + "green" +
                  Style.RESET_ALL + " value represents a unique default value" + Style.RESET_ALL +
                  "\n".format(num_layers * 3))

            print(Fore.LIGHTRED_EX + Back.BLACK + "0) Continue" + Style.RESET_ALL)
            for i in range(1, num_layers * 3 + 1):
                if i - 1 > 0 and (i - 1) % 3 == 0:
                    print()

                print("{0})".format(i), end="")
                print(' ' * (longest_num - len(str(i)) + 1), end="")
                if i % 3 == 1:
                    print("text_set{0} = ".format((i - 1) // 3 + 1), end="")
                elif i % 3 == 2:
                    print("image_name{0} = ".format((i - 1) // 3 + 1), end="")
                else:
                    print("color_set{0} = ".format((i - 1) // 3 + 1), end="")

                cur_val = text_image_colors[(i - 1) % 3][(i - 1) // 3]
                prev_val = previous[(i - 1) % 3][(i - 1) // 3] if previous is not None else None
                if is_duplicate((i - 1) % 3, (i - 1) // 3, text_image_colors):
                    print(duplicate_color + str(cur_val) + Style.RESET_ALL)
                elif cur_val != prev_val:
                    print(diff_color + str(cur_val) + Style.RESET_ALL)
                else:
                    print(same_color + str(cur_val) + Style.RESET_ALL)

            print('\nSelect your choice (between 0 and {0})'.format(num_layers * 3))
            user_choice = get_user_choice_from_range(0, num_layers * 3)

            if user_choice == 0:
                print('\nAre you sure you would like to continue? [Y/n]')
                if user_says_yes():
                    break
                else:
                    continue

            print('\n' + one_line() + '\n')

            if user_choice % 3 == 1:
                text_image_colors[0][(user_choice - 1) // 3] = self._get_input_name()
            elif user_choice % 3 == 2:
                text_image_colors[1][(user_choice - 1) // 3] = self._get_image_name()
            else:
                text_image_colors[2][(user_choice - 1) // 3] = self._get_colors()

            clear_screen()

        return text_image_colors

    # -----------------------------------------   WORD CLOUD PRIVATE METHODS   --------------------------------------- #

    # ----------------------------------------------   BUILT IN METHODS   -------------------------------------------- #

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

    # ----------------------------------------------   BUILT IN METHODS   -------------------------------------------- #


def get_user_choice_from_range(start, end):
    """Returns the integer corresponding to the user's choice"""
    choice_range = [str(i) for i in range(start, end + 1)]
    user_choice = None
    while user_choice not in choice_range:
        user_choice = input("> ")

    return int(user_choice)
