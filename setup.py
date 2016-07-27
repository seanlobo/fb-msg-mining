import os
import time
import shutil
import textwrap
from colorama import Fore, Back, Style, init

from functions import setup_functions

init(autoreset=True)


# ------------------------------------------  CHECKING FOR PREVIOUS SETUP  ------------------------------------------- #
if os.path.isfile('data/data.txt'):
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

print('Setup information\n' + setup_functions.one_line() + '\n')

# Background information
print(Fore.LIGHTGREEN_EX + Back.BLACK + 'Background:' + Style.RESET_ALL)
background = ("All of your message data (that hasn't been deleted) can be found in the file `messages.htm`. "
              "But since this file is written in raw html, and can get quite large, it isn't very fun to "
              "read through. What setup does is parse this html into a form more amenable to analysis.")
print(textwrap.fill(background, width=console_width))
print()

# User prompting information
print(Fore.LIGHTCYAN_EX + Back.BLACK + "User Prompting:" + Style.RESET_ALL)
user_prompting_info = ("For the most part, setup can figure things out for itself. However, due to the nature of "
                       "how information is stored in the html file, there are times when conversations can "
                       "be confused for each other, in particular group chats. When this happens, setup will "
                       "prompt users to specify whether two confusing conversations are the same, or if "
                       "they both belong to separate chats that happen to share participants. It's likely that "
                       "you will have to go to Facebook.com to see whether the two conversations are the same.")
print(textwrap.fill(user_prompting_info, width=console_width))
print()

# Example
print(Fore.LIGHTMAGENTA_EX + Back.BLACK + "An Example:" + Style.RESET_ALL)
example_text = ("Let's assume Sally makes a group chat with her friends Susie and Blake. Later, Blake "
                "makes a group chat with Susie and another unnamed friend. If the unnamed friend leaves "
                "this second chat at some point, and Sally is added, there will be two chats with identical "
                "people in them. Due to the nature of the data storage, telling the conversations apart will  "
                "be ambiguous. In such a case you will be prompted to specify whether the two conversations "
                "belong to the same chat. If you aren't sure at any point, or can't figure out their identities, "
                + Fore.LIGHTRED_EX + Back.BLACK + "default to NO" + Style.RESET_ALL)
print(textwrap.fill(example_text, width=console_width))
print()

# Tips
print(Fore.LIGHTRED_EX + Back.BLACK + "Tips:" + Style.RESET_ALL)
tips_text = ("When two duplicate conversations are encountered, setup prints the last 10 messages from the previous "
             "conversation, as well as the first 10 from the next conversation. Based on these 20 messages, the user's "
             "job is to specify whether the second conversation comes right after the first one. A good way to do this "
             "is to go to www.facebook.com/messages and search for one of the longer messages that appear. When you "
             "find the conversation that has this messages, see if all 20 messages can be found consecutively. Only "
             "if you find them all should you specify \"yes\", that the two conversations are the same. Otherwise "
             "specify no")
print(textwrap.fill(tips_text, width=console_width))
print('\n' * 2)


time_text = ("Now waiting for background setup. This process has been known to take up to 10 minutes, depending "
             "on the speed of your processor and the size of your archive\n")
print(textwrap.fill(time_text, width=console_width))

os.makedirs('data', exist_ok=True)
unordered_threads, footer = setup_functions.get_all_threads_unordered(
    setup_functions.get_all_thread_containers('html/messages.htm'))

msgs, footer, preferences = setup_functions.get_all_msgs_dict('html/messages.html', unordered_threads, footer, times)
# ------------------------------------  BACKGROUND SETUP AND INFORMATION FOR USER  ---------------------------------- #



#


# -------------------------------------------------  WRITING TO FILES  ----------------------------------------------- #
with open('data/data.txt', mode='w', encoding='utf-8') as f:
    f.write(str(msgs) + '\n')
    f.write(footer + '\n')
    f.write(str(preferences))
os.makedirs('data/conversation_data', exist_ok=True)
print('Setup will finish shortly\n')
# -------------------------------------------------  WRITING TO FILES  ----------------------------------------------- #


#


# -------------------------------------------------  PRINTING TIMES  ------------------------------------------------- #
# times should be in the following format:
# [{start_time}, {after_user_says_continue}, {begin_user_input}, {final_analysis_end}]


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
