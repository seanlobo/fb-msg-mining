class MessageReader():

	def __init__(self, data='/Users/seanlobo/TEMP FOLDER/data.txt'):
		assert type(data) in [str, dict], ("Invalid constructor:"
			" must pass a dictionary or ./data.txt path")
		if type(data) is str:
			self.data = eval(open(data).read())
		else:
			self.data = data
		self._set_convo_names_freq()
		self._set_convo_names_alpha()
		self.names = self.names_freq

	def get_convo_names(self, by_num_msgs=False):
		if by_num_msgs:
			return self.names_freq
		else:
			return self.names_alpha

	def get_convo(self, people):
		assert type(people) in [str, list], (""
			"Invalid argument: must pass"
			"a list of names (as strings) or string")
		if type(people) is str:
			people = people.title().split(', ')
		else:
			people = [name.title() for name in people]
		for name in self.data.keys():
			if self._contents_equal(name.split(', '), people):
				return ConvoReader(name, self.data[name])
		return None

	def get_convo_len(self, people):
		convo = self.get_convo(people)
		return len(convo) if convo is not None else -1

	def _set_convo_names_freq(self):
		self.names_freq = [sorted(ele.split(', ')) for ele, _ in 
			sorted([(key, len(val)) for key, val in self.data.items()],
					key=lambda x: x[1], reverse=True)]


	def _set_convo_names_alpha(self):
		names = [name.split(', ') for name in self.data.keys()]
		self.names_alpha = sorted([sorted(ele) for ele in names])

	def _contents_equal(self, lst1, lst2):
		if len(lst1) != len(lst2):
			return False
		for ele in lst1:
			if ele not in lst2:
				return False
		return True


Reader = MessageReader

a = MessageReader()

class ConvoReader():

	def __init__(self, convo_name, convo_list):
		self.name = convo_name
		self.convo = convo_list
		self.msgs = (msg for name, msg, date in self.convo)
		self.dates = (date for name, msg, date in self.convo)


	def __getitem__(self, index):
		if index >= len(self):
			raise IndexError
		return self.convo[index]

	def __len__(self):
		return len(self.convo)

	def __str__(self):
		string = ""
		for name, msg, date in self.convo:
			string += name + ": " +  msg + " | " + date
			string += '\n'
		return string

	def __repr__(self):
		return "ConvoReader(" + repr(self.name) +', ' + repr(self.convo) + ")"

convo = a.get_convo("Swetha raman, sean lobo")

dates = convo.dates


class MessageStats():

	def __init__(self, convo_name, convo_list):
		self.name = convo_name
		self.convo = convo_list

	def get_msgs_over_time(start=None, end=None, group_size=1):
		pass


















#########################TO DO##################################
# impliment str and repr in all classes
# implement len in some
# 
# 
# 
# CONVO READER
# get message based on elements
# find all elements / messages that match a phrase
# iterator
# 
# 
# 
# 
# 
# 
# MESSAGE STATS
# somehow get a graph of messages over tome
#  - get a list with # of messages / day or time unit
# average response time?
# 
# 
# 
# 
