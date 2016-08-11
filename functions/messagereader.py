from collections import Counter
import shutil
import os
import random
import ast
from colorama import Fore, Back, Style, init


from functions.setup_functions import (PreferencesSearcher, clear_screen, user_says_yes, fit_colored_text_to_console,
                                       one_line)
from functions.baseconvoreader import BaseConvoReader
from functions.convoreader import ConvoReader, color_method
from functions.guiconvoreader import GUIConvoReader
from functions.customdate import CustomDate

init(autoreset=True)


class MessageReader:

    def __init__(self):
        with open('data/data.txt', mode='r', encoding='UTF8') as f:
            try:
                self.data = ast.literal_eval(f.readline())
                self.download = f.readline()

                tmp_preference = ast.literal_eval(f.readline())
                tmp_contacted = tmp_preference['contacted']
                new_contacted = dict()
                for key, val in tmp_contacted.items():
                    new_contacted[key] = (val[0], CustomDate(val[1]))
                tmp_preference['contacted'] = new_contacted

                self.quick_stats = PreferencesSearcher(tmp_preference)
            except Exception as e:
                print(Fore.LIGHTRED_EX + Back.BLACK + "An error occurred when reading in your data file. Please make "
                                                      "sure setup.py finished properly")
                raise e
        self.names = self._get_convo_names_freq()
        self.person = " ".join(self.download.split(' ')[2:-8])
        self.download_date = CustomDate(" ".join(self.download.split()[-7:]))
        self.first_chat_date = self.get_first_chat_date()
        self._edits = []

    # -------------------------------------------   CONVERSATION GRABBING  ------------------------------------------ #

    def get_convo_names(self, by_recent=False):
        """Returns a list of lists, where each inner list is
        the members of a conversation. By default is arranged
        with most active chat first in decreasing order, but
        can pass alpha=True to order by alphabetical
        Parameters:
            by_recent (optional): False by default, in which case conversation names are
                returned in order of most frequent first, and then alphabetical. If True
                conversations names are ranked in order of most recent chat first
        """
        if not by_recent:
            return self.names
        else:
            return sorted(self.names, key=lambda name: CustomDate(self.data[name][-1][2]), reverse=True)

    def print_names(self, limit=None, by_recent=False):
        """Prints to screen conversation names
        Parameters:
            by_recent (optional): False by default, in which case conversation names are
                printed in order of frequency, with highest frequencies first. If True then
                conversations are printed in order of most recently contacted first
            limit (optional): The number of conversations to print to the screen, if left
                as default then all are printed
            """
        i = 1
        for name in self.get_convo_names(by_recent):
            print(str(i) + ": " + name)
            i += 1
            if limit is not None and i > limit:
                break

    def get_convo(self, people):
        """Returns a ConvoReader object representing the conversation
        passed as a list of names, string name or index of conversation
        (from print_names). If an invalid parameter is passed return None
        Parameters:
            people: Which conversation you would like to get. Either the number from the output of
            print_names(), the name of the conversation you want (e.g. 'sean lobo, jason perrin')
            or a list of names (e.g. ['jason perrin', 'sean lobo'])
        """
        assert type(people) in [str, list, int], (
            "Invalid argument: must pass a list of names (as strings), string, or int"
        )

        if type(people) is int:
            if people > 0:
                return ConvoReader(self.names[people - 1], self.data[self.names[people - 1]], people)
            else:
                return ConvoReader(self.names[len(self.names) + people],
                                   self.data[self.names[len(self.names) + people]],
                                   people)
        if type(people) is str:
            people = people.title().split(', ')
        else:
            people = list(map(lambda x: x.title() if 'facebook' not in x else x, people))
        for i in range(len(self)):
            name = self.quick_stats.get_name(i + 1, 'alpha')
            if contents_equal(name.split(', '), people):
                return ConvoReader(name, self.data[name], i + 1)
        print("You haven't talked with {0} before".format(people))
        return None

    def get_convo_gui(self, index):
        """Returns the GUIConvoReader object corresponding to index"""
        assert isinstance(index, int), "index needs to be an integer"
        assert 0 < index <= len(self), "Index out of bounds, index must be between 1 and {0}".format(len(self))

        return GUIConvoReader(self.names[index - 1], self.data[self.names[index - 1]], self.download_date)

    def random(self):
        """Returns a random conversation"""
        return self.get_convo(int(random.random() * len(self) + 1))

    def rank(self, convo_name):
        """Prints to the console the rank of the conversation passed"""
        try:
            res = self._raw_rank(convo_name)
            if res is not None:
                print(res)
            else:
                print("A conversation for {0} was not found"
                      .format(convo_name.get_people if isinstance(convo_name, ConvoReader) else str(convo_name)))
        except AssertionError as e:
            print(e)

    # -------------------------------------------   CONVERSATION GRABBING  ------------------------------------------ #

    # ------------------------------------------------   EDITING DATA  ----------------------------------------------- #

    def edit_convo_participants(self, convo_num, old_name, new_name, force=False, verbose=True):
        """Updates the specified conversation number by replacing all instances of old_name in the person
        attribute with new_name
        Parameter:
            convo_num: an integer representing the conversation we would like to edit
            old_name: the old name to be replaced
            new_name: the new name to replace old_name with
            force (optional): if True then user prompts are bypassed and the edits occur anyway. Defaults to False
        """
        # Assertions to make sure data is good 
        assert isinstance(convo_num, int), "convo_num must be an integer"
        assert 1 <= convo_num <= len(self) or -len(self) <= convo_num <= -1, \
            "convo_num must be a valid index (between 1 and {0})".format(len(self))
        if convo_num < 1:
            convo_num = convo_num + len(self) + 1
        assert isinstance(old_name, str), "old_name must be a string"
        old_name = old_name.lower()
        convo = self.get_convo(convo_num)
        if old_name not in convo.get_people():
            return
        assert isinstance(new_name, str), "new_name must be a string"
        new_name = new_name.lower()
        # Assertions to make sure data is good

        if verbose:
            chunk = ("Beginning conversation edits for your #{rank} ranked chat (by messages). The conversation "
                     "includes {people}".format(rank=self.rank(convo), people=convo.get_people()))
            print(fit_colored_text_to_console(chunk))

        if new_name in convo.get_people() and not force:
            # if the user is trying to replace a name with an already existing name, 
            # it could be impossible to undo this, since we can't tell which names 
            # were originally the new name and which were changed. This block warns them if force is False
            print("{new} is already in the conversation. Swapping {old} for {new} will potentially make it "
                  "impossible to revert settings for this conversation alone. If you proceed and save these changes,"
                  "you will have to run setup again and revert all conversation edits. "
                  .format(new=new_name, old=old_name), end="")
            print(Fore.RED + "Are you sure you would like to proceed? [Y/n]")
            if not user_says_yes():
                print()
                return
            print()

        occurrences = 0  # number of occurrences that are being swapped. Just so the user knows
        for person, msg, date in convo:
            if person == old_name:
                occurrences += 1
        if not force:
            print("Swapping {old} for {new} will result in {num_changes} changes. Would you like to proceed? [Y/n]"
                  .format(old=old_name, new=new_name, num_changes=occurrences))

            # Does the user really want to continue after getting information
            if not user_says_yes():
                return

        # The name and data associated with the desired conversation before any actions have been performed
        previous_name = self.names[convo_num - 1]
        previous_data = self.data[previous_name]

        # if else block below deal with getting an updated name for the self.data dictionary key
        if new_name.title() not in previous_name.split(', '):
            # if new_name is not already present, swap the old_name for it
            updated_name = previous_name.replace(old_name.title(), new_name.title())
        else:
            # Take the previous_name and cut out old_name, instead of
            # replacing with new_name since new name is already in the name
            updated_name = ", ".join([name for name in previous_name.split(', ') if name != old_name.title()])
        updated_name = ', '.join(sorted(updated_name.split(', ')))

        if updated_name in self.names and not force:
            print('\n' + Fore.LIGHTRED_EX + Back.BLACK + "Warning:" + Style.RESET_ALL)
            chunk1 = ("Replacing '{old}' with '{new}' would result in a conversation whose participants are "
                      "identical to an existing conversation. This may cause unexpected behavior, or cause issues. "
                      "If you encounter any such issues contact someone at this project's download location. "
                      "Would you like to continue? [Y/n]".format(old=old_name, new=new_name))
            print(fit_colored_text_to_console(chunk1, old_name, new_name, '[Y/n]'))
            if not user_says_yes():
                return

        # The block below updates the List<tuple> for the self.data value of the dictionary
        for i in range(len(previous_data)):
            person, msg, date = previous_data[i]
            if person.lower() == old_name:
                previous_data[i] = tuple([new_name.title(), msg, date])

        self._edits.append(self._raw_rank(previous_name))
        del self.data[previous_name]  # deletes the old data from self.data
        self.data[updated_name.title()] = previous_data  # updates self.data with the new data
        self.names = self._get_convo_names_freq()  # update self.names with new keyset

        chunk = ("The specified changes have been made. Please note that these changes will only last the duration "
                 "of this python session. If you would like to make the changes permanent, call m.save_convo_edits()")
        if verbose:  # print confirmation if in verbose mode
            print(fit_colored_text_to_console(chunk, "m.save_convo_edits()"))

    def edit_all_occurrences(self, old_person, new_person, force=False, verbose=True):
        """Edits every conversation with old_person, replacing them with new_person
        Parameters:
            old_person: (str) the name of the person to be replaced
            new_person: (str) the name to replace occurrences of old_person with
            force (optional): (Boolean) Whether to prompt the user about the change
        """
        assert isinstance(old_person, str), "old_person must be a string"
        assert isinstance(new_person, str), "new_person must be a string"
        old_person = old_person.lower()
        new_person = new_person.lower()

        change_count = 0
        for i in range(len(self)):
            if old_person in self.names[i].lower().split(', '):
                change_count += 1
        if change_count == 0:
            return
        if not force:
            chunk = "Changing all conversations would result in {num_changes} changes. Would you like to proceed? [Y/n]"\
                .format(num_changes=change_count)
            print(fit_colored_text_to_console(chunk))
            if not user_says_yes():
                return

        for i in range(len(self)):
            self.edit_convo_participants(i + 1, old_person, new_person, force=True, verbose=False)

        if verbose:
            print("Your changes have been made where applicable")

    def save_convo_edits(self, force=False):
        """Saves changes made to conversation names with edit_convo_participants
        Parameters:
            force (optional): (Boolean) If True bypasses user prompts to continue. Default False
        """
        if not force:
            print(fit_colored_text_to_console("Are you sure you would like to save the changes made? You might have to "
                  "redo setup in order to revert. Additionally your conversation preferences will  be lost. [Y/n]"))
            if not user_says_yes():
                return

        for value in self._edits:
            path = BaseConvoReader.BASE_PATH + str(value) + '/'
            if os.path.isfile(path):
                shutil.rmtree(path)

        with open('data/data.txt', mode='w', encoding='utf-8') as f:
            f.write(repr(self.data) + '\n')
            f.write(self.download)
            f.write(str(PreferencesSearcher.from_msgs_dict(self.data).preferences))

    def save_subset_of_data(self, conversation_names, file_name):
        """Saves to a file the data for the conversation specified
        Parameters:
            conversation_names: a list of: integer indexes corresponding to the conversation you would like,
                or comma separated strings of names e.g. 'my name, your name',
                or lists of names as strings e.g. ['your name', 'my name']
            file_name: a string filename for the data to be written to
        """
        try:
            assert isinstance(conversation_names, list) or isinstance(conversation_names, tuple), \
                "conversation_names must be a list or tuple of conversation identifiers"
            assert len(conversation_names) > 0, "conversation_names must not be empty"
            assert isinstance(file_name, str), "file_name must be a string"
            assert ' ' not in file_name[
                              -4:] == '.txt' in file_name, "file_name can't have spaces and should end in .txt"

            # prompt user if the passed file_name already exists
            if os.path.isfile(file_name):
                print(
                    "{0} already exists, continuing would override this data. Would you like to continue? [Y/n]")
                if not user_says_yes():
                    return

            convo_ranks = [self._raw_rank(self.get_convo(name)) for name in conversation_names]

            new_data = dict()
            for rank in convo_ranks:
                new_data[self.names[rank - 1]] = self.data[self.names[rank - 1]]

            download = self.download
            quick_settings = PreferencesSearcher.from_msgs_dict(new_data)

            with open(file_name, mode='w', encoding='utf-8') as f:
                f.write(str(new_data) + '\n')
                f.write(download)
                f.write(str(quick_settings.preferences))
        except AssertionError as e:
            print(e)
            return

    # ------------------------------------------------   EDITING DATA  ----------------------------------------------- #

    # ----------------------------------------------   ANALYTIC METHODS  --------------------------------------------- #

    def top_conversations(self, start, end, limit=10):
        """Prints a ranking of top conversations in a time period
        Parameters:
            start: The date string representing the first day to start counting from (in the format {month}/{day}/{year}
            end: The date string for the last day to count
            limit (optional): An integer representing the number of conversations to print, or False to display all
        """
        try:
            rankings = self.raw_top_conversations(start, end)
            assert isinstance(limit, int) or isinstance(limit, False), "Limit should be an integer or False"
            if isinstance(limit, int):
                assert 1 <= limit, "Limit should be greater than or equal to 1"
        except AssertionError as e:
            print(e)
            return

        if limit is False or limit > len(self):
            limit = len(self)

        MAX_INT_LEN = len(str(limit)) + 1
        i = 1
        for convo, freq in rankings.most_common(limit):
            if freq == 0:
                break
            print(Fore.GREEN + Back.BLACK + str(i) + ')', end="")
            print("{0}{1} - {2}".format(' ' * (MAX_INT_LEN - len(str(i))), convo, freq))
            i += 1

    def raw_top_conversations(self, start, end):
        """Returns a counter for top conversations in a time period"""
        CustomDate.assert_dates(start, end)
        start, end = CustomDate.from_date_string(start), CustomDate.from_date(CustomDate.from_date_string(end) + 1)
        rankings = Counter()

        for i in range(len(self)):
            convo = self.get_convo(i + 1)
            name = convo._name.title()
            rankings[name] = 0
            if start < convo[-1][2] and end > convo[0][2]:  # if the range we want overlaps with this conversation
                for person, msg, date in convo:
                    if start <= date <= end:
                        rankings[name] += 1

        return rankings

    def emoijs(self, only_me=False, limit=10):
        """Prints the emoji use of all conversations combined to the console
        Parameters:
            only_me (optional): (Boolean) Whether to include only your emoji use or everyone's in total.
                                Defaults to everyone's use
            limit (optional): (int|None) The number of emojis to print, or None to print all. Defaults to 10
        """
        ranking = self.raw_emojis(only_me=only_me)
        try:
            ConvoReader.print_counter(ranking, limit=limit)
        except AssertionError as e:
            print(e)
            return

    def raw_emojis(self, only_me=False):
        """Returns the total raw_emojis in an aggregate sum of all your conversations
            Parameters:
                only_me (optional): Considers only your sent messages if True, otherwise both your sent and received
            Return:
                Counter object storing your emoji frequencies
        """
        res = Counter()
        for i in range(1, len(self) + 1):
            try:
                if only_me:
                    res += self.get_convo_gui(i).raw_emojis(person=self.person)
                else:
                    res += self.get_convo_gui(i).raw_emojis()
            except AssertionError:
                pass
        return res

    def messages_graph(self, only_me=False, forward_shift=0, start=None, end=None):
        try:
            msgs_freq = self.raw_messages_graph(only_me=only_me, forward_shift=forward_shift, start=start, end=end)
            CustomDate.assert_dates(start, end)
        except AssertionError as e:
            print(e)
            return

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

    def raw_messages_graph(self, only_me=False, forward_shift=0, start=None, end=None):
        """Returns a list representing the data for aggregate messaging totals by day for every day from the date your
        first message was sent to data's download date
        Parameters:
            only_me (optional): (Boolean) Whether to include just your chatting data (messages sent by you) or all
                                messages sent and received
            forward_shift (optional): (int) The number of minutes past 11:59pm that should be counted towards the totals
                                       for the previous day
            start (optional): (str|None) a date string representing the start date in the form "{month}/{day}/{year}"
            end (optional): (str|None) a date string for the end date, in the same format as start
        Return:
            A list of tuples with a CustomDate in element 0 and the integer number of messages for that day in element 1
        """
        CustomDate.assert_dates(start, end)
        start = self.first_chat_date if start is None else CustomDate.from_date_string(start)
        end = self.download_date if end is None else CustomDate.from_date_string(end)
        assert start >= self.first_chat_date, "start needs to be on or after {0}"\
            .format(self.first_chat_date.to_string())
        assert end <= self.download_date, "end needs to be before or on {0}".format(self.download_date.to_string())

        start_index = start - self.first_chat_date
        end_index = end - self.download_date - 1

        total = Counter()
        if only_me:
            contact = self.person.lower()
        else:
            contact = None

        for i in range(1, len(self) + 1):
            try:
                messages_data = self.get_convo_gui(i).raw_msgs_graph(contact=contact, forward_shift=forward_shift)
                total.update({key: val for key, val in messages_data})
            except AssertionError:
                pass

        result = sorted(total.most_common(), key=lambda x: x[0])
        return result[start_index: end_index]

    # ----------------------------------------------   ANALYTIC METHODS  --------------------------------------------- #

    @staticmethod
    def help():
        """Provides help for using MessageReader based on user input"""
        clear_screen()
        print("Welcome to the help function for MessageReader\n\n")

        condition = True
        while condition:  # Continue's offering help until the user escapes with option 3
            print(Fore.LIGHTMAGENTA_EX + Back.BLACK + 'Please select which feature you would like help with:')
            print(Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + Back.BLACK + '0) What can I do here??')
            print(Style.RESET_ALL + '\n1) Viewing a list of conversations you can analyze')
            print('2) Getting started analyzing a specific conversation')
            print('3) Exit helper\n')
            print("Choose a number between 0 and 3")
            # Which choice would the user like help with?

            choice_condition = True
            while choice_condition:
                choice = input('> ')
                choice_condition = choice not in [str(i) for i in range(4)]
            clear_screen()
            # Gets the user's choice of 0-3 and clears the screen after in preparation

            if choice == '0':
                # Helps user with an idea of what they can do with a messagereader
                print("Option 0:")
                print(Fore.LIGHTCYAN_EX + Back.BLACK + '\"What can I do here??\"' + Style.RESET_ALL)
                chunk1 = ('Good question. Here you can perform a variety of analysis on your facebook conversations, '
                          'from analyzing the words you use most frequently in your favorite chat, to stats '
                          'on who starts or ends conversations the most, to rankings of total emoji use in all your '
                          'conversations, and much more.')
                chunk2 = ('If you\'re primarily interested in viewing visualizations of your data, and not in actually '
                          'using the raw data, you might be better off using the GUI version of this program. Exit '
                          'this helper (choice 3) and type the command `exit()`. Once you\'re out of this python'
                          ' session, run the command `python3 fancy_playground.py`')
                chunk3 = ('If you\'re looking to get into the nitty gritty analysis of your facebook conversation '
                          'history, this is the place for you. To get information on getting started pick choices '
                          '1 or 2 below')

                print(fit_colored_text_to_console(chunk1))
                print('\n')
                print(fit_colored_text_to_console(chunk2, "exit()", "python3 fancy_playground.py"))
                print('\n')
                print(fit_colored_text_to_console(chunk3))
                print('\n')

            elif choice == '1':
                # Helps users view a list of conversations they can analyze
                print("Option 1: Viewing a list of conversations you can analyze")
                print(one_line())

                chunk1 = ('To view a list of conversations that you can analyze, exit this helper and execute the '
                          'command `m.print_names()`. This will print to the console a list of all contacts you '
                          'have messaged, sorted with decreasing number of messages. Since this number can be large, '
                          'you can optionally pass an integer limiting the conversations printed, for example '
                          '`m.print_names(10)` to print your top 10 conversations')
                chunk2 = ('To get more options on printing conversations, exit the helper and execute '
                          '`help(m.print_names)`. This is only if you plan on doing fancy stuff')

                print(fit_colored_text_to_console(chunk1, "m.print_names()", "m.print_names(10)"))
                print()
                print(fit_colored_text_to_console(chunk2, "help(m.print_names)"))
                print()
                print('After deciding on a conversation to analyze, see option (2) below on how to get started, '
                      'as well as an example')

            elif choice == '2':
                # Helps users see how to grab a specific conversation
                print('Option 2: Getting started analyzing a specific conversation')
                print(one_line())
                print('To analyze a specific conversation, you must retrieve it in one of 3 main ways:')
                print()

                chunk1 = ('Print to the screen the ordered list of conversations (see choice 1) and find the rank of '
                          'the conversation you would like. Then save that conversation to variable by executing the '
                          'command `variable_name = m.get_convo(rank_of_desired_convo)`')
                chunk2 = ('Get the conversation you would like by searching for its name, e.g. executing the '
                          'command `variable_name = m.get_convo(\'bob smith, sally brown\')`')
                chunk3 = ('Get the conversation you would like by searching for its name as a list, e.g. '
                          'executing the command `variable_name = m.get_convo([\'both smith\', \'sally brown\'])`')

                print(Fore.GREEN + Back.BLACK + '(1)')
                print(fit_colored_text_to_console(chunk1, "variable_name", "m.get_convo(rank_of_desired_convo)"))
                print(Fore.GREEN + Back.BLACK + '\n(2)')
                print(fit_colored_text_to_console(chunk2, "variable_name", "m.get_convo(\'bob smith, sally brown\')"))
                print(Fore.GREEN + Back.BLACK + '\n(3)')
                print(fit_colored_text_to_console(chunk3, "variable_name",
                                                  'm.get_convo([\'both smith\', \'sally brown\'])'))
                print()

                print('Once you have your desired conversation, to get additional help analyzing it execute '
                      '`{0}`'.format(color_method('help(variable_name_from_above)')))

                print('\n\n...would you like an example? [Y/n]')

                # Describes an example of how to grab a conversation
                if user_says_yes():
                    code_color = Fore.LIGHTBLACK_EX + Back.BLACK
                    print(one_line())
                    print(Fore.LIGHTRED_EX + Back.BLACK + "\nEXAMPLE)")

                    chunk1 = ("Let\'s say I want to see my top 3 conversations. I can do this with command "
                              "`m.print_names(3)`, where the 3 tells the program to print my top 3 contacts "
                              "(ordered by total number of messages sent and received; for more options do "
                              "`help(m.print_names)`)")
                    print(fit_colored_text_to_console(chunk1, "help(m.print_names)", "m.print_names(3)"))
                    print("The above would go something like this:\n")

                    print(code_color + ">>> m.print_names(3)" + Style.RESET_ALL +
                          code_color + "\n1) Sally Brown, Your Name" + Style.RESET_ALL +
                          code_color + "\n2) Bob Smith, Your Name" + Style.RESET_ALL +
                          code_color + "\n3) Your Name, Edward Newgate" + Style.RESET_ALL)
                    print()

                    chunk2 = ("Now if I'd like to analyze my chat with Edward, I should first capture our "
                              "conversation in the following way:\n")
                    print(fit_colored_text_to_console(chunk2))
                    print(code_color + ">>> edward = m.get_convo(3)" + Style.RESET_ALL + '\n')

                    chunk3 = ("Here, we use the `get_convo(3)` method to retrieve our conversation. The 3 "
                              "corresponds to our 3rd most contacted person from the `print_names()` method call."
                              " Additionally, the fact that we used the variable name \"edward\" is arbitrary. "
                              "Any name can be used, I've just fallen into the habit of naming conversation variables "
                              "after the name of the conversation, so it\'s easy to remember later")
                    print(fit_colored_text_to_console(chunk3, "print_names()", "get_convo(3)"))
                    print()

                    chunk4 = ("\nOnce we\'ve successfully saved the chat we'd like, we can proceed to analyze it by "
                              "executing the command `edward.help()` (replace edward with whatever variable name"
                              " you used)")
                    print(fit_colored_text_to_console(chunk4, "edward.help()"))

            condition = choice != '3'
            if condition:  # We're continuing for another round
                print('\nContinue getting help? [Y/n]')
                if not user_says_yes():
                    return

            clear_screen()

    def get_first_chat_date(self) -> CustomDate:
        start_dates = []
        for i in range(len(self)):
            # the date of the first message for the ith chat
            start_dates.append(CustomDate(self.data[self.names[i]][0][2]))

        return min(start_dates)

    def _raw_rank(self, convo_name) -> int:
        """Returns the rank of the particular conversation, or None if not found"""
        assert type(convo_name) in [str, list, ConvoReader], "You must pass a Conversation name or ConvoReader object"
        if isinstance(convo_name, BaseConvoReader):
            return self._raw_rank(convo_name.get_people())
        if type(convo_name) == list:
            for i, name in enumerate(convo_name):
                assert type(name) == str, "Your list must contain strings corresponding to names of people"
                convo_name[i] = name.title()
        elif type(convo_name) == str:
            convo_name = convo_name.title().split(', ')
        for i, name in enumerate(self.names):
            if contents_equal(convo_name, name.title().split(', ')):
                return i + 1

    def _get_convo_names_freq(self):
        """Returns the list of title case names of conversations you have,
        sorted first in order of most chatted to least and second alphabetically"""
        return [ele for ele, _ in
                sorted([(key, len(val)) for key, val in self.data.items()],
                       key=lambda x: (-x[1], x[0]))]

    def __len__(self):
        return len(self.names)

    def __str__(self):
        return self.download

    def __repr__(self):
        return 'MessageReader()'


def contents_equal(lst1, lst2):
    if len(lst1) != len(lst2):
        return False
    return sorted(lst1) == sorted(lst2)
