# Place to run all commands
try:
    import sys
    import os
    import shutil
    import traceback
    import ast

    from functions.messagereader import MessageReader
    from functions.setup_functions import clear_screen, fit_colored_text_to_console
    from functions.wordcloud import WordCloud
    from functions.convoreader import ConvoReader
    from functions.customdate import CustomDate
    from functions import emojis
except (ImportError, SyntaxError) as e:  # if an error arises when importing abort the program

    try:  # attempt to print out a traceback, and catch possible name error due to traceback not importing
        print(traceback.format_exc())
        os._exit(3)
    except NameError as error:
        print(e)
        os._exit(3)


preload = True
if len(sys.argv) > 1:
    try:
        assert len(sys.argv) == 2, ""
        assert sys.argv[1].title() in ["True", "False"], ""
        preload = ast.literal_eval(sys.argv[1].title())
    except AssertionError:
        print("usage: playground.py [preload=True]")
        print()
        print("preload: True|False, whether to pre-load all conversations for quick retrieval")
        os._exit(2)


# http://stackoverflow.com/questions/2356399/tell-if-python-is-in-interactive-mode
if not sys.flags.interactive:
    print("Please run this program interactively, with the `-i` flag")
    print("The program will now abort")
    os._exit(1)


print("Please wait a few moments for the playground to set up.")
if preload:
    print("Loading all conversations, this will take some additional time")


try:
    m = MessageReader(preload_conversations=preload)
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
