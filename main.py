from functions import setup


with open(setup.data, mode='w', encoding='utf-8') as f:
  print('\nSetting up the data, this could take around 2 minutes\n')
  f.write(str(setup.get_all_msgs_dict(setup.msgs)))
print('Setup is finished.')
