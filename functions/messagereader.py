from collections import Counter
import shutil
import os
import random
import ast
from colorama import Fore, Back, Style, init


from functions.setup_functions import PreferencesSearcher, clear_screen, user_says_yes
from functions.convoreader import ConvoReader, color_method
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
                print(Fore.LIGHTRED_EX + Back.BLACK + "An error occured when reading in your data file. Please make "
                                                      "sure setup.py finished properly")
                raise e
        self.names = self._get_convo_names_freq()
        self.person = join(self.download.split(' ')[2:-8], split=" ")

        self._edits = dict()
        self._spacer = ' ---> '

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
        assert type(people) in [str, list, int], (""
                                                  "Invalid argument: must pass"
                                                  "a list of names (as strings), string, or int")

        if type(people) is int:
            if people > 0:
                return ConvoReader(self.names[people - 1], self.data[self.names[people - 1]])
            else:
                return ConvoReader(self.names[len(self.names) + people], self.data[self.names[len(self.names) + people]])
        if type(people) is str:
            people = people.title().split(', ')
        else:
            people = [name.title() for name in people]
        for name in self.data.keys():
            if contents_equal(name.split(', '), people):
                return ConvoReader(name, self.data[name])
        print("You haven't talked with {0} before".format(people))
        return None

    def edit_convo_participants(self, convo_num, old_name, new_name):
        """Updates the specified conversation number by replacing all instances of old_name in the person
        attribute with new_name
        Parameter:
            convo_num: an integer representing the conversation we would like to edit
            old_name: the old name to be replaced
            new_name: the new name to replace old_name with
        """
        # Assertions to make sure data is good 
        assert isinstance(convo_num, int), "convo_num must be an integer"
        assert 1 <= convo_num <= len(self) or -len(self) <= convo_num <= -1, \
            "convo_num must be a valid index (between 1 and the number of conversations)"
        if convo_num < 1:
            convo_num = convo_num + len(self) + 1
        assert isinstance(old_name, str), "old_name must be a string"
        old_name = old_name.lower()
        convo = self.get_convo(convo_num)
        assert old_name in convo.get_people(), "old_name must be someone currently in the conversation"
        assert isinstance(new_name, str), "new_name must be a string"
        new_name = new_name.lower()
        # Assertions to make sure data is good

        if new_name in convo.get_people():
            # if the user is trying to replace a name with an already existing name, 
            # it could be impossible to undo this, since we can't tell which names 
            # were originally the new name and which were changed. This block warns them 
            print("{0} is already in the conversation. Swapping {1} for {2} will potentially make it "
                  "impossible to revert settings for this conversation alone. If you proceed and save these changes,"
                  "you will have to run setup again and revert all conversation edits. "
                  .format(new_name, old_name, new_name), end="")
            print(Fore.RED + "Are you sure you would like to proceed? [Y/n]")
            if not user_says_yes():
                print()
                return
            print()

        occurrences = 0  # number of occurances that are being swapped. Just so the user knows
        for person, msg, date in convo:
            if person == old_name:
                occurrences += 1
        print("Swapping {0} for {1} will result in {2} changes. Would you like to proceed? [Y/n]"
              .format(old_name, new_name, occurrences))

        # Does the user really want to continue after getting information
        if not user_says_yes():
            return

        # The name and data associated with the desired converation before any actions have been performed
        previous_name = self.names[convo_num - 1]
        previous_data = self.data[previous_name]

        # if else block below deal with getting an updated name for the self.data dictionary key
        if new_name.title() not in previous_name:  # if new_name is not already present, swap the old_name for it
            updated_name = previous_name.replace(old_name.title(), new_name.title())
        else:
            # Take the previous_name and cut out old_name, instead of
            # replacing with new_name since new name is already in the name
            updated_name = join([name for name in previous_name.split(', ') if name != old_name.title()], ", ")

        # The block below updates the List<tuple> for the self.data value of the dictionary
        for i in range(len(previous_data)):
            person, msg, date = previous_data[i]
            if person.lower() == old_name:
                previous_data[i] = tuple([new_name.title(), msg, date])

        del self.data[previous_name]  # deletes the old data from self.data
        self.data[updated_name.title()] = previous_data  # updates self.data with the new data
        self.names = self._get_convo_names_freq()  # update self.names with new keyset
        edit_string = "{0}{1}{2}".format(previous_name, self._spacer, updated_name)
        if convo_num not in self._edits:
            self._edits[convo_num] = [edit_string]
        else:
            self._edits[convo_num].append(edit_string)
        print("The specified changes have been made. Please note that these changes will only last the "
              "duration of this python session. If you would like to make the changes permanent, call ", end="")
        print(Fore.LIGHTGREEN_EX + "m.save_convo_edits()")


    def save_convo_edits(self):
        """Saves changes made to conversation names with edit_convo_participants"""
        print("Are you sure you would like to save the changes made? "
              "You might have to redo setup in order to revert. Your conversation preferences will  be lost. [Y/n]")
        if user_says_yes():
            return

        for key in self._edits:
            for change in self._edits[key]:
                old, new = change.split(self._spacer)

                old_path = 'data/' + ConvoReader.list_to_combined_string(sorted(old.split(', ')))
                new_path = 'data/' + ConvoReader.list_to_combined_string(sorted(old.split(', ')))

                if os.path.isdir(old_path):
                    shutil.rmtree(old_path)

                # for future use in moving things consider the following post
                # http://stackoverflow.com/questions/225735/batch-renaming-of-files-in-a-directory

        with open('data/data.txt', mode='w', encoding='utf-8') as f:
            f.write(repr(self.data) + '\n')
            f.write(repr(self.download))

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

    def raw_top_conversations(self, start, end):
        """Returns a counter for top conversations in a time period"""
        CustomDate.assert_dates(start, end)
        start, end = CustomDate.from_date_string(start), CustomDate.from_date(CustomDate.from_date_string(end) + 1)
        rankings = Counter()

        for i in range(len(self)):
            convo = self.get_convo(i + 1)
            name = convo._name.title()
            rankings[name] = 0
            for person, msg, date in convo:
                if start <= date <= end:
                    rankings[name] += 1

        return rankings

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

    def total_emojis(self, only_me=True):
        """Returns the total raw_emojis in an aggragate sum of all your conversations
            Parameters:
                only_me (optional): Considers only your sent messages if True, otherwise both your sent and received
            Return:
                Counter object storing your emoji frequencies
        """
        res = Counter()
        for i in range(1, len(self) + 1):
            try:
                if only_me:
                    res += self.get_convo(i).raw_emojis(person=self.person)
                else:
                    res += self.get_convo(i).raw_emojis()
            except AssertionError:
                pass
        return res

    @staticmethod
    def help():
        """Responsively provides help for using MessageReader"""
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
                print(Fore.LIGHTCYAN_EX + Back.BLACK + '\"What can I do here??\"')
                print(Style.RESET_ALL + 'Good question. Here you can perform a variety of analysis on your facebook'
                                        ' conversations, '
                      'ranging from analyzing the words you use most frequently in your favorite chat, to stats '
                      'on who starts conversations the most in that spammy group chat, to rankings of total emoji '
                      'use in all your conversations combined, and much more.\n')
                print('If you\'re primarily interested in viewing graphs of message history, you might be better off '
                      'using the GUI version of this program. Exit this helper (choice 3) and type the command '
                      '`{0}`. Once you\'re out of this python session, run the command `{1}`'
                      .format(color_method('exit()'), color_method("python3 fancy_playground.py")))
                print()
                print('If you\'re looking to get into the nitty gritty analysis of your facebook converation history, '
                      'well this is the place for you. To get information on analyzing your data, pick choices 1 or 2 '
                      'below')

            elif choice == '1':
                # Helps users view a list of conversations they can analyze
                print("Option 1: Viewing a list of conversations you can analyze\n")
                print(Fore.RED + '*', end=' ')
                print('To view a list of conversations that you can analyze, exit this helper and execute the '
                      'command `{0}`'.format(color_method('m.print_names()')))
                print(Fore.RED + '*', end=' ')
                print('To get more options on printing conversations, exit the helper and execute `{0}`. This is '
                      'only if you plan on doing fancy stuff'
                      .format(color_method('help(m.print_names)')))
                print('\nAfter picking a conversation to analyze, see option (2) below')

            elif choice == '2':
                # Helps users see how to grab a specific conversation
                print(Fore.RED + '*', end=' ')
                print('To analyze a specific conversation, you must retrieve it in one of 3 main ways:')
                print(Fore.GREEN + 'a)', end=' ')
                print('Print to the screen the ordered list of conversations (see choice 1) and find the rank of'
                      ' the conversation you would like. Then save that conversation to variable by executing the '
                      'command `{0}{1}`'.format(color_method('variable_name = '),
                                                color_method('m.get_convo(rank_of_desired_convo)')))
                print(Fore.GREEN + 'b)', end=' ')
                print('Get the conversation you would like by searching for it\'s name, e.g. executeing the command '
                      '`{0}{1}`'.format(color_method('variable_name = '),
                                        color_method('m.get_convo(\'bob smith, sally brown\')')))
                print(Fore.GREEN + 'c)', end=' ')
                print('Get the conversation you would like by searching for it\'s name as a list, e.g.'
                      ' executing the command `{0}{1}`'
                      .format(color_method('variable_name = '),
                              color_method('m.get_convo([\'both smith\', \'sally brown\'])')))
                print()
                print('Once you have your desired conversation, to get additional help analyzing it execute '
                      '`{0}`'.format(color_method('help(variable_name_from_above)')))

                print('\n\n...would you like an example? [Y/n]')

                # Describes an example of how to grab a conversation
                if user_says_yes():
                    print(Fore.LIGHTRED_EX + "\nEXAMPLE)")
                    print("Let\'s say I want to see my top 3 conversations. I can do this with command "
                          "`{0}`, where the 3 tells the program to print my top 3 contacts (ordered "
                          "by total number of messages sent and received; for more options do `{1}`)"
                          .format(color_method('m.print_names(3)'), color_method('help(m.print_names)')))
                    print("The above would go something like this:\n")

                    print(Fore.LIGHTBLACK_EX + ">>> m.print_names(3)\n"
                          "1) Sally Brown, Your Name\n"
                          "2) Bob Smith, Your Name\n"
                          "3) Your Name, Edward Newgate\n")
                    print("Now if I'd like to analyze my chat with Edward, I should first capture our conversation in "
                          "the following way:\n")
                    print(Fore.LIGHTBLACK_EX + ">>> edward = m.get_convo(3)\n")
                    print("Here, we use the `{0}` method to retrieve our conversation. The 3 corresponds to "
                          "our 3rd most contacted person from the `{1}` method"
                          .format(color_method("get_convo()"), color_method("print_names()")))
                    print("Additionally, the fact that we used the variable name \"edward\" is arbitrary. Any name can "
                          "be used, I've just fallen into the habit of naming conversation variables after the "
                          "name of the conversation, so it\'s easy to remember later")
                    print("\nOnce we\'ve successfully saved the chat we'd like, we can proceed to analyze it by "
                          "executing the command `{0}` (replace edward with whatever variable name you used)"
                          .format(color_method('edward.help()')))

            condition = choice != '3'
            if condition:  # We're continuing for another round
                print('\nContinue getting help? [Y/n]')
                if not user_says_yes():
                    return

            clear_screen()

    def _raw_rank(self, convo_name):
        """Returns the rank of the particular conversation, or None if not found"""
        assert type(convo_name) in [str, list, ConvoReader], "You must pass a Conversation name or ConvoReader object"
        if type(convo_name) is ConvoReader:
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


def join(lst, split=""):
    res = ""
    for i in range(len(lst) - 1):
        res += str(lst[i]) + split
    return res + lst[-1]


def contents_equal(lst1, lst2):
    if len(lst1) != len(lst2):
        return False
    for ele in lst1:
        if ele not in lst2:
            return False
    return True
