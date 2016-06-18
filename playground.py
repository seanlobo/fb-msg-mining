# Place to run all commands

from functions.messagereader import MessageReader, color_method
from functions.setup_functions import clear_screen
from functions.wordcloud import WordCloud
from functions.convoreader import ConvoReader
from functions.customdate import CustomDate
from functions import emojis

m = MessageReader()

clear_screen()
print("\nWelcome to the python3 terminal version of fb-msg-mining!\n\n")
print("If you are unfamiliar with python syntax... then you might be better off using the GUI version of this program. "
      "You can exit this interactive session by typing the command `{0}` without the back tics, and clicking enter. "
      "If you're still set on using this version, then consider getting up to speed on syntax by executing the command "
      "`{1}`\n".format(color_method("exit()"), color_method("help()")))

print('Once you feel comfortable with basic python syntax, get ready to analyze your conversations with the '
      'command `{0}`\n\n'.format(color_method("m.help()")))


