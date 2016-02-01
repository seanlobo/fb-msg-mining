from setup import get_msg_data_paths as get_paths, data

from collections import Counter

class MessageReader():

	def __init__(self):
		self.data = eval(open(data).read())
		self.names = self._get_convo_names_freq()
		self.names_alpha = self._get_convo_names_alpha()

	def get_convo_names(self, by_num_msgs=False):
		if by_num_msgs:
			return self.names
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

	def _get_convo_names_freq(self):
		return [ele for ele, _ in 
			sorted([(key, len(val)) for key, val in self.data.items()],
					key=lambda x: x[1], reverse=True)]


	def _get_convo_names_alpha(self):
		names = [name.split(', ') for name in self.data.keys()]
		return sorted([sorted(ele) for ele in names])

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


	def print_lsts(self, lst):
		assert type(lst) is list, "must pass list"
		assert type(lst[0]) in [tuple, list], "wrong type of list"

		for i in range(len(lst)):
			print(str(i + 1) + ") " + lst[i][0] + ": " + str(lst[i][1]))

	def msgs(self, name=None):
		if name is None:
			return self.__msgs_per_person()
		else:
			return self.__msgs_spoken(name)

	def words(self, name=None):
		if name is None:
			return self.__words_per_person()
		else:
			return self.__words_spoken(name)

	def ave_words(self, name=None):
		if name is None:
			return self.__ave_words_per_person()
		else:
			return self.__ave_words(name)

	def __msgs_per_person(self): 
		res = dict()
		for person, msg, date in self.convo:
			if person not in res:
				res[person] = 1
			else:
				res[person] += 1
		return Counter(sorted([(name, num) for name, num in res.items()], 
				key=lambda x: x[1], reverse=True))

	def __msgs_spoken(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		num = 0
		for person, msg, date in self.convo:
			if person == name:
				num += 1
		return num

	def __words_per_person(self):
		res = dict()
		for person, msg, date in self.convo:
			if person not in res:
				res[person] = len(msg.split())
			else:
				res[person] += len(msg.split())
		return Counter(res)

	def __words_spoken(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		num = 0
		for person, msg, date in self.convo:
			if person == name:
				num += len(msg.split())
		return num

	def __ave_words_per_person(self):
		return Counter(sorted([(name, float(self.words_spoken(name)) / self.msgs_spoken(name)) 
				for name in self.people], key=lambda x: x[1], reverse=True))

	def __ave_words(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		return words_spoken(self, name) / msgs_spoken(self, name)


	def __len__(self):
		return len(self.convo)

	def __str__(self):
		return "Stats for " + self.name

	def __repr__(self):
		return "MessageStats({0}, {1})".format(self.convo_name, self.convo_list)




a = MessageReader()
stud = a.get_convo(7)
stats = stud.get_stats()








#########################TO DO################################## 
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
