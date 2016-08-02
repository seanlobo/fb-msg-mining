import os
import shutil
import time
import textwrap
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style


from functions.customdate import CustomDate


init(autoreset=True)


def get_all_thread_containers(msg_html_path):
    """Returns a list of list of divs. Contains all information
    needed to get full conversation history for any conversation.

    Return type has the following structure:

    [[msg_div1, msg_div2, msg_div3],
     [msg_div1],
     [msg_div1, msg_div2, msg_div3, msg_div4]
     .
     .
     .
    ]

    each inner list has an arbitrary length. The elements of each
    inner list are div tags that contain 1 thread each

    A thread is a list of up to 10,000 messages between two people
    or one group. The conversation the thread belongs to can be
    found by:

    thread.contents[0]
    """
    try:
        text = open(msg_html_path, mode='r', encoding='UTF8')
    except OSError as err:
        print('OS error: {0}'.format(err))
        exit()

    # soup object that holds all of the html
    soup = BeautifulSoup(text, 'html.parser')

    # finds the outer div tag that holds all relevant information
    div_tag = soup.find('div', class_='contents')
    footer = soup.find('div', class_='footer').get_text()

    # creates a list containing elements whose div
    # tags hold the chat data
    all_divs = [] # list of list of divs [ [div, div], [div], ...]
    for div in div_tag("div", recursive=False):
        all_divs.append(div)

    return (all_divs, footer)


def get_all_threads_unordered(all_divs):
    """Returns a list of message_divs (threads) whose contents
    match the passed convo_name, or all message_divs by default

    Return type has the following structure:

    [thread1,
    thread2,
    thread3,
    .
    .
    .
    ]
    """
    all_divs, footer = all_divs
    thread_bucket = []
    for msg_container in all_divs:
        for msg_div in msg_container('div', class_="thread", recursive=False):
            thread_bucket.append(msg_div)

    return (thread_bucket, footer)


def get_messages_readable(thread, previous=None):
    """Returns a list of tuples of length 3. First element is person speaking,
    second message, third time
    """
    if previous is None:
        previous = []

    # list of all div ids for a certain message group
    # (each message group has max 10,000 messages)
    # each element (div id tag) has the time and person of the message
    div_ids = [div for div in thread('div', class_='message', recursive=False)]

    # a list of messages. Each element corresponds to the information in div_ids
    messages = [p for p in thread('p', recursive=False)]
    assert len(div_ids) == len(messages), 'div_ids and messages\
                                             have different lengths'

    for i in range(len(div_ids) - 1, -1, -1):
        # person who said the ith message
        person = [div for div in div_ids[i]('span', class_='user')][0].contents[0]

        # time ith message was sent at
        time = [div for div in div_ids[i]('span', class_='meta')][0].contents[0]

        try:
            msg = messages[i].get_text()
        except IndexError:
            msg = ''
        previous.append( (person, msg, time) )

    return previous


def get_all_msgs_dict(msg_html_path, unordered_threads, footer, times):
    """Returns the dictionary used by MessageReader"""
    conversation_color = Fore.LIGHTYELLOW_EX + Back.LIGHTBLACK_EX
    previous_color = Fore.LIGHTCYAN_EX + Back.BLACK
    current_color = Fore.LIGHTGREEN_EX + Back.BLACK
    are_same_color = Fore.LIGHTRED_EX + Back.BLACK

    def add_to_duplicate():
        """Helper method to add a message group to a DUPLICATE conversation"""
        nonlocal msgs, cur_thread, key, next_time, duplicate_index
        duplicate_num = 1  # the number of duplicate message groups (have the same people, aka name)
        # but in reality belong to different conversations

        added = False  # used so that we don't accidentally add something twice

        # while there exists another duplicate conversation in our list keep checking if the current
        # message group belongs to it. If we exit the while loop a new conversation is created with
        # "DUPLICATE #X appended to distinguish it, with X being the xth new duplicate conversation
        while (key + ', DUPLICATE #{0}'.format(duplicate_num)) in msgs and not added:
            new_name = key + ', DUPLICATE #{0}'.format(duplicate_num)

            # The time of the last message in the conversation for new_name
            prev_time = CustomDate(msgs[new_name][-1][2])

            if prev_time.distance_from(next_time) <= 0:
                # if our current conversation was during or after the last message in the new_name convo
                print(one_line())
                print()
                print(one_line())

                print("#{0} of {1} (at maximum) duplicate conversations. Some might be done for you behind the scenes."
                      .format(duplicate_index, num_duplicates))
                print(conversation_color + key)
                print(one_line() + "\n")

                print(previous_color + '# previous conversation end - length = {0:,}'.format(len(msgs[new_name]))
                      + Style.RESET_ALL)
                print_thread(msgs[new_name], end=True, padding=10)

                print(current_color + "\n# next conversation start - length = {0:,} (maximum possible length is 10,000)"
                      .format(len(cur_thread)) + Style.RESET_ALL)
                print_thread(cur_thread, start=True, padding=10)

                print('\n' + one_line())
                # Prints the last 5 messages of the previous message group and the first 5 message of
                # the current message group, both in RED with a BLACK background

                print(are_same_color + "\nAre these two chunks from the same conversation? You might have "
                                       "to look this up on facebook.com. [Y/n]" + Style.RESET_ALL)

                are_same = user_says_yes()
                # User input for whether the two message groups are in the same conversation

                if not are_same:
                    duplicate_num += 1  # if they aren't the same, increment duplicate_num and try again
                else:
                    # check to make sure the current message group hasn't already been added, otherwise add it
                    msgs[new_name].extend(cur_thread)
                    added = True
            else:
                # this conversation existed but was after our current one, so increment the number and try again
                duplicate_num += 1

        if not added:
            # if the current message group hasn't been added, add with a new duplicate #
            msgs[key + ', DUPLICATE #{0}'.format(duplicate_num)] = cur_thread
        duplicate_index += 1
        return

    def print_thread(thread, start=False, end=False, padding=5):
        """Prettily prints the thread passed from start to start + padding or end - padding to end"""
        if start:
            assert not end, "Either start or end can be True, not both"
        else:
            assert end, "Exactly one value from start and end must be true"
        assert isinstance(padding, int), "padding must be an integer"
        assert padding > 0, "padding must be greater than 0"

        if start:
            start = 0
            end = min(start + padding, len(thread))
            date_color = Fore.GREEN + Back.BLACK
        else:
            end = len(thread)
            start = max(0, end - padding)
            date_color = Fore.CYAN + Back.BLACK

        max_name_length = max(len(name) for name, _, _ in thread[start:end]) + 1
        for person, msg, date in thread[start:end]:

            print("{0:{align}{width}}: {1} | {2}"
                  .format(person, msg, date_color + date, align='<', width=max_name_length))
        return

    # Getting values if default arguments were left as default
    if unordered_threads is None or footer is None:
        all_thread_containers = get_all_thread_containers(msg_html_path)
        unordered_threads, footer = get_all_threads_unordered(all_thread_containers)

    msgs = dict()  # result we return
    duplicate_bucket = dict()  # temporarily holds duplicate conversations
    num_duplicates = 0
    for thread in unordered_threads:
        convo_name = clean_convo_name(thread.contents[0])
        cur_thread = get_messages_readable(thread)
        if convo_name not in msgs:
            # A conversation with the name of current message group does not exist, so it is added with no issues :D
            msgs[convo_name] = cur_thread

        else:  # Another conversation with this name been seen before, add to duplicate bucket if appropriate
            num_duplicates += 1
            if convo_name in duplicate_bucket:
                duplicate_bucket[convo_name].append(cur_thread)
            else:
                duplicate_bucket[convo_name] = [cur_thread]

    # The following is used in setup to time how long it takes various processes
    # This timing counts the time that user input starts, as there can be a lag before
    times.append(time.time())  # Background setup done
    print('\n' + one_line() + '\n')
    input("Press enter when you're ready to continue to user input: \n")
    # this time is user input prompt time
    times.append(time.time())  # User selection is starting

    # Lets finish up this setup boys, place all elements in the conversation bucket
    duplicate_index = 1
    for key in sorted(duplicate_bucket.keys()):
        for cur_thread in duplicate_bucket[key]:

            previous = msgs[key][-1]
            next = cur_thread[0]
            prev_time, next_time = CustomDate(previous[2]), CustomDate(next[2])
            # prev_time and next_time are used to calculate the time difference between the previous
            # message group's last message and this message group's first message. This time helps
            # determine whether both message groups belong to the same conversation

            if -3 <= prev_time.distance_from(next_time) <= 0 and len(msgs[key]) > 10000 and len(cur_thread) == 10000:
                msgs[key].extend(cur_thread)
                duplicate_index += 1
            elif prev_time.distance_from(next_time) <= 0:

                clear_screen()

                print("#{0} of {1} (at maximum) duplicate conversations. Some might be done for you behind the scenes."
                      .format(duplicate_index, num_duplicates))
                print(conversation_color + key)
                print(one_line() + "\n")

                print(previous_color + '# previous conversation end - length = {0:,}'.format(len(msgs[key]))
                      + Style.RESET_ALL)
                print_thread(msgs[key], end=True, padding=10)

                print(current_color + "\n# next conversation start - length = {0:,} (maximum possible length is 10,000)"
                      .format(len(cur_thread)) + Style.RESET_ALL)
                print_thread(cur_thread, start=True, padding=10)

                print('\n' + one_line())
                # Prints the last 5 messages of the previous message group and the first 5 message of
                # the current message group, both in RED with a BLACK background

                print(are_same_color + "\nAre these two chunks from the same conversation? You might have "
                                       "to look this up on facebook.com. [Y/n]" + Style.RESET_ALL)

                are_same = user_says_yes()
                # user input to decide if the above two message groups are the same conversation

                if are_same:
                    msgs[key].extend(cur_thread)
                    duplicate_index += 1

                    clear_screen()
                else:
                    # the two conversations are NOT the same (because of user input)
                    #  so we need to add the new one to an appropriate duplicate

                    add_to_duplicate()
            else:
                # The two conversations are not the same (since the previous is after the new one)
                # so we need t add the new one to an appropriate duplicate

                add_to_duplicate()

    clear_screen()
    quick_preferences = PreferencesSearcher.from_msgs_dict(msgs)
    times.append(time.time())  # The end of setup

    return msgs, str(footer), quick_preferences.preferences


def clean_convo_name(name, split_factor=', ') -> str:
    return split_factor.join(sorted(name.split(split_factor)))


class PreferencesSearcher:
    QUALITIES = ['alpha', 'length', 'contacted']

    def __init__(self, preferences):
        self.preferences = preferences
        self.bounds = range(1, len(preferences['alpha']) + 1)

    @classmethod
    def from_msgs_dict(cls, msgs_dict: dict):
        preferences = dict()

        # a list of names sorted first alphabetically and second by reversed number of messages (largest first)
        alphabetical = [name for name, _ in sorted(msgs_dict.items(), key=lambda x: (x[0], -len(x[1])))]
        alpha_dict = dict()
        for i, name in enumerate(alphabetical):
            alpha_dict[i + 1] = (name, name)
            alpha_dict[name] = (i + 1, name)
        preferences['alpha'] = alpha_dict

        # a list of names and conversations lengths sorted first by
        # reverse number of messages (largest first) and then alphabetically
        by_num = sorted([(name, len(convo)) for name, convo in msgs_dict.items()], key=lambda x: (-x[1], x[0]))
        by_num_dict = dict()
        for i, entry in enumerate(by_num):
            name, convo_length = entry
            by_num_dict[i + 1] = tuple(entry)
            by_num_dict[name] = (i + 1, convo_length)
        preferences['length'] = by_num_dict

        # a list of conversation names and conversations sorted first by date values
        # (more recent dates first - None should be after the current date, or date of download)
        by_recently_contacted = sorted([(name, convo) for name, convo in msgs_dict.items()],
                                       key=lambda val: CustomDate(val[1][-1][2]), reverse=True)
        by_recent_dict = dict()
        for i, entry in enumerate(by_recently_contacted):
            date = entry[1][-1][2]
            name = entry[0]
            by_recent_dict[i + 1] = (name, date)
            by_recent_dict[name] = (i + 1, date)
        preferences['contacted'] = by_recent_dict

        return cls(preferences)

    def get_name(self, index, quality, value=False):
        assert isinstance(index, int), "index must be an integer"
        assert index in self.bounds, "index must be in {0}".format(str(self.bounds))
        assert quality in PreferencesSearcher.QUALITIES, "quality must be in: "\
            .format(str(PreferencesSearcher.QUALITIES))
        assert value in [True, False], "value must be a boolean"

        data = self.preferences[quality][index]
        if value:
            return data[1]
        else:
            return data[0]

    def get_index(self, name, quality, value=False):
        assert isinstance(name, str), "index must be an integer"
        assert quality in PreferencesSearcher.QUALITIES, "quality must be in: "\
            .format(str(PreferencesSearcher.QUALITIES))
        assert value in [True, False], "value must be a boolean"

        if name not in self.preferences[quality]:
            return None
        data = self.preferences[quality][name]
        return data[1] if value else data[0]

    def ordered_values(self, sort, reverse=False) -> list:
        """Returns a list of dictionaries sorted by the values corresponding to sort
        Parameters:
            sort: A list of the qualities to include in the returned dicts. The order of sort determines the sort order
            reverse (optional): Whether the returned list should be reverse sorted
        Return:
            A list of dictionaries with each dictionary having queryable keys from sort
        """
        assert isinstance(sort, list) or isinstance(sort, tuple), "sort must be a list or tuple of sorting preferences"
        for ele in sort:
            assert ele in self.QUALITIES, "sort must contain only values from self.QUALITIES: {0}"\
                .format(self.QUALITIES)
        assert reverse in [True, False], "reverse must be a boolean"
        values = []
        for i in range(self.bounds.start, self.bounds.stop // 2):
            tmp = []
            name = self.get_name(i, 'alpha')
            for quality in sort:
                tmp.append(self.get_index(name, quality, value=True))
            values.append(tmp)

        # A list of dictionaries with keys from quality and corresponding values. sorted by ordered values
        return [dict(zip(sort, value)) for value in sorted(values, reverse=reverse)]

    def match_name(self, query, sort=('length', 'alpha', 'contacted'), reverse=True):
        """Returns a filtered output of ordered_values where each conversation name contains query"""
        return [d for d in self.ordered_values(sort, reverse=reverse) if query.lower() in d['alpha'].lower()]

    def __repr__(self):
        return "PreferenceSearcher({0})".format(repr(self.preferences))

    def __str__(self):
        return repr(self)


def clear_screen():
    """Clears the user's screen/ terminal"""
    #  http://stackoverflow.com/questions/2084508/clear-terminal-in-python
    os.system('cls' if os.name == 'nt' else 'clear')


def one_line(pattern='-'):
    """Fills one line of the user's screen with pattern"""
    # http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python/6550596#6550596
    console_length = shutil.get_terminal_size().columns
    pattern_string = pattern * (console_length // len(pattern)) + pattern[console_length % len(pattern)]
    return pattern_string[:-1]

    # Alternatively https://docs.python.org/3/library/string.html#formatstrings
    # return '{:{fill}{align}{width}}'.format('', fill=pattern, width=console_length, align='^')


def user_says_yes():
    """Returns True if the user types 'y' or 'yes' and False for 'no', 'n (ignoring case)'"""
    while True:
        choice = input('> ').lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['no', 'n']:
            return False


def color_method(string: str) -> str:
    """Colors a function call passed with one color, making the arguments / parameters another"""
    outer_code_color = Fore.LIGHTGREEN_EX
    inner_code_color = Fore.CYAN

    result = "" + Back.BLACK

    if '(' in string:
        result += outer_code_color + string[:string.find('(') + 1]
        result += inner_code_color + string[string.find('(') + 1:-1]
        result += outer_code_color + ')' + Style.RESET_ALL
    else:
        result += inner_code_color + string + Style.RESET_ALL
    return result


def fit_colored_text_to_console(text, *to_be_colored, color_fn=None) -> str:
    """Returns a string formatted to the console width and with all elements of to_be_colored colored by color_fn
    Parameters:
        text: (str) the text to be formated
        to_be_colored: (str) an arbitrary number of substrings from text that should be colored according to color_fn
        color_fn (optional): (fn) the function used to color elements of to_be_colored. Should take in a string and
            return a colored version of that string. Defaults to functions.setup_functions.color_method
    """
    if color_fn is None:
        color_fn = color_method
    console_width = min(shutil.get_terminal_size().columns, 150)
    formatted_text = textwrap.fill(text, console_width)

    for colorable_text in to_be_colored:
        if colorable_text in formatted_text:
            formatted_text = formatted_text.replace(colorable_text, color_fn(colorable_text))
        else:
            words = colorable_text.split()
            for i in range(1, len(words)):
                tmp_text = ' '.join(words[0:i]) + '\n' + ' '.join(words[i:])
                if tmp_text in formatted_text:
                    formatted_text = formatted_text.replace(tmp_text, color_fn(tmp_text))
                    break

    return formatted_text
