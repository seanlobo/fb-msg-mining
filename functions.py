from setup import get_msg_data_paths as get_paths, data

from collections import Counter

from datetime import date, timedelta

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
		self.convo = [[name, msg, CustomDate(date)] for name, msg, date in convo_list]
		self.msgs = [msg for name, msg, date in self.convo]
		self.dates = [date for name, msg, date in self.convo]
		self.people = sorted(self.name.split(', '))

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

	def prettify(self):
		string = ""
		for name, msg, date in self.convo:
			string += name + ": " +  msg + " | " + date
			string += '\n'
		return string

	def msgs_per_day(self):
		start = self.dates[0]
		end = self.dates[-1]
		days = end - start

		msg_freq = [[None, 0] for i in range(days + 1)]
		for person, msg, date in self.convo:
			msg_freq[date - start][1] += 1
		
		for day in range(len(msg_freq)):
			msg_freq[day][0] = CustomDate.from_date(start + day)


		return msg_freq

	def print_msgs_per_day(self, msgs_freq=None):
		if msgs_freq is None:
			msgs_freq = self.msgs_per_day()

		max_msgs = max(msgs_freq, key=lambda x: x[1])[1]
		value = max_msgs / 50
		print("\nEach \"#\" referes to {0} messages".format(max_msgs))
		print()

		start = msgs_freq[0][0]
		L = 10
		for i in range(0, len(msgs_freq)):
			if i % 3 == 0:
				day = msgs_freq[i][0].to_string()
				spaces = len(day)
				print(day + max(0, L - spaces) * " " + " |", end="")
			else:
				print(L * " " + " |", end="")

			print('#' * int(msgs_freq[i][1] / value))








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









	def __getitem__(self, index):
		if type(index) is not int:
			raise TypeError
		elif index >= len(self) or index < -len(self):
			raise IndexError
		else:
			return self.convo[index] if index >= 0 else self.convo[len(self) + index]

	def __len__(self):
		return len(self.convo)

	def __str__(self):
		return "Converation for " + self.name

	def __repr__(self):
		return "ConvoReader({0}, {1})".format(repr(self.name), repr(self.convo))



class CustomDate():
	months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
				'August': 8 , 'September': 9, 'October': 10, 'November': 11, 'December': 12, }

	months_reversed = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
						7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

	days_of_week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

	def __init__(self, date_str):
		self.full_date = date_str
		temp = date_str.split(',')
		self.week_day = temp[0]
		month, day_of_month = temp[1].split()
		year, _, self.time, self.time_zone = date_str.split(',')[2].split()

		self.date = date(int(year), int(CustomDate.months[month]), int(day_of_month))

	@classmethod
	def from_date(cls, date_obj):
		date_string = "{0}, {1} {2}, {3} at [unknown-time] [unkown-timezone]".format(
						CustomDate.days_of_week[date_obj.weekday()], 
						CustomDate.months_reversed[date_obj.month], 
						date_obj.day,
						date_obj.year)
		return cls(date_string)

	def to_string(self):
		return "{0}/{1}/{2}".format(self.date.year, self.date.month, self.date.day)

	def __add__(self, other):
		if type(other) is not int:
			return NotImplemented
		return self.date + timedelta(days=other)

	def __sub__(self, other):
		if type(other) is not type(self):
			return NotImplemented
		return (self.date - other.date).days

	def __str__(self):
		return self.full_date

	def __repr__(self):
		return "CustomDate({0})".format(self.full_date)



















a = MessageReader()
stud = a.get_convo(7)






#########################TO DO################################## 
# 
# 
# CONVO READER
# get message based on elements
# find all elements / messages that match a phrase
# iterator
# somehow get a graph of messages over tome
# average response time?
# 
# 
# 
# 
# 
# 
# 
# 
# 
