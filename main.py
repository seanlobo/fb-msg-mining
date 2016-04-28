import os

from functions import setup


os.makedirs('data', exist_ok=True)
with open('data/data.txt', mode='w', encoding='utf-8') as f:
  print('\nSetting up the data, this could take a few minutes depending on how much data you have (aka how much you chat)\n')
  msgs, footer = setup.get_all_msgs_dict('html/messages.htm')
  f.write(str(msgs) + '\n')
  f.write(footer)
print('Setup is finished.')
