from collections import Counter
import shutil
import os
import random
import ast
import inspect
import re
import json

from colorama import Fore, Back, Style, init

from functions.setup_functions import (
    PreferencesSearcher, clear_screen, user_says_yes, fit_colored_text_to_console, one_line, data_as_json
)
from functions.baseconvoreader import BaseConvoReader
from functions.convoreader import ConvoReader, color_method, get_user_choice_from_range
from functions.guiconvoreader import GUIConvoReader
from functions.customdate import CustomDate

init(autoreset=True)


class MessageReader:

    def __init__(self, preload_conversations=False):
        with open('data/data.json', mode='r', encoding='UTF8') as f:
            try:
                all_data = f.read()
            except Exception as e:
                print(Fore.LIGHTRED_EX + Back.BLACK + "An error occurred when reading in your data file. Please make "
                                                      "sure setup.py finished properly" + Style.RESET_ALL)
                raise e

        all_data = json.loads(all_data)
        self.data = all_data['conversation_data']
        self.download = all_data['footer']

        tmp_preference = all_data['preferences']
        tmp_contacted = tmp_preference['contacted']
        new_contacted = dict()
        for key, val in tmp_contacted.items():
            new_contacted[key] = (val[0], CustomDate(val[1]))
        tmp_preference['contacted'] = new_contacted

        self.quick_stats = PreferencesSearcher(tmp_preference)

        self.names = self._get_convo_names_freq()
        self.person = " ".join(self.download.split(' ')[2:-8])
        self.download_date = CustomDate(" ".join(self.download.split()[-7:]))
        self.first_chat_date = self._get_first_chat_date()
        self._edits = []

        self.convo_readers = {}
        if preload_conversations:
            for name in self.names:
                self.convo_readers[name] = self.get_convo(name)

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

    def get_convo(self, people) -> ConvoReader:
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
            if people < 0:
                people += len(self)
            if self.names[people - 1] not in self.convo_readers:
                self.convo_readers[self.names[people - 1]] = \
                    ConvoReader(self.names[people - 1], self.data[self.names[people - 1]], people)
            return self.convo_readers[self.names[people - 1]]

        if type(people) is str:
            people = people.title().split(', ')
        else:
            people = list(map(lambda x: x.title() if 'facebook' not in x else x, people))
        for i in range(len(self)):
            name = self.quick_stats.get_name(i + 1, 'length')  # get names sorting by number of messages
            if contents_equal(name.split(', '), people):
                if name not in self.convo_readers:
                    self.convo_readers[name] = ConvoReader(name, self.data[name], i + 1)
                return self.convo_readers[name]
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
        """Prints to the console the rank of the conversation passed, based on the number of messages for the chat
        Parameters:
            convo_name: (str|list<str>|ConvoReader) A representation of the conversation, either as a string e.g
                        "my name, your name", a list of names e.g. ["your name", "my name"], or a ConvoReader object
        """
        try:
            res = self.raw_rank(convo_name)
            if res is not None:
                if isinstance(convo_name, str):
                    name = convo_name.title()
                    length = len(self.get_convo(convo_name))
                elif isinstance(convo_name, list):
                    name = ', '.join(sorted(convo_name)).title()
                    length = len(self.get_convo(convo_name))
                else:  # if isinstance(convo_name, ConvoReader)
                    name = convo_name._name.title()
                    length = len(convo_name)
                print("{rank}) {name} - {length:,}".format(rank=res, name=name, length=length))
            else:
                print("A conversation for {0} was not found"
                      .format(convo_name.get_people if isinstance(convo_name, ConvoReader) else str(convo_name)))
        except AssertionError as e:
            print(e)

    def raw_rank(self, convo_name) -> int:
        """Returns the rank of the particular conversation, or None if not found"""
        assert type(convo_name) in [str, list,
                                    ConvoReader], "You must pass a Conversation name or ConvoReader object"
        if isinstance(convo_name, BaseConvoReader):
            return self.raw_rank(convo_name._name.split(', '))
        if type(convo_name) == list:
            for i, name in enumerate(convo_name):
                assert type(name) == str, "Your list must contain strings corresponding to names of people"
                convo_name[i] = name.title()
        elif type(convo_name) == str:
            convo_name = convo_name.title().split(', ')
        for i, name in enumerate(self.names):
            if contents_equal(convo_name, name.title().split(', ')):
                return i + 1

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
            verbose (optional): (Boolean) Whether to print out a confirmation string upon completion. Defaults to True
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
                     "includes {people}".format(rank=self.raw_rank(convo), people=convo.get_people()))
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
        if new_name not in previous_name.lower().split(', '):  # use split so substrings aren't false positives
                            # aka 'sean lo' is in 'sean lobo, bob builder' but not 'sean lobo, bob builder'.split()

            # if new_name is not already present, swap the old_name for it
            updated_name = previous_name.replace(self.custom_title(old_name), self.custom_title(new_name))
        else:
            # Take the previous_name and cut out old_name, instead of
            # replacing with new_name since new name is already in the name
            updated_name = ", ".join([name for name in previous_name.split(', ') if name != self.custom_title(old_name)])
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
                previous_data[i] = tuple([self.custom_title(new_name), msg, date])

        self._edits.append(self.raw_rank(previous_name))
        del self.data[previous_name]  # deletes the old data from self.data
        del self.convo_readers[previous_name]  # deletes the old convoreader from the cache
        self.data[updated_name] = previous_data  # updates self.data with the new data
        self.names = self._get_convo_names_freq()  # update self.names with new keyset

        chunk = ("The specified changes have been made. Note that these changes will only last the duration "
                 "of this python session. If you would like to make the changes permanent, call m.save_convo_edits()")
        if verbose:  # print confirmation if in verbose mode
            print(fit_colored_text_to_console(chunk, "m.save_convo_edits()"))

    def edit_all_occurrences(self, old_person, new_person, force=False, verbose=True):
        """Edits every conversation with old_person, replacing them with new_person
        Parameters:
            old_person: (str) the name of the person to be replaced
            new_person: (str) the name to replace occurrences of old_person with
            force (optional): (Boolean) Whether to prompt the user about the change
            verbose (optional): (Boolean) Whether to print out a confirmation string upon completion. Defaults to True
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
            chunk = ("Changing all conversations would result in {num_changes} conversation changes. "
                     "Would you like to proceed? [Y/n]".format(num_changes=change_count))
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

        data = data_as_json(self.data, self.download, PreferencesSearcher.from_msgs_dict(self.data).preferences)
        with open('data/data.json', mode='w', encoding='utf-8') as f:
            f.write(data)

    def save_subset_of_data(self, conversation_names, file_name, skip_messages=False):
        """Saves to a file the data for the conversations specified
        Parameters:
            conversation_names: a list of: integer indexes corresponding to the conversation you would like,
                or comma separated strings of names e.g. 'my name, your name',
                or lists of names as strings e.g. ['your name', 'my name']
            file_name: a string filename for the data to be written to
            skip_messages (optional): (boolean) If true saves a version of the data where all messages are empty strings
                                        This data can still be used for graph annotations. Defaults to False
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
                    "{0} already exists, continuing would override this data. Would you like to continue? [Y/n]"
                        .format(file_name)
                )
                if not user_says_yes():
                    return

            convo_ranks = [self.raw_rank(self.get_convo(name)) for name in conversation_names]

            new_data = dict()
            for rank in convo_ranks:
                if not skip_messages:
                    new_data[self.names[rank - 1]] = self.data[self.names[rank - 1]]
                else:
                    data = [(person, '', date) for person, message, date in self.data[self.names[rank - 1]]]
                    new_data[self.names[rank - 1]] = data

            download = self.download
            quick_settings = PreferencesSearcher.from_msgs_dict(new_data)

            writable_data = data_as_json(new_data, download, quick_settings)

            with open(file_name, mode='w', encoding='utf-8') as f:
                f.write(writable_data)
        except AssertionError as e:
            print(e)
            return

    def update_all_facebook_names(self):
        """Prompts the user to give the real names of all facebook names (e.g. '23524534634@facebook.com') and then
        updates those names. Goes through all names in sorted order of the numbers before @facebook. To update a
        specific contact use update_select_facebook_names()
        """
        def check_data_file(data):
            r = re.compile("\d+@facebook.com")
            assert isinstance(data, dict), "file must be a python dictionary"
            for key, val in data.items():
                assert isinstance(key, str) and r.fullmatch(key), (
                    "All keys in data must be facebook strings (e.g. '2358249589240@facebook.com'"
                )
                assert isinstance(val, str), "All mapped values in data must be names as strings"

                data[key] = val.title()  # ensure all strings are title case after verifying this element

        exit_color = Fore.LIGHTMAGENTA_EX + Back.BLACK
        continue_color = Fore.LIGHTGREEN_EX + Back.BLACK

        facebook_names = self.raw_facebook_names()

        chunk1 = (
            "Here you can update facebook names (e.g. 23023502345@facebook.com) with the true names they belong "
            "to. To find out what account a number belongs to go to facebook.com/number and see if you are "
            "redirected to a friend's account. If so, that is the account."
        )
        chunk2 = (
            "You have a total of {} facebook names in your conversation. You will now be prompted to update as "
            "many of these as you would like. ".format(len(facebook_names))
        )
        print(Fore.LIGHTGREEN_EX + Back.BLACK + "Update Facebook Names" + Style.RESET_ALL)
        print(fit_colored_text_to_console(chunk1))
        print()

        previous_mapping = dict()
        if os.path.isfile('data/facebook_name_mapping.txt'):  # we can use a previous data file
            mapping_text = (
                "A previous facebook_name_mapping file was found, would you like to load this data to help expedite "
                "the process? [Y/n]"
            )
            print(one_line())
            print(fit_colored_text_to_console(mapping_text))
            print('\n')
            if user_says_yes():  # the user wants to use this data file
                try:
                    with open('data/facebook_name_mapping.txt', mode='r', encoding="utf-8") as f:
                        previous_mapping = ast.literal_eval(f.read())
                except (SyntaxError, TypeError, ValueError) as e:  # there was an error loading in the data file
                    previous_mapping = dict()
                    error_loading_text = (
                        "There was an error when loading your previous mapping. If you would like to use this data "
                        "ensure the file is formatted as a proper python dictionary. Now aborting data loading. "
                        "Would you like to view the error message? [Y/n]"
                    )
                    print(fit_colored_text_to_console(error_loading_text))
                    if user_says_yes():
                        print()
                        print("Error:", e)
                else:  # The data file was correctly loaded
                    try:  # ensure that the loaded data is of the proper form
                        check_data_file(previous_mapping)
                    except AssertionError as e:
                        previous_mapping = dict()
                        invalid_syntax_text = (
                            "The data files was properly loaded but contained invalid syntax for use in this method. "
                            "If you would like to use this data ensure that the structure of the file is valid. Now "
                            "aborting data loading. Would you like to view the error message received when validating "
                            "structure? [Y/n]"
                        )
                        print(fit_colored_text_to_console(invalid_syntax_text))
                        if user_says_yes():
                            print(e)
                    else:  # the data file was loaded and has proper structure
                        print()
                        print(one_line())
                        print()
                        print("The data file was properly loaded. Below is its data:")
                        print()

                        key_set = sorted(previous_mapping.keys())

                        print(exit_color + "-1) Cancel data loading")
                        print(continue_color + "0) Continue")
                        print()
                        for i, key in enumerate(key_set):  # print out the dictionary's elements
                            val = previous_mapping[key]
                            print("{}) {fb_name} ---> {new_name}".format(i + 1, fb_name=key, new_name=val))

                        print()
                        prompt = (
                            "Select a conversation if you would like to edit its mapping, (0) continue to proceed with "
                            "the current mappings, or (-1) cancel to discard these data file values and proceed. "
                            "[-1 to {}]"
                            .format(len(previous_mapping))
                        )

                        to_user_input = False
                        while not to_user_input:
                            # this outer loop is used to allow the user to confirm whether they would like to continue /
                            # delete previous_mappings

                            print(fit_colored_text_to_console(prompt))
                            choice = get_user_choice_from_range(-1, len(previous_mapping))
                            print()
                            # While loop allows users to edit elements of previous mapping, or remove them entirely
                            while choice not in [-1, 0]:
                                key_set = sorted(previous_mapping.keys())
                                key = key_set[choice - 1]

                                while True:
                                    chunk = (
                                        "Type the name you would like to use instead of {name}, or 'delete' to delete "
                                        "this value from the mapping".format(name=previous_mapping[key])
                                    )
                                    print(fit_colored_text_to_console(chunk))
                                    name = input("> ").title()

                                    if name == 'Delete':
                                        del previous_mapping[key]
                                        break

                                    print()
                                    print("Would you like to confirm {}? [Y/n]".format(name))
                                    if user_says_yes():
                                        previous_mapping[key] = name
                                        break

                                print(one_line())
                                print(exit_color + "-1) Cancel data loading")
                                print(continue_color + "0) Continue")
                                for i, key in enumerate(key_set):  # print out the dictionary's elements
                                    val = previous_mapping[key]
                                    print("{}) {fb_name} ---> {new_name}".format(i + 1, fb_name=key, new_name=val))
                                print(fit_colored_text_to_console(prompt))
                                choice = get_user_choice_from_range(-1, len(previous_mapping))
                                print()

                            if choice == -1:
                                print("Are you sure you would like to discard the data file? [Y/n]")
                                if user_says_yes():
                                    previous_mapping = dict()
                                    to_user_input = True
                            elif choice == 0:
                                print("Are you sure you would like to continue to user input? [Y/n]")
                                if user_says_yes():
                                    to_user_input = True

            print(one_line())

        print(fit_colored_text_to_console(chunk2))
        print('\n')
        input("Press enter to continue to user input ")

        value = None
        name_mapping = previous_mapping
        for i, name in enumerate(facebook_names):
            # go through all facebook names, until we complete them all or the user wants to quit

            if name not in name_mapping.keys():  # if we don't already have a value for this name
                number = name.split("@")[0]
                print(one_line())
                print(fit_colored_text_to_console("({0}) {num} ---> ?".format(i + 1, num=number),
                                                  "({})".format(i + 1)))
                chunk = (
                    "Type one of the following: (1) the name you find at facebook.com/{num} , (2) 'skip' to skip this "
                    "name, or (3) 'quit' to skip the remaining names. Note that all names are converted "
                    "to title case".format(num=number)
                )
                print(fit_colored_text_to_console(chunk))

                while True:
                    print()
                    print("Type your value")
                    value = input("> ").title()

                    if value == "Skip" or value == "Quit":
                        break

                    print()
                    print("Would you like to confirm: {facebook_name} == {user_name}? [Y/n]".
                          format(facebook_name=name, user_name=value))
                    if user_says_yes():
                        break

                if value == "Quit":
                    break

                if value != "Skip":
                    name_mapping[name] = value
                    print()

        print(one_line())
        print("Below is a summary of the names you provided:")
        print()

        print(continue_color + "0) Continue" + Style.RESET_ALL)
        key_set = sorted(name_mapping.keys())
        for i, key in enumerate(key_set):
            val = name_mapping[key]
            print("{index}) {facebook_name} ---> {name}".format(index=i + 1, facebook_name=key, name=val))

        print()
        print("Choose a number if you would like to edit it, or 0 to continue:")
        num = get_user_choice_from_range(0, len(name_mapping))

        while num != 0:
            key = key_set[num - 1]

            while True:
                chunk = "Type the name you would like to use instead of {name}, or 'delete' to delete this value"\
                    .format(name=name_mapping[key])
                print(fit_colored_text_to_console(chunk))
                name = input("> ").title()

                if name == 'Delete':
                    del name_mapping[key]
                    key_set = sorted(name_mapping.keys())
                    break

                print()
                print("Would you like to confirm {}? [Y/n]".format(name))
                if user_says_yes():
                    name_mapping[key] = name

            print(one_line())
            print("Choose a number if you would like to edit it, or 0 to continue:")
            num = get_user_choice_from_range(0, len(name_mapping))

        # Write mapping to file
        if os.path.isfile('data/facebook_name_mapping.txt'):
            exist_promt = (
                "A file named `facebook_name_mapping.txt` already exists in the data directory. Continuing will "
                "override the file. If you would like to save your old version, rename or move it elsewhere."
            )
            print(fit_colored_text_to_console(exist_promt))
            input("Press enter when ready ")
        with open('data/facebook_name_mapping.txt', mode='w', encoding='utf-8') as f:
            f.write(str(name_mapping))

        self._update_facebook_names(name_mapping)

    def update_select_facebook_names(self):
        """Interactive method to allow users to update specific facebook names (e.g. '2353424235234@facebook.com')
        with the account names they belong to. Users will presumably look up the accounts online, e.g.
        2353424235234@facebook.com --> the name of the account at facebook.com/2353424235234. To update all names
        in a row use update_all_facebook_names()
        """
        facebook_names = self.raw_facebook_names()
        choice = None
        while choice != 0:
            print("0) Exit")
            print("1) View a list of names and select one to edit")
            print("2) Enter a facebook name and updated account name")
            print()
            print("Select your option [0-2]")
            choice = get_user_choice_from_range(0, 2)

            if choice == 1:
                print('\n' + one_line())

                print("0) Cancel")
                for i, fb_name in enumerate(facebook_names):
                    print("{index}) {name}".format(index=i + 1, name=fb_name))
                print()
                print("Select the facebook_name you would like to edit, or 0 to cancel")
                name_index = get_user_choice_from_range(0, len(facebook_names))

                if name_index != 0:
                    replacement = None
                    while True:
                        print()
                        print("Type the name you would like to replace {fb_name} with, or 'cancel' to cancel"
                              .format(fb_name=facebook_names[name_index - 1]))
                        replacement = input("> ").title()

                        if replacement == 'Cancel':
                            break

                        print("Would you like to confirm: {fb_name} ---> {replacement}? [Y/n]"
                              .format(fb_name=facebook_names[name_index - 1], replacement=replacement))
                        if user_says_yes():
                            break

                    print(one_line())
                    if replacement != 'Cancel':
                        self.edit_all_occurrences(facebook_names[name_index - 1], replacement,
                                                  force=True, verbose=False)
                else:
                    print()
                    print(one_line())
                    print()

            elif choice == 2:
                print('\n' + one_line())

                fb_name = False
                while True:
                    chunk = ("Type the account number of the facebook name you would like to update, e.g. if the full "
                             "name is '23582450923@facebook.com' type '23582450923' (without the quotes)")
                    print(fit_colored_text_to_console(chunk))
                    fb_name = input("> ") + '@facebook.com'
                    print()

                    if fb_name in facebook_names:
                        break
                    else:  # the user's number isn't present, tell them and loop back
                        chunk = ("'{fb_name}' isn't in your list of facebook names. (to "
                                 "see a list of names choose no and then choose option 1)".format(fb_name=fb_name))
                        print(fit_colored_text_to_console(chunk))
                        print("Would you like to try again? [Y/n]")
                        if not user_says_yes():

                            print()
                            print(one_line())
                            print()
                            fb_name = False
                            break

                if isinstance(fb_name, str):  # the user specified a valid name
                    while True:
                        print()
                        print("Type the name you would like to replace {fb_name} with, or 'cancel' to cancel"
                              .format(fb_name=fb_name))
                        replacement = input("> ").title()

                        if replacement == 'Cancel':
                            break

                        print("Would you like to confirm: {fb_name} ---> {replacement}? [Y/n]"
                              .format(fb_name=fb_name, replacement=replacement))
                        if user_says_yes():
                            self.edit_all_occurrences(fb_name, replacement, force=True, verbose=False)
                            break

    def _update_facebook_names(self, name_mapping, force=True, verbose=False):
        """Replaces all occurrences of facebook names with their real names, using the data in name_mapping
        Parameters:
            name_mapping: (dict) A mapping of facebook names (e.g. 1384239872@facebook.com) to their real names
        """
        assert isinstance(name_mapping, dict), (
            "name_mapping must be a dictionary with keys being facebook names (e.g. 23425323452@facebook.com) and "
            "values being the account name corresponding to the integer"
        )
        for key, val in name_mapping.items():
            self.edit_all_occurrences(key, val, force=force, verbose=verbose)

    # ------------------------------------------------   EDITING DATA  ----------------------------------------------- #

    # ----------------------------------------------   ANALYTIC METHODS  --------------------------------------------- #

    def top_conversations(self, start=None, end=None, limit=10):
        """Prints a ranking of top conversations in a time period
        Parameters:
            start (optional): The date string representing the first day to start counting from
                                (in the format {month}/{day}/{year}. Defaults to the first date messages were sent
            end (optional): The date string for the last day to count. Defaults to the download date
            limit (optional): An integer representing the number of conversations to print, or False to display all
        """
        try:
            rankings = self.raw_top_conversations(start=start, end=end)
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
            print("{0}{1} - {2:,}".format(' ' * (MAX_INT_LEN - len(str(i))), convo, freq))
            i += 1

    def raw_top_conversations(self, start=None, end=None):
        """Returns a Counter object holding the names of conversations mapped to their message frequency
        in a time period
        Parameters:
            start (optinal): (str) A date string for the beginning of the desired period, in the form
                            "{month}/{day}/{year}". Defaults to the first date messages were sent
            end (optional): (str) A date string for the end of the desired period, in the same form as start.
                            Defaults to the download date
        Return:
            a Counter object with keys being the title case names of conversations and values being the number of
              messages sent during the specified period
        """
        CustomDate.assert_dates(start, end)
        start = CustomDate.from_date_string(start) if start is not None else self.first_chat_date
        end = CustomDate.from_date_string(end).plus_x_days(1) if end is not None else self.download_date
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
        """Prints the emojis use of all conversations combined to the console
        Parameters:
            only_me (optional): (Boolean) Whether to include only your emojis use or everyone's in total.
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
                Counter object storing your emojis frequencies
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

    def messages_graph(self, only_me=False, forward_shift=0, start=None, end=None):
        """Prints to the console a graph of aggregate message frequency by day for all conversation data combined
        Parameters:
            only_me (optional): (Boolean) Whether the data should only reflect messages sent by you
            forward_shift (optional): (int) The number of minutes past 11:59pm that count for the previous date.
                                            Example, if forward_shift == 30, a messages sent on July 5th until 12:29am
                                            will count as being sent on July 4th.
            start (optional): (str) the date string for the start date of the graph, in the form "{month}/{day}/{year}"
            end (optional): (str) the date string for the end date of the graph
        """
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
                messages_data = self.get_convo(i).raw_msgs_graph(contact=contact, forward_shift=forward_shift)
                total.update({key: val for key, val in messages_data})
            except AssertionError:
                pass

        result = sorted(total.most_common(), key=lambda x: x[0])
        return result[start_index: end_index]

    def raw_facebook_names(self):
        """Returns a list of all facebook names in chats, e.g. 10232342934@facebook.com, but with a working number"""
        facebook_person = re.compile("\d+@facebook.com")
        res = set()
        for i in range(1, len(self) + 1):
            convo = self.get_convo(i)
            for person in convo.get_people():
                if facebook_person.fullmatch(person):
                    res.add(person)
        return sorted(list(res))

    # ----------------------------------------------   ANALYTIC METHODS  --------------------------------------------- #

    @staticmethod
    def help():
        """Provides help for using MessageReader based on user input"""
        clear_screen()
        print("Welcome to the help function for MessageReader\n\n")

        while True:  # Continue's offering help until the user escapes with option 4
            print(Fore.LIGHTMAGENTA_EX + Back.BLACK + 'Select which feature you would like help with:')
            print()
            choices = [
                Fore.LIGHTCYAN_EX + Back.BLACK + '0) What can I do here??' + Style.RESET_ALL + '\n',
                '1) Viewing a list of conversations you can analyze',
                '2) Getting started analyzing a specific conversation',
                '3) Aggregate data analytic methods',
                Fore.LIGHTRED_EX + Back.BLACK + '4) Exit helper' + Style.RESET_ALL,
            ]
            for line in choices:
                print(fit_colored_text_to_console(line))
            print()
            print("Choose a number between 0 and {length}".format(length=len(choices) - 1))
            # Which choice would the user like help with?

            choice = get_user_choice_from_range(0, 4)

            if choice == 4:
                return

            clear_screen()
            # Gets the user's choice of 0-3 and clears the screen after in preparation

            if choice == 0:
                # Helps user with an idea of what they can do with a messagereader
                print("Option 0:")
                print(Fore.LIGHTCYAN_EX + Back.BLACK + '\"What can I do here??\"' + Style.RESET_ALL)
                chunk1 = ('Good question. Here you can perform a variety of analysis on your facebook conversations, '
                          'from analyzing the words you use most frequently in your favorite chat, to stats '
                          'on who starts or ends conversations the most, to rankings of total emojis use in all your '
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

            elif choice == 1:
                # Helps users view a list of conversations they can analyze
                print("Option 1: Viewing a list of conversations you can analyze")
                print(one_line())

                chunk1 = ('To view a list of conversations that you can analyze, exit this helper and execute the '
                          'command `m.print_names()`. This will print to the console a list of all contacts you '
                          'have messaged, sorted with decreasing number of messages. Since you might have many '
                          'contacts, you can optionally pass an integer limiting the conversations printed, for '
                          'example `m.print_names(10)` to print your top 10 conversations')
                chunk2 = ('To get more options on printing conversations, exit the helper and execute '
                          '`help(m.print_names)`. This is only if you plan on doing fancy stuff')

                print(fit_colored_text_to_console(chunk1, "m.print_names()", "m.print_names(10)"))
                print()
                print(fit_colored_text_to_console(chunk2, "help(m.print_names)"))
                print()
                print('After deciding on a conversation to analyze, see option (2) below on how to get started, '
                      'as well as an example')

            elif choice == 2:
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
                    print()
                    print(Fore.LIGHTRED_EX + Back.BLACK + "EXAMPLE)" + Style.RESET_ALL)

                    chunk1 = ("Let\'s say I want to see my top 3 conversations. I can do this with command "
                              "`m.print_names(3)`, where the 3 tells the program to print my top 3 contacts "
                              "(ordered by total number of messages sent and received; for more options do "
                              "`help(m.print_names)`)")
                    print(fit_colored_text_to_console(chunk1, "help(m.print_names)", "m.print_names(3)"))
                    print("\nThe above would go something like this:")

                    print(code_color + ">>> m.print_names(3)" + Style.RESET_ALL)
                    print(code_color + "1) Sally Brown, Your Name" + Style.RESET_ALL)
                    print(code_color + "2) Bob Smith, Your Name" + Style.RESET_ALL)
                    print(code_color + "3) Your Name, Edward Newgate" + Style.RESET_ALL)
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
                    chunk4 = ("Note that as stated previously, we could also retrieve this conversation by using "
                              "`m.get_convo('edward newgate, your name')` or `m.get_convo(['edward newgate', 'your "
                              "name'])`")
                    print(fit_colored_text_to_console(chunk3, "print_names()", "get_convo(3)"))
                    print(fit_colored_text_to_console(chunk4, "m.get_convo('edward newgate, your name')",
                                                      "m.get_convo(['edward newgate', 'your name'])"))
                    print()

                    chunk4 = ("Once we\'ve successfully saved the chat we'd like, we can proceed to analyze it by "
                              "executing the command `edward.help()` (replace edward with whatever variable name"
                              " you used)")
                    print(fit_colored_text_to_console(chunk4, "edward.help()"))

            elif choice == 3:
                    # Give info on the analytic methods of messagereader
                keep_going = True
                while keep_going:
                    print('Option 3: Aggregate data analytic methods')
                    print(one_line())

                    method_key = lambda method: method.__name__
                    visualization_methods = sorted([MessageReader.messages_graph, MessageReader.emoijs,
                                                    MessageReader.top_conversations, MessageReader.rank],
                                                   key=method_key)

                    raw_data_methods = sorted([MessageReader.raw_messages_graph, MessageReader.raw_emojis,
                                               MessageReader.raw_top_conversations, MessageReader.raw_rank],
                                              key=method_key)

                    editing_data_methods = sorted([MessageReader.save_subset_of_data,
                                                   MessageReader.save_convo_edits,
                                                   MessageReader.edit_all_occurrences,
                                                   MessageReader.edit_convo_participants,
                                                   MessageReader.update_all_facebook_names,
                                                   MessageReader.update_select_facebook_names], key=method_key)

                    # the length of the string representing the length of each list, plus a bit of padding,
                    len_longest_str = len(str(len(visualization_methods) + len(raw_data_methods) +
                                              len(editing_data_methods))) + 1

                    chunk1 = ("Below are a list of analytic methods you can perform with the MessageReader object. You "
                              "can call each of the following methods from the object m, e.g. if you see the method "
                              "'test' listed below, you can call it with the command `m.test()`. Note that all of "
                              "these methods perform aggregate analysis, that is information for all conversations "
                              "combined. If you would like information on specific conversations then see options (1) "
                              "and (2) on how view a list of conversations and grab a desired one, respectively.")
                    chunk2 = "Visualization methods - methods that print information to the console:"
                    chunk3 = ("Raw data methods - methods that return the data (some of these are used by the "
                              "visualization methods)")
                    chunk4 = ("Conversation editing methods - methods that allow you to edit your conversation data "
                              "in case you find issues or errors")
                    print(fit_colored_text_to_console(chunk1, 'm.test()', "'test'"))
                    print()

                    print(Fore.LIGHTRED_EX + Back.BLACK + "0) Exit" + Style.RESET_ALL)
                    print()

                    print(fit_colored_text_to_console(chunk2))
                    # print the names of visualization_methods
                    for i, method in enumerate(visualization_methods):
                        method_name = color_method(method.__name__)
                        print('{0}){1}{2}'.format(str(i + 1), ' ' * (len_longest_str - len(str(i + 1)) + 1), method_name))

                    print()
                    print(fit_colored_text_to_console(chunk3))
                    # print the names of the raw_data methods
                    for i, method in enumerate(raw_data_methods):
                        method_name = color_method(method.__name__)
                        index = i + len(visualization_methods) + 1
                        print('{0}){1}{2}'.format(str(index),
                                                  ' ' * (len_longest_str - len(str(index)) + 1),
                                                  method_name))

                    print()
                    print(fit_colored_text_to_console(chunk4))
                    # print the names of editing_data
                    for i, method in enumerate(editing_data_methods):
                        method_name = color_method(method.__name__)
                        index = i + len(visualization_methods) + +len(raw_data_methods) + 1
                        print('{0}){1}{2}'.format(str(index),
                                                  ' ' * (len_longest_str - len(str(index)) + 1),
                                                  method_name))
                    print()

                    length = len(visualization_methods) + len(raw_data_methods) + len(editing_data_methods)
                    print("Select your option [0-{length}]".format(length=length))
                    method_choice = get_user_choice_from_range(0, length)

                    if method_choice != 0:
                        methods = visualization_methods + raw_data_methods + editing_data_methods
                        method_choice -= 1

                        print(one_line())
                        print()

                        if 'return' in methods[method_choice].__annotations__:
                            # in the form '(self, person=None) -> collections.Counter'
                            annotation = str(inspect.signature(methods[method_choice]))
                            # the part of the annotation up until the signature ends
                            end_method = annotation.find(' ->')
                            name = color_method(methods[method_choice].__name__ + annotation[:end_method])
                            name += color_method(annotation[end_method:])
                        else:
                            name = color_method(methods[method_choice].__name__ +
                                                str(inspect.signature(methods[method_choice])))

                        print(name)
                        print(inspect.getdoc(methods[method_choice]))

                        print('\n')
                        print("Would you like to view help for another method? [Y/n]")
                        keep_going = user_says_yes()
                        if keep_going:
                            clear_screen()
                    else:
                        keep_going = False
            print('\nContinue getting help? [Y/n]')
            if not user_says_yes():
                return

            clear_screen()

    def _get_first_chat_date(self) -> CustomDate:
        start_dates = []
        for i in range(len(self)):
            # the date of the first message for the ith chat
            start_dates.append(CustomDate(self.data[self.names[i]][0][2]))

        return min(start_dates)

    def _get_convo_names_freq(self):
        """Returns the list of title case names of conversations you have,
        sorted first in order of most chatted to least and second alphabetically"""
        return [ele for ele, _ in
                sorted([(key, len(val)) for key, val in self.data.items()],
                       key=lambda x: (-x[1], x[0]))]

    @staticmethod
    def custom_title(name):
        """Returns a title case version of name if name does not contain facebook in it"""
        if 'facebook' not in name.lower():
            return name.title()
        return name.lower()

    def __len__(self):
        return len(self.names)

    def __str__(self):
        return self.download

    def __repr__(self):
        return 'MessageReader()'


def contents_equal(lst1, lst2):
    if len(lst1) != len(lst2):
        return False
    filter = lambda x: x.lower()
    return sorted(map(filter, lst1)) == sorted(map(filter, lst2))
