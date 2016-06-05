from collections import Counter
import random

from functions.convoreader import ConvoReader
from functions.customdate import CustomDate


class MessageReader:

    def __init__(self):
        with open('data/data.txt', mode='r', encoding='UTF8') as f:
            self.data = eval(f.readline())
            self.download = f.readline()
        self.names = self._get_convo_names_freq()
        self.person = join(self.download.split(' ')[2:-8], split=" ")

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
