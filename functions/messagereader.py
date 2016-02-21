
from functions.convoreader import ConvoReader
from functions.customdate import CustomDate
from functions.setup import data


class MessageReader():

	def __init__(self):
		with open(data, mode='r', encoding='UTF8') as f:
			self.data = eval(f.readline())
			self.download = f.readline()
		self.names = self._get_convo_names_freq()
		self.names_alpha = self._get_convo_names_alpha()

	def get_convo_names(self, alpha=False):
		"""Returns a list of lists, where each inner list is 
		the members of a conversation. By default is arranged 
		with most active chat first in decreasing order, but 
		can pass alpha=True to order by alphabetical
		Parameters:
			alpha (optional): False by default, in which case conversation names are 
				returned in order of most frequent first, and then alphabetical. If True
				conversations names are ranked in order of alphabetical first
		"""
		if alpha:
			return self.names
		else:
			return self.names_alpha

	def print_names(self):
		"""Prints to screen conversation names in order of most 
		active to least active"""
		i = 1
		for name in self.names:
			print(str(i) + ": " + name)
			i += 1
			

	def get_convo(self, people):
		"""Returns a ConvoReader object representing the conversation
		passed as a list of names, string name or index of conversation
		(from print_names). If an invalid parameter is passed return None
		Parameters:
			people: Which conversation you would like to get. Either the number from the output of 
			print_names(), the name of the conversation you want (e.g. 'sean lobo, jason perrin') 
			or a list of names (e.g. ['jason perrin', 'sean lobo'])
		"""
		assert type(people) in [str, list, int], (""
			"Invalid argument: must pass"
			"a list of names (as strings), string, or int")

		if type(people) is int:
			if people > 0:
				return ConvoReader(self.names[people - 1], self.data[self.names[people - 1]])
			else:
				return ConvoReader(self.names[len(self.names) + people], self.data[self.names[len(self.names) + people]])
		if type(people) is str:
			people = people.title().split(', ')
		else:
			people = [name.title() for name in people]
		for name in self.data.keys():
			if self._contents_equal(name.split(', '), people):
				return ConvoReader(name, self.data[name])
		print("You haven't talked with {0} before".format(people))
		return None

	def _get_convo_names_freq(self):
		return [ele for ele, _ in 
			sorted([(key, len(val)) for key, val in self.data.items()],
					key=lambda x: (-x[1], x[0]))]

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

	def __len__(self):
		return len(self.names)

	def __str__(self):
		return self.download

	def __repr__(self):
		return 'MessageReader()'


