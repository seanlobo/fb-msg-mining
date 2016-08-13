# Place to run all commands

import sys
import os
import shutil
import traceback


from functions.messagereader import MessageReader
from functions.setup_functions import clear_screen, color_method, fit_colored_text_to_console
from functions.wordcloud import WordCloud
from functions.convoreader import ConvoReader
from functions.customdate import CustomDate
from functions import emojis


# http://stackoverflow.com/questions/2356399/tell-if-python-is-in-interactive-mode
if not sys.flags.interactive:
    print("Are you sure you ran this program interactively, with the `-i` flag?")
    input("If not the program will exit. Press enter to continue: ")

print("Please wait a few moments for the playground to set up")

try:
    m = MessageReader(preload_conversations=True)
    p = m.quick_stats
except:
    # http://stackoverflow.com/questions/3702675/how-to-print-the-full-traceback-without-halting-the-program
    print(traceback.format_exc())
    os._exit(1)

clear_screen()
console_width = min(shutil.get_terminal_size().columns, 150)

print("\nWelcome to the python3 terminal version of fb-msg-mining!\n\n")
intro_text = ("If you are unfamiliar with python syntax... then you might be better off using the GUI version of this "
              "program. You can exit this interactive session by typing the command `exit()` without the back tics, "
              "and clicking enter. If you're still set on using this version, then consider getting up to speed on "
              "syntax by executing the command `help()`")
formatted_text = fit_colored_text_to_console(intro_text, "help()", "exit()")
print(formatted_text)
print()


intro_text2 = ('Once you feel comfortable with basic python syntax, get ready to analyze your conversations with the '
               'command `m.help()`')
print(fit_colored_text_to_console(intro_text2, "m.help()"))
print('\n')
