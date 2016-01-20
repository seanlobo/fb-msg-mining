with open('./readableChatLog.py', 'r', encoding='utf-8') as f:
	log = eval(f.read())





class MessageHelper():

	def __init__(self, log):
		self.log = log
		self.length = len(self.log)

	def get(self, pos, part=None):
		assert pos < self.length and pos >= 0, 'invalid position'
		if part is None:
			return self.log[pos]

		assert part.lower() in ['m', 'p', 't'], "invalid search token"

		if part.lower() == 'p':
			part = 0
		elif part.lower() == 'm':
			part = 1
		else:
			part = 2

		return self.log[pos][part]

	def indexOf(self, token, start=0):
		assert start < self.length, "invalid start length"
		for i in range(start, self.length):
			if token in self.log[i][1]:
				return i
		return -1

	def indexOf_all(self, token):
		res = []
		for i in range(self.length):
			if token in self.log[i][1]:
				res.append(i)
		return res

	def find(self, token, before=10, after=10):
		lst = self.indexOf_all(token)
		if lst == list():
			return

		for pos in lst:
			for i in range(max(0, pos - before), min(self.length, pos + after)):
				print(self.get(i,'m'))
			print('\n')




test = MessageHelper(log)



print(test.find('\U000fe32c'))












