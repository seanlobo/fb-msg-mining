from setup import data
import convoreader
import customdate




class MessageReader():

	def __init__(self):
		self.data = eval(open(data).read())
		self.names = self._get_convo_names_freq()
		self.names_alpha = self._get_convo_names_alpha()

	def get_convo_names(self, by_num_msgs=True):
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

	def len_convo(self, people):
		assert type(people) in [int, list, str], "Invalid opperand"
		convo = self.get_convo(people)
		return len(convo)

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
















