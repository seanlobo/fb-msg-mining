import os
import shutil
from bs4 import BeautifulSoup
from colorama import init, Fore,Back, Style


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


def get_all_msgs_dict(msg_html_path='./messages.htm'):
    """Returns the dictionary uesd by MessageReader"""
    def add_to_duplicate():
        """Helper method to add a message group to a DUPLICATE conversation"""
        nonlocal msgs, cur_thread, convo_name, next_time
        duplicate_num = 1  # the number of duplicate message groups (have the same people, aka name)
        # but in reality belong to different conversations

        added = False # used so that we don't accidentally add something twice

        # while there exists another duplicate conversation in our list keep checking if the current
        # message group belongs to it. If we exit the while loop a new conversation is created with
        # "DUPLICATE #X appended to distinguish it, with X being the xth new duplicate conversation
        while (convo_name + ', DUPLICATE #{0}'.format(duplicate_num)) in msgs and not added:
            new_name = convo_name + ', DUPLICATE #{0}'.format(duplicate_num)

            # The time of the last message in the conversation for new_name
            prev_time = CustomDate(msgs[new_name][-1][2])

            if prev_time.distance_from(next_time) <= 0:
                # if our current conversation was during or after the last message in the new_name convo

                print('# previous convo end for {0}'.format(convo_name))
                for i in range(- min(5, len(msgs[new_name]), 0)):
                    print(msgs[new_name][i])
                print("\n# next convo start")
                for i in range(0, min(6, len(cur_thread))):
                    print(cur_thread[i])
                # prints last and first 5 messages of previous and current message groups, respectively

                are_same = input(Fore.MAGENTA + Back.BLACK + "\nAre these two chunks from "
                                                             "the same conversation? [Y/n]\n You might "
                                                             "have to look this up on facebook.com\n> " + Style.RESET_ALL)
                while are_same.lower() not in ['y', 'yes', 'n', 'no']:
                    are_same = input(Style.RESET_ALL + "[Y/n] > ")
                # User input for whether the two message groups are in the same conversation

                if are_same.lower() in ['no', 'n']:
                    duplicate_num += 1  # if they aren't the same, increment duplicate_num and try again
                elif not added:
                    # check to make sure the current message group hasn't already been added, otherwise add it
                    msgs[new_name].extend(cur_thread)
                    added = True
            else:
                # this conversation existed but was after our current one, so increment the number and try again
                duplicate_num += 1

            clear_screen()

        if not added:
            # if the current message group hasn't been added, add with a new duplicate #
            msgs[convo_name + ', DUPLICATE #{0}'.format(duplicate_num)] = cur_thread
        return

    all_thread_containers = get_all_thread_containers(msg_html_path)
    unordered_threads, footer = get_all_threads_unordered(all_thread_containers)

    # The end result
    msgs = dict()
    for thread in unordered_threads:
        convo_name = thread.contents[0]
        cur_thread = get_messages_readable(thread)
        if convo_name in msgs: # Another conversation with this name been seen before
            previous = msgs[convo_name][-1]
            next = cur_thread[0]
            prev_time, next_time = CustomDate(previous[2]), CustomDate(next[2])
            # prev_time and next_time are used to calculate the time difference between the previous
            # message group's last message and this message group's first message. This time helps
            # determine whether both message groups belong to the same conversation

            if -3 <= prev_time.distance_from(next_time) <= 0:
                # the previous conversation chunk is before the new one and within 3 minutes
                msgs[convo_name].extend(cur_thread)
            elif prev_time.distance_from(next_time) < -3:
                # if the new message group is after the new message group it but not within 3 minutes
                # we need user input to see if the two belong to the same chat

                print(Fore.RED + Back.BLACK + '# previous convo end for {0}'.format(convo_name) + Style.RESET_ALL)
                for i in range(- min(5, len(msgs[convo_name])), 0):
                    print(msgs[convo_name][i])
                print(Fore.RED + Back.BLACK + "\n# next convo start" + Style.RESET_ALL)
                for i in range(0, min(6, len(cur_thread))):
                    print(cur_thread[i])
                # Prints the last 5 messages of the previous message group and the first 5 message of
                # the current message group, both in RED with a BLACK background

                print(Fore.MAGENTA + Back.BLACK + "\nAre these two chunks from the same conversation? "
                                                  "[Y/n]\nYou might have to look this up on facebook.com" +
                      Style.RESET_ALL)
                are_same = input("> ").lower()
                while are_same not in ['y', 'yes', 'n', 'no']:
                    are_same = input("[Y/n] > ").lower()
                clear_screen()
                # user input to decide if the above two message groups are the same conversation

                if are_same.lower() in ['y', 'yes']: # if part of same convo append the new to the old
                    msgs[convo_name].extend(cur_thread)

                else:
                    # the two conversations are NOT the same (because of user input)
                    #  so we need to add the new one to an appropriate duplicate
                    add_to_duplicate()
            else:
                # The two conversations are not the same (since the previous is after the new one)
                # so we need t add the new one to an appropriate duplicate
                add_to_duplicate()

        else:
            # A conversation with the name of current message group does not exist, so it is added with no issues :D
            msgs[convo_name] = cur_thread

    print('\a', '')
    return (msgs, str(footer))


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
