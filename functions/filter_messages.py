#	Author: Sean Lobo
#	Date: Jan 11, 2016
#	File Purpose: Clean up facebook chat data

from collections import Counter


def bsearch(lst, word, low=0, high=None):
	if high is None:
		high = len(lst) - 1
	mid = (low + high) // 2
	while lst[mid] != word and mid > low and mid < high:
		if lst[mid] > word:
			high = mid - 1
			mid = (low + high) // 2
		else:
			low = mid + 1
			mid = (low + high) // 2
	return lst[mid] == word





# loads dictionary data
with open('./chatDictionary.py', 'r', encoding='utf-8') as f:
	chat_dict = eval(f.read())

# converts messages to lowercase
for key, val in chat_dict.items():
	chat_dict[key] = list(map(lambda string: string.lower(), val))

# list that will hold raw messages aggregates of each person
messages = []
# keeps track of who each element in messages refers to
order = []
for key, val in chat_dict.items():
	order.append(key)
	lst = []
	for ele in val:
		for word in ele.split():
			lst.append(word)
	messages.append(lst)

# dictionary with people paired with list of all words 
word_dict = dict()
for i in range(len(order)):
	word_dict[order[i]] = messages[i]

# dictionary with people paired with tuple of all unique words
unique_word_dict = dict()
for key, val in word_dict.items():
	unique_word_dict[key] = sorted(val)

# get rid of (most) emojis
for key, val in unique_word_dict.items():
	for i in range(len(val)):
		if val[i] > 'z' * 10:
			end = i
			break
	unique_word_dict[key] = val[:end]

# get rid of (most) websites
for key, val in unique_word_dict.items():
	new = []
	for ele in val:
		if 'www.' not in ele and '.com' not in ele:
			new.append(ele)
	unique_word_dict[key] = new

# get rid of (most) leading non letter words
for key, val in unique_word_dict.items():
	new = []
	for ele in val:
		new.append(ele.strip('.!123456789-+?><}{][()\'\""\\ /*#$%^&#@,'))
	unique_word_dict[key] = new

for key, val in unique_word_dict.items():
	if 'Sean' in key:
		sean = val
	else:
		swetha = val



def filter_words(words, exclude):
	res = []
	for word in words:
		if word not in exclude:
			res.append(word)
	return res





common_words = """
'' i you to the it a me and that so my for we be 
in of if is just with was then do have i'm your 
what on too but in not when how get much don't 
ok it's i'll up what at can this 
""".split()




common_words.append('\"\"')

sean = filter_words(sean, common_words)
swetha = filter_words(swetha, common_words)











sean_counter = Counter(sean)
swetha_counter = Counter(swetha)

sean100 = sean_counter.most_common(750)
swetha100 = swetha_counter.most_common(750)

#print(sean100)
#print(swetha100)

word = 'boring'







# with open('./sean_word_freq.txt', 'w', encoding='utf-8') as f:
# 	lst = []
# 	for key, val in sean_counter.items():
# 		lst.append( (key, val))
# 	for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
# 		f.write("{0}: {1}".format(key, val) + "\n")	
# print('list can be found in ./sean_word_freq.txt')


# with open('./swetha_word_freq.txt', 'w', encoding='utf-8') as f:
# 	lst = []
# 	for key, val in swetha_counter.items():
# 		lst.append( (key, val))
# 	for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
# 		f.write("{0}: {1}".format(key, val) + "\n")	
# print('list can be found in ./swetha_word_freq.txt')



















