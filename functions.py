from collections import Counter

class MessageReader():

	def __init__(self, data='./data.txt'):
		assert type(data) in [str, dict], ("Invalid constructor:"
			" must pass a dictionary or ./data.txt path")
		if type(data) is str:
			self.data = eval(open(data).read())
		else:
			self.data = data
		self._set_convo_names_freq()
		# self._set_convo_names_alpha()

	def get_convo_names(self, by_num_msgs=False):
		if by_num_msgs:
			return self.names_freq
		else:
			return self.names_alpha

	def print_names(self):
		i = 1
		for name in self.names:
			print(str(i) + ": " + name)
			i += 1
			

	def get_convo(self, people):
		assert type(people) in [str, list, int], (""
			"Invalid argument: must pass"
			"a list of names (as strings), string, or int")

		if type(people) is int:
			return ConvoReader(self.names[people - 1], self.data[self.names[people - 1]])
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
		self.names = [ele for ele, _ in 
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




class ConvoReader():

	def __init__(self, convo_name, convo_list):
		self.name = convo_name
		self.convo = convo_list
		self.msgs = (msg for name, msg, date in self.convo)
		self.dates = (date for name, msg, date in self.convo)

	def get_stats(self):
		return MessageStats(self.name, self.convo)

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




class MessageStats():

	def __init__(self, convo_name, convo_list):
		self.name = convo_name
		self.convo = convo_list
		self.people = sorted(self.name.split(', '))

	@classmethod
	def fromConvoReader(cls, convo):
		name = convo.name
		msgs = convo.convo
		return cls(name, msgs)

	def msgs_per_person(self): 
		res = dict()
		for person, msg, date in self.convo:
			if person not in res:
				res[person] = 1
			else:
				res[person] += 1
		return sorted([(name, num) for name, num in res.items()], 
				key=lambda x: x[1], reverse=True)

	def words_per_person(self):
		res = dict()
		for person, msg, date in self.convo:
			if person not in res:
				res[person] = len(msg.split())
			else:
				res[person] += len(msg.split())
		return sorted([(name, num) for name, num in res.items()], 
				key=lambda x: x[1], reverse=True)

	def msgs_spoken(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		num = 0
		for person, msg, date in self.convo:
			if person == name:
				num += 1
		return num

	def words_spoken(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		num = 0
		for person, msg, date in self.convo:
			if person == name:
				num += len(msg.split())
		return num

	def ave_words_per_person(self):
		return sorted([(name, float(self.words_spoken(name)) / self.msgs_spoken(name)) 
				for name in self.people], key=lambda x: x[1], reverse=True)

	def ave_words(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		return words_spoken(self, name) / msgs_spoken(self, name)

	def print_lsts(self, lst):
		assert type(lst) is list, "must pass list"
		assert type(lst[0]) in [tuple, list], "wrong type of list"

		for i in range(len(lst)):
			print(str(i + 1) + ") " + lst[i][0] + ": " + str(lst[i][1]))



a = MessageReader("/Users/seanlobo/TEMP FOLDER/data.txt")
stud = a.get_convo(7)
stats = stud.get_stats()






def get_msg_ranks(all_msgs_dict=None, msg_html_path='./messages.htm'):
	assert all_msgs_dict is None or type(all_msgs_dict) is dict, \
	"you must pass the return from get_all_msgs"

	if all_msgs_dict is None:
		all_msgs_dict = get_all_msgs_dict(msg_html_path)

	ranks = dict()
	for key, val in all_msgs_dict.items():
		if key not in ranks:
			ranks[key] = len(val)
		else:
			ranks[key] += len(val)

	return Counter(ranks)







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
