import os
import time

from functions import setup_functions


if os.path.isfile('data/data.txt'):
    print("Are you sure you want to override the data currently saved?\n"
          "This might require resetting preferences. [Y/n]")
    choice = input("> ")
    while choice.lower() not in ['y', 'yes', 'no', 'n']:
        choice = input("> ")
    if choice.lower() in ['n', 'no']:
        exit()

start = time.time()

print('\nSetting up the data, this could take a few minutes depending on how much\n '
      'data you have (aka how much you chat) and your computer\'s processor speeds\n')

os.makedirs('data', exist_ok=True)
msgs, footer = setup_functions.get_all_msgs_dict('html/messages.htm')

with open('data/data.txt', mode='w', encoding='utf-8') as f:
    f.write(str(msgs) + '\n')
    f.write(footer)
os.makedirs('data/conversation_data', exist_ok=True)
print('Setup is finished', end=" ")

end = time.time()
diff = end - start

if diff > 60:
    print("and took about {0} minute(s) and {1} seconds".format(int(diff // 60), int(diff % 60)))
else:
    print("and took about {0} seconds".format(diff))
print()