import os
import time
import shutil
import textwrap
import json
from colorama import Fore, Back, Style, init

from functions import setup_functions
import functions.emojis as emojis

init(autoreset=True)


# ------------------------------------------  CHECKING FOR PREVIOUS SETUP  ------------------------------------------- #
if os.path.isfile('data/data.json'):
    print("Are you sure you want to override the data currently saved?\n"
          "This might require resetting preferences. [Y/n]")
    choice = input("> ")
    while choice.lower() not in ['y', 'yes', 'no', 'n']:
        choice = input("> ")
    if choice.lower() in ['n', 'no']:
        exit()
# ------------------------------------------  CHECKING FOR PREVIOUS SETUP  ------------------------------------------- #


#


# ------------------------------------  BACKGROUND SETUP AND INFORMATION FOR USER  ---------------------------------- #
setup_functions.clear_screen()
times = [time.time()]

console_width = min(shutil.get_terminal_size().columns, 150)

intro_text1 = (
    "Beginning setup. During setup you might be prompted to answer whether two sets of messages are from the same "
    "chat. In this case, setup prints the last 10 messages from the first conversation, as well as the first 10 "
    "from the second conversation. You will then be asked whether the 20 messages are from the same chat, or two "
    "different chats."
)
intro_text2 = (
    "A good way to do this is to go to www.facebook.com/messages and search for one of the longer messages that "
    "appear. When you find the conversation that has this messages, see if all 20 messages can be found "
    "consecutively. Only if you find them all should you specify \"yes\", that the two conversations are the same. "
    "Otherwise specify no."
)

time_text = (
    "Now waiting for background setup. This process might take a few minutes depending on your archive size and "
    "processor speed."
)

print(textwrap.fill(intro_text1, width=console_width))
print()
print(textwrap.fill(intro_text2, width=console_width))
print()
print(textwrap.fill(time_text, width=console_width))
print()

os.makedirs('data', exist_ok=True)
unordered_threads, footer = setup_functions.get_all_threads_unordered(
    setup_functions.get_all_thread_containers('html/messages.htm')
)

msgs, footer, preferences = setup_functions.get_all_msgs_dict('html/messages.html', unordered_threads, footer, times)

for convo_name, convo in msgs.items():
    for i in range(len(convo)):
        convo[i] = (convo[i][0], emojis.emojify(convo[i][1]), convo[i][2])
# ------------------------------------  BACKGROUND SETUP AND INFORMATION FOR USER  ---------------------------------- #


#


# -------------------------------------------------  WRITING TO FILES  ----------------------------------------------- #
all_data = {
    'conversation_data': msgs,
    'footer': footer,
    'preferences': preferences
}
all_data = json.dumps(all_data)
with open('data/data.json', mode='w', encoding='utf-8') as f:
    f.write(all_data)
os.makedirs('data/conversation_data', exist_ok=True)
print('Setup will finish shortly\n')
times.append(time.time())
# -------------------------------------------------  WRITING TO FILES  ----------------------------------------------- #


#


# -------------------------------------------------  PRINTING TIMES  ------------------------------------------------- #
# times should be in the following format:
# [{start_time}, {after_user_says_continue}, {begin_user_input}, {end_user_input}, {end_setup}]


def time_string(time_as_seconds):
    if time_as_seconds > 60:
        return "{0} minute{1} and {2} second{3}".format(int(time_as_seconds // 60),
                                                        's' if int(time_as_seconds) // 60 != 1 else '',
                                                        int(time_as_seconds % 60),
                                                        's' if int(time_as_seconds % 60) != 1 else '')
    else:
        return "{0} second{1}".format(int(time_as_seconds), 's' if int(time_as_seconds) != 1 else '')


real_times = [
    "Background setup time: {0}".format(time_string(times[1] - times[0])),
    "User instruction time, prior to user input: {0}".format(time_string(times[2] - times[1])),
    "User input time: {0}".format(time_string(times[3] - times[2])),
    "Final processing time: {}".format(time_string(times[4] - times[3])),
]

for ele in real_times:
    print(ele)
print("\nTotal setup time: {0}".format(time_string(times[-1] - times[0])))

print()
print("If you've made it this far then you should be good to start analyzing your conversations!\n"
      "run `{0}` to start up the terminal version, or `{1}` for a gui"
      .format(Fore.LIGHTGREEN_EX + Back.BLACK + 'python3 -i playground.py' + Style.RESET_ALL,
              Fore.LIGHTCYAN_EX + Back.BLACK + 'python3 fancy_playground.py' + Style.RESET_ALL))
print()
# -------------------------------------------------  PRINTING TIMES  ------------------------------------------------- #
