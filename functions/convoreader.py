from collections import Counter
from math import ceil

from functions.customdate import CustomDate


class ConvoReader():

	def __init__(self, convo_name, convo_list):
		self.name = convo_name.lower()
		self.convo = [[name.lower(), msg, CustomDate(date)] for name, msg, date in convo_list]
		self.msgs = [msg for name, msg, date in self.convo]
		self.dates = [date for name, msg, date in self.convo]
		self.people = sorted(self.name.split(', '))

	def print_people(self):
		"""Prints to the screen an alphabetically sorted list of people
		in the conversation
		"""
		res = ""
		for i, pers in enumerate(self.people):
			res += "{0}) {1}\n".format(i + 1, pers.title())
		print(res)

	def messages(self, name=None):
		"""Returns either the number of messages spoken by the specified
		person, or if no name is passed, a Counter object storing the number
		of mesages as values paired with names of people as keys.
		"""
		if name is None:
			return self.__msgs_per_person()
		else:
			return self.__msgs_spoken(name)

	def words(self, name=None):
		"""Returns either the number of words spoken by the specified
		person, or if no name is passed, a Counter object storing the number
		of words as values paired with names of people as keys.
		"""

		if name is None:
			return self.__words_per_person()
		else:
			return self.__words_spoken(name)

	def ave_words(self, name=None):
		"""Returns either the average number of words spoken per message 
		by the specified person, or if no name is passed, a Counter object 
		storing the average number of words per message as values paired 
		with names of people as keys.
		"""

		if name is None:
			return self.__ave_words_per_person()
		else:
			return self.__ave_words(name)

	def prettify(self):
		"""returns a string that \"prettily\" shows the conversation history"""
		
		string = ""
		for name, msg, date in self.convo:
			string += name + ": " +  msg + " | " + str(date)
			string += '\n'
		return string

	def msgs_graph(self, contact=None):
		"""Returns a list of length 2 lists that store a day as element 0
		and the number of total messages sent that day as element 1
		"""
		assert type(contact) in [type(None), str, list], "Contact must be of type string or a list of strings"
		if type(contact) is list:
			for i, ele in enumerate(contact):
				assert type(ele) is str, "Each element in contact must be a string"
				contact[i] = ele.lower()
			for ele in contact:	
				assert ele in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
											ele, str(self.people))
		elif type(contact) is str:
			assert contact in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
											contact, str(self.people)) 
			contact = [contact]


		if contact is not None:
			filt = lambda x: x in contact 
		else:
			filt = lambda x: True

		start = self.dates[0]
		end = self.dates[-1]
		days = end - start

		msg_freq = [[None, 0] for i in range(days + 1)]
		for person, msg, date in self.convo:
			if filt(person.lower()):
				msg_freq[date - start][1] += 1
		
		for day in range(len(msg_freq)):
			msg_freq[day][0] = CustomDate.from_date(start + day)

		return msg_freq

	def print_msgs_graph(self, contact=None):
		"""Prettily prints to the screen the message history of a chat"""
		msgs_freq = self.msgs_graph(contact)

		if contact is not None:
			print('Graph for {0}'.format(str(contact)))

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

	def msgs_by_weekday(self):
		"""Returns a list containing frequency of chatting by days
		of week, ordered by index, with 0 being Monday and 6 Sunday
		"""
		weekday_freq = [0 for i in range(7)]
		check = self.dates[0]
		msgs = 0
		for person, msg, date in self.convo:
			if check - date == 0:
				msgs += 1
			else:
				weekday_freq[date.weekday()] += msgs
				msgs = 1

		return [day / sum(weekday_freq) for day in weekday_freq]

	def msgs_by_day(self, window=60, contact=None):
		"""Returns a list containing average frequency of chatting by 
		times in days, starting at 12:00 am. Default window is 60 minute 
		interval.If time less than the passed window is left at the end,
		it is put at the end of the list
		"""
		assert type(contact) in [type(None), str, list], "Contact must be of type string or a list of strings"
		if type(contact) is list:
			for i, ele in enumerate(contact):
				assert type(ele) is str, "Each element in contact must be a string"
				contact[i] = ele.lower()
			for ele in contact:	
				assert ele in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
											ele, str(self.people))
		elif type(contact) is str:
			assert contact in self.people, "{0} is not in the list of people for this conversation:\n{1}".format(
											contact, str(self.people)) 
			contact = [contact]


		if contact is not None:
			filt = lambda x: x in contact 
		else:
			filt = lambda x: True

		total_msgs = 0
		msg_bucket = [[CustomDate.minutes_to_time(i * window), 0] for i in range(ceil(60*24 // window))]

		for person, msg, date in self.convo:
			if filt(person.lower()):
				msg_bucket[(int(date.minutes() // window) % (len(msg_bucket) - 1))][1] += 1
				total_msgs += 1
		for i in range(len(msg_bucket)):
			msg_bucket[i][1] /= (total_msgs / 100)
		return msg_bucket 

	def print_msgs_by_day(self, window=60, threshold=None, contact=None):
		"""Prints to the screen a graphical result of msgs_by_day"""
		frequencies = self.msgs_by_day(window, contact)

		if threshold is None:
			threshold = window / 120
		else:
			assert threshold > 0

		to_print = ''
		time_len = 9
		num_len = 6
		for time, freq in frequencies:
			time_str = time + (time_len - len(time) + 1) * ' '
			freq_str = str(freq)[:6]
			freq_str += (num_len - len(freq_str)) * '0' + '%'
			to_print += time_str
			to_print += freq_str
			to_print += ' |'

			to_print += '#' * int(freq / threshold)

			to_print += '\n'
		print(to_print)

		



	def __msgs_per_person(self): 
		res = dict()
		for person, msg, date in self.convo:
			if person not in res:
				res[person] = 1
			else:
				res[person] += 1
		return Counter(res)

	def __msgs_spoken(self, name):
		name = name.lower()
		if name not in self.people:
			raise Exception("Invalid name passed")
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
		name = name.lower()
		if name not in self.people:
			raise Exception("Invalid name passed")
		num = 0
		for person, msg, date in self.convo:
			if person == name:
				num += len(msg.split())
		return num

	def __ave_words_per_person(self):
		words = []
		for name in self.people:
			msgs = float(self.__msgs_spoken(name))
			tot_words = float(self.__words_spoken(name))
			if msgs > 0:
				words.append( (name, tot_words / msgs) )
		res = Counter()
		for name, ave in words:
			res[name] = ave
		return res

	def __ave_words(self, name):
		name = name.title()
		if name not in self.people:
			return -1
		return words_spoken(self, name) / msgs_spoken(self, name)





	def __getitem__(self, index):
		"""Returns the tuple (person, message, datetime) for the corresponding index"""
		if type(index) is not int:
			raise TypeError
		elif index >= len(self) or index < -len(self):
			raise IndexError
		else:
			return self.convo[index] if index >= 0 else self.convo[len(self) + index]

	def __len__(self):
		"""Returns the number of messages in self"""
		return len(self.convo)

	def __str__(self):
		"""Returns a string with the alphabetically sorted names of people
		in this conversation
		"""
		return "Converation for " + self.name

	def __repr__(self):
		"""Returns a valid constructor for this object"""
		return "ConvoReader({0}, {1})".format(repr(self.name), repr(self.convo))


