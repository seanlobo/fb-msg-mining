
from functions.convoreader import ConvoReader
from functions.customdate import CustomDate
from functions.setup import data



class MessageReader():

	def __init__(self):
		self.data = eval(open(data).read())
		self.names = self._get_convo_names_freq()
		self.names_alpha = self._get_convo_names_alpha()

	def get_convo_names(self, alpha=False):
		"""Returns a list of lists, where each inner list is 
		the members of a conversation. By default is arranged 
		with most active chat first in decreasing order, but 
		can pass alpha=True to order by alphabetical
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
		"""Returns a ConvoReader object reprsenting the conversation
		passed as a list of names, string name or index of conversation
		(from print_names). If an invalid parameter is passed return None
		"""
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

	def _get_convo_names_freq(self):
		lst = [ele for ele, l in 
			sorted([(key, len(val)) for key, val in self.data.items()],
					key=lambda x: x[1], reverse=True)]
		# new = True
		# for i in range(len(lst) - 1):
		# 	if new:
		# 		temp = []

		# 	if lst[i][1] == lst[i + 1]:
		# 		temp.append(i)
		# 		new = False
		# 	else:
		# 		temp.append(i + 1)
		# 		if len(temp) != 1:
		# 			sort = sort([lst[i] for i in temp], key=lambda x: x[0])
		# 			for temp_ind, lst_ind in enumerate(temp):
		# 				lst[lst_ind] = temp[temp_ind]
		# 		new = True
		return lst

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
















