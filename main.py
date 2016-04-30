import os

from functions import setup

print('\nSetting up the data, this could take a few minutes depending on how much data you have (aka how much you chat)\n')

os.makedirs('data', exist_ok=True)
msgs, footer = setup.get_all_msgs_dict('html/messages.htm')

with open('data/data.txt', mode='w', encoding='utf-8') as f:
  f.write(str(msgs) + '\n')
  f.write(footer)
print('Setup is finished.')
