#	Author: Sean Lobo
#	Date: Jan 15, 2016
#	File Purpose: Trying to improve composition of project
#				  and consolidate functions

from bs4 import BeautifulSoup
from collections import Counter

def get_all_divs(msg_html_path='./messages.htm'):
	"""Returns a list of list of divs. Contains all information
	needed to get full conversation history for any conversation.

	Return type has the following structure:

	[[msg_div1, msg_div2, msg_div3],
	 [msg_div1],
	 [msg_div1, msg_div2, msg_div3, msg_div4]
	 .
	 .
	 .
	]

	each inner list has an arbitrary length. The elemens of each 
	inner list are div tags that contain 1 thread each

	A thread is a list of up to 10,000 messages between two people
	or one group. The conversation the thread belongs to can be 
	found by:

	thread.contents[0]
	"""
	# soup object that holds all of the html
	soup = BeautifulSoup(open(msg_html_path), 'html.parser')

	# finds the outer div tag that holds all relevant information
	divs = []
	for div in soup.find_all('div', class_='contents'):
	    divs.append(div)
	div_tag = divs[0]

	divs = None
	soup = None

	# creates a list containing elements whose div 
	# tags hold the chat data
	all_divs = [] # list of list of divs [ [div, div], [div], ...]
	for div in div_tag("div", recursive=False):
		all_divs.append(div)

	return all_divs

def get_convo_divs(all_divs, convo_name=None):
	"""Returns a list of message_divs (threads) whose contents
	match the passed convo_name, or all message_divs by default

	Return type has the following sturcture:

	[thread1,
	thread2,
	thread3,
	.
	.
	.
	]
	"""
	def contents_equal(lst1, lst2):
		if len(lst1) != len(lst2):
			return False
		for ele in lst1:
			if ele not in lst2:
				return False
		return True

	if convo_name is not None:
		assert type(convo_name) is list, "You must pass in a list \
										  of names"

	bucket = []
	for msg_container in all_divs:
		for msg_div in msg_container('div', class_="thread", recursive=False):
			person = msg_div.contents[0].split(', ')
			if convo_name is None or contents_equal(person, convo_name):
				bucket.append(msg_div)

	return bucket

def get_messages_dict(msg_div, convo_dict=None):
	"""Returns a dictionary of chat histories paired with Person Name"""
	if convo_dict is None:
		convo_dict = dict()

	# list of all div ids for a certain message group 
	# (each message group has max 10,000 messages)
	# each element (div id tag) has the time and person of the message
	div_ids = [div for div in convo('div', class_='message', recursive=False)]
	# a list of messages. Each element corresponds to the information in div_ids
	messages = [p for p in convo('p', recursive=False)]
	
	for i in range(len(div_ids) - 1, -1, -1):
		# person who said the ith message
		person = [div for div in div_ids[i]('span', class_='user')][0].contents[0]
		
		if person not in convo_dict:
			convo_dict[person] = []

		try:
			msg = messages[i].contents[0]
		except IndexError:
			msg = ''
		convo_dict[person].append(msg)

	return convo_dict


def get_messages_readable(thread, previous=None):
	"""Returns a list of tuples of length 3. First element is person speaking,
	second message, third time
	"""
	if previous is None:
		previous = []

	# list of all div ids for a certain message group 
	# (each message group has max 10,000 messages)
	# each element (div id tag) has the time and person of the message
	div_ids = [div for div in thread('div', class_='message', recursive=False)]
	# a list of messages. Each element corresponds to the information in div_ids
	messages = [p for p in thread('p', recursive=False)]
	assert len(div_ids) == len(messages), 'div_ids and messages\
											 have different lengths'

	for i in range(len(div_ids) - 1, -1, -1):
		# person who said the ith message
		person = [div for div in div_ids[i]('span', class_='user')][0].contents[0]
		# time ith message was sent at
		time = [div for div in div_ids[i]('span', class_='meta')][0].contents[0]

		try:
			msg = messages[i].contents[0]
		except IndexError:
			msg = ''
		previous.append( (person, msg, time) )

	return previous



def get_all_msgs_dict(msg_html_path='./messages.htm'):
	all_divs = get_all_divs(msg_html_path)
	convo_divs = get_convo_divs(all_divs)

	msgs = dict()
	for thread in convo_divs:
		convo_name = thread.contents[0]
		if convo_name in msgs:
			msgs[convo_name].extend(get_messages_readable(thread))
		else:
			msgs[convo_name] = get_messages_readable(thread)

	print('\a', end='')
	return msgs


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


# with open('./data.txt', mode='w', encoding='utf-8') as f:
# 	f.write(str(get_all_msgs_dict()))
# print('Setup is finished.')








