from collections import Counter
import shutil
import os
import random
from colorama import Fore, init


from functions.convoreader import ConvoReader
from functions.customdate import CustomDate

init(autoreset=True)


class MessageReader:

    def __init__(self):
        with open('data/data.txt', mode='r', encoding='UTF8') as f:
            self.data = eval(f.readline())
            self.download = f.readline()
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
            while True:
                choice = input('> ').lower()
                if choice in ['y', 'yes', 'n', 'no']:
                    break
            print()
            if choice in ['no', 'n']:
                return

        occurrences = 0  # number of occurances that are being swapped. Just so the user knows
        for person, msg, date in convo:
            if person == old_name:
                occurrences += 1
        print("Swapping {0} for {1} will result in {2} changes. Would you like to proceed? [Y/n]"
              .format(old_name, new_name, occurrences))

        # Does the user really want to continue after getting information
        while True:
            choice = input("> ").lower()
            if choice in ['y', 'yes', 'n', 'no']:
                break
        if choice in ['n', 'no']:
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
        while True:
            choice = input('> ').lower()
            if choice in ['n', 'no']:
                return
            if choice in ['yes', 'y']:
                break
        # user input: should we continue?

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

    def total_emojis(self, only_me=True):
        """Returns the total emojis in an aggragate sum of all your conversations
            Parameters:
                only_me (optional): Considers only your sent messages if True, otherwise both your sent and received
            Return:
                Counter object storing your emoji frequencies
        """
        res = Counter()
        for i in range(1, len(self) + 1):
            try:
                if only_me:
                    res += self.get_convo(i).emojis(person=self.person)
                else:
                    res += self.get_convo(i).emojis()
            except AssertionError:
                pass
        return res

    @staticmethod
    def help():
        condition = True
        while condition:
            print('Please select which feature you would like help with:\n')

            print('1) Viewing a list of conversations')
            print('2) Analyzing a specific conversation')
            print('3) Exit helper\n')

            choice_condition = True
            while choice_condition:
                choice = input('> ')
                choice_condition = choice not in [str(i) for i in range(1, 4)]
            print()

            if choice == '1':
                print('* To view a list of conversations, exit this helper and execute the command \"m.print_names()\"')
                print('* To get more information about printing conversations, exit the helper and execute'
                      ' \"help(m.print_names)\"')
                print('\n')
            elif choice == '2':
                print('* To analyze a specific conversation, you must retrieve it in one of 3 main ways:')
                print('a) Print to the screen the ordered list of conversations (see choice 1) and find the rank of'
                      ' the conversation you would like. Then save that conversation to variable by executing the '
                      'command \"variable_name = m.get_convo(rank_of_desired_convo)\"')
                print('b) Get the conversation you would like by searching for it\'s name, e.g. executeing the command '
                      '\"variable_name = m.get_convo(\'bob smith, sally brown\')\"')
                print('c) Get the conversation you would like by searching for it\'s name as a list, e.g.'
                      ' executing the command \"variable_name = m.get_convo([\'both smith\', [\'sally smith\'])\"')
                print()
                print('Once you have your desired conversation, to get additional help analyzing it execute '
                      '\"help(variable_name_from_above)\"')

            condition = choice != '3'

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
