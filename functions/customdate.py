from datetime import date, timedelta



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
		return "{0}/{1}/{2}".format(self.date.month, self.date.day, self.date.year)

	def day(self):
		return self.date.day

	def month(self):
		return self.date.month

	def weekday(self):
		return self.date.weekday()

	def year(self):
		return self.date.year

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




