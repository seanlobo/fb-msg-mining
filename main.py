from functions import setup


with open(setup.data, mode='w', encoding='utf-8') as f:
  print('\nSetting up the data, this could take a few minutes depending on how much data you have (aka how much you chat)\n')
  msgs, footer = setup.get_all_msgs_dict(setup.msgs)
  f.write(str(msgs) + '\n')
  f.write(footer)
print('Setup is finished.')
