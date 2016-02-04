from collections import Counter

from functions.customdate import CustomDate


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
		value = max_msgs / 100
		print("\nEach \"#\" referes to ~{0} messages".format(value))
		print()

		start = msgs_freq[0][0]
		date_len = 12
		num_len = len(str(max(msgs_freq, key=lambda x:x[1])[1]))
		for i in range(0, len(msgs_freq)):
			day = msgs_freq[i][0].to_string()
			day += ' ' * (date_len - len(day))

			msg_num = str(msgs_freq[i][1])
			msg_num += " " * (num_len - len(msg_num))
			
			string = day + msg_num
			if i % 2 == 0:
				print(string + " |", end="")
			else:
				print(date_len * " " + msg_num + " |", end="")


			if msgs_freq[i][1] == 0:
				print("(none)")
			else:
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


