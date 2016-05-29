from math import ceil
from datetime import date, timedelta


class CustomDate():
    months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
              'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12,}

    months_reversed = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                       7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    days_of_week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    def __init__(self, date_str):
        """Constructor for CustomDate object. has following fields:
        String full_date   : the full date of this object, e.g. Wednesday, April 13, 2016 at 11:54pm PDT
        String week_day    : the day of the week e.g. Monday
        String time        : the time e.g. 11:54pm
        String time_zone   : the time zone e.g. PDT
        datetime.date date : a date object representation of the year, month and day
            e.g. datetime.date(2016, 4, 13)
        """
        if type(date_str) is type(self):
            date_str = date_str.full_date
        self.full_date = date_str
        temp = date_str.split(',')
        self.week_day = temp[0]
        month, day_of_month = temp[1].split()
        year, _, self.time, self.time_zone = date_str.split(',')[2].split()

        self.date = date(int(year), int(CustomDate.months[month]), int(day_of_month))

    @classmethod
    def from_date(cls, date_obj):
        """Alternative constructor using a datetime.date object
        Creates a CustomDate object with a default time of 12:00am PDT
        """
        year = None
        if len(str(date_obj.year)) == 2:
            if date_obj.year <= 17:
                year = date_obj.year + 2000
            else:
                year = date_obj.year + 1900
        else:
            year = date_obj.year
        date_string = "{0}, {1} {2}, {3} at 12:00am PDT".format(
            CustomDate.days_of_week[date_obj.weekday()],
            CustomDate.months_reversed[date_obj.month],
            date_obj.day,
            year)
        return cls(date_string)

    @classmethod
    def from_date_string(cls, date_string):
        """Alternative constructor using a date string in the form '{month}/{day}/{year}'"""
        date_lst = [int(ele) for ele in date_string.split('/')]
        return CustomDate.from_date(date(date_lst[2], date_lst[0], date_lst[1]))

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

    def time(self):
        return self.time

    def minutes(self):
        minutes = self.time[:-2]
        minutes = (int((minutes[:minutes.find(':')])) % 12) \
                  * 60 + int(minutes[minutes.find(':') + 1:])
        if 'pm' in self.time:
            minutes += 12 * 60
        return minutes

    def minutes_to_time(minutes):
        assert minutes >= 0, "You can't have negative minutes"
        assert minutes <= 24 * 60, "You passed more than 1 day of minutes"

        hours = ceil(minutes // 60)
        if hours == 0:
            hours = 12
        elif hours > 12:
            hours -= 12
        mins = str(minutes % 60)
        if len(mins) == 1:
            mins = '0' + mins
        return "{0}:{1}{2}".format(hours, mins, 'pm' if minutes >= 12 * 60 else 'am')

    def distance_from(self, other):
        assert isinstance(other, CustomDate), "You must pass a valid CustomDate object"



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
        return "CustomDate({0})".format(repr(self.full_date))

    def __eq__(self, other):
        if isinstance(other, CustomDate):
            return False
        return self.date == other.date and self.minutes() == other.minutes()

    def __hash__(self):
        return hash(self.full_date)

    def __lt__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        if self.date < other.date:
            return True
        elif self.date == other.date:
            if self.minutes() < other.minutes():
                return True
        return False

    def __le__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        if self.date < other.date:
            return True
        elif self.date == other.date:
            if self.minutes() <= other.minutes():
                return True
        return False

    def __gt__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        if self.date > other.date:
            return True
        elif self.date == other.date:
            if self.minutes() > other.minutes():
                return True
        return False

    def __ge__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        if self.date > other.date:
            return True
        elif self.date == other.date:
            if self.minutes() >= other.minutes():
                return True
        return False


def bsearch_index(lst, date, low=0, high=None, key=lambda x:x):
    if high is None:
        high = len(lst) - 1
    mid = (low + high) // 2
    while key(lst[mid]) != date and mid > low and mid < high:
        if key(lst[mid]) > date:
            high = mid - 1
            mid = (low + high) // 2
        else:
            low = mid + 1
            mid = (low + high) // 2

    return mid
