import os
import time

from functions import setup_functions


start = time.time()

print('\nSetting up the data, this could take a few minutes depending on how much data you have\n'
      '(aka how much you chat) and your computer\'s processor speeds\n')

os.makedirs('data', exist_ok=True)
msgs, footer = setup_functions.get_all_msgs_dict('html/messages.htm')

with open('data/data.txt', mode='w', encoding='utf-8') as f:
    f.write(str(msgs) + '\n')
    f.write(footer)
print('Setup is finished', end=" ")

end = time.time()
diff = end - start

if diff > 60:
    print("and took about {0} minute(s) and {1} seconds".format(int(diff // 60), int(diff % 60)))
else:
    print("and took about {0} seconds".format(diff))
print()