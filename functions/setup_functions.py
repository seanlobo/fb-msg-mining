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
    divs = []
    for div in soup.find_all('div', class_='contents'):
        divs.append(div)
    div_tag = divs[0]

    footer = []
    for foot in soup('div', class_='footer'):
        footer.append(foot)

    divs = None
    soup = None

    # creates a list containing elements whose div
    # tags hold the chat data
    all_divs = [] # list of list of divs [ [div, div], [div], ...]
    for div in div_tag("div", recursive=False):
        all_divs.append(div)

    return (all_divs, footer[0].contents[0])


def get_all_threads_unordered(all_divs, convo_name=None):
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

    def contents_equal(lst1, lst2):
        if len(lst1) != len(lst2):
            return False
        for ele in lst1:
            if ele not in lst2:
                return False
        return True

    if convo_name is not None:
        assert type(convo_name) is list, "You must pass in a list \
                                          of names"

    thread_bucket = []
    for msg_container in all_divs:
        for msg_div in msg_container('div', class_="thread", recursive=False):
            person = msg_div.contents[0].split(', ')
            if convo_name is None or contents_equal(person, convo_name):
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

            if prev_time.distance_from(next_time) > 0 or prev_time.distance_from(next_time) <= -3:
                # if the previous message group is within 3 minutes of the new message group it
                # most likely was from the same conversation, and is treated as such, skipping this block

                print(Fore.RED + Back.BLACK + '# previous convo end for {0}'.format(convo_name))
                for i in range(- min(5, len(msgs[convo_name])), 0):
                    print(msgs[convo_name][i])
                print(Fore.RED + Back.BLACK + "\n# next convo start")
                for i in range(0, min(6, len(cur_thread))):
                    print(cur_thread[i])
                # Prints the last 5 messages of the previous message group and the first 5 message of
                # the current message group, both in RED with a BLACK background

                are_same = input(Fore.MAGENTA + Back.BLACK + "\nAre these two chunks from the same conversation?"
                                                             " [Y/n]\nYou might have to look this up on "
                                                             "facebook.com\n> ")
                while are_same.lower() not in ['y', 'yes', 'n', 'no']:
                    are_same = input(Style.RESET_ALL + "[Y/n] > ")
                print('\n' * 5)
                # user input to decide if the above two message groups are the same conversation

                if are_same.lower() in ['y', 'yes']: # if part of same convo append the new to the old
                    msgs[convo_name].extend(cur_thread)
                else:
                    duplicate_num = 1 # the number of duplicate message groups (have the same people, aka name)
                                      # but in reality belong to different conversations
                    added = False

                    # while there exists another duplicate conversation in our list keep checking if the current
                    # message group belongs to it. If we exit the while loop a new conversation is created with
                    # "DUPLICATE #X appended to distinguish it, with X being the xth new duplicate conversation
                    while (convo_name + ', DUPLICATE #{0}'.format(duplicate_num)) in msgs:
                        new_name = convo_name + ', DUPLICATE #{0}'.format(duplicate_num)
                        print('# previous convo end for {0}'.format(convo_name))
                        for i in range(- min(5, len(msgs[new_name]), 0)):
                            print(msgs[new_name][i])
                        print("\n# next convo start")
                        for i in range(0, min(6, len(cur_thread))):
                            print(cur_thread[i])
                        # Again prints last and first 5 messages of previous and current message groups, respectively

                        are_same = input( Fore.MAGENTA + Back.BLACK + "\nAre these two chunks from "
                                                                      "the same conversation? [Y/n]\n You might "
                                                                      "have to look this up on facebook.com\n> ")
                        while are_same.lower() not in ['y', 'yes', 'n', 'no']:
                            are_same = input(Style.RESET_ALL + "[Y/n] > ")
                        # User input for whether the two message groups are in the same conversation

                        if are_same.lower() in ['no', 'n']:
                            duplicate_num += 1 # if they aren't the same, increment duplicate_num and try again
                        elif not added:
                            # check to make sure the current message group hasn't already been added, otherwise add it
                            msgs[new_name].extend(cur_thread)
                            added = True
                            break
                    if not added:
                        # if the current message group hasn't been added, add with a new duplicate #
                        msgs[convo_name + ', DUPLICATE #{0}'.format(duplicate_num)] = cur_thread
            else:
                # easy case, a message group with the name of the current one already exists, but because the two
                # are within 3 minutes of each other they are assumed to be in the same conversation and added
                msgs[convo_name].extend(cur_thread)
        else: # A conversation with the name of current message group does not exist, so it is added with no issues :D
            msgs[convo_name] = cur_thread
    print('\a', '')
    return (msgs, str(footer))


