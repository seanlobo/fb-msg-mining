#	Author: Sean Lobo
#	Date: Feb 16, 2016
#	File Purpose: Clean up facebook chat data

from collections import Counter
import os


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


def get_words(convoReader):
    def raw_msgs(convo):
        freqs = dict()
        for person, message, time in convo.convo:
            if person not in freqs:
                freqs[person] = [message.lower()]
            else:
                freqs[person] += [message.lower()]
        return freqs

    def raw_words(msg_dict):
        word_dict = dict()
        for key in msg_dict.keys():
            word_dict[key] = []
        for key, val in msg_dict.items():
            for msg in val:
                for word in msg.split():
                    word_dict[key].append(word)
        return word_dict

    def clean_words(word_dict):
        cleaned = dict()
        for key, val in word_dict.items():
            cleaned[key] = sorted(val)

        for key, val in cleaned.items():
            end = 0
            for i in range(len(val)):
                end = i
                if val[i] > 'z' * 10:
                    break
            cleaned[key] = val[:end]

        for key, val in cleaned.items():
            new = []
            for ele in val:
                if 'www.' not in ele and '.com' not in ele:
                    new.append(ele)
            cleaned[key] = new

        for key, val in cleaned.items():
            new = []
            for ele in val:
                new.append(ele.strip('.!123456789-+?><}{][()\'\""\\ /*#$%^&#@,'))
            cleaned[key] = new

        return cleaned

    cleaned = clean_words(raw_words(raw_msgs(convoReader)))
    res = dict()
    for key, val in cleaned.items():
        res[key] = Counter(val)
    return res


def write_to_files(words, directory, chat):
    os.makedirs(directory + chat, exist_ok=True)
    for person, counter in words.items():
        split = person.split()
        pers = ''
        for i in range(len(split) - 1):
            pers += split[i]
            pers += '-'
        pers += split[-1]
        with open(directory + chat + '/' + pers + '_word_freq.txt', mode='x', encoding='utf-8') as f:
            lst = []
            for key, val in counter.items():
                lst.append((key, val))
            for key, val in sorted(lst, key=lambda x: x[1], reverse=True):
                f.write("{0}: {1}".format(key, val) + "\n")


def write_to_file_total(tot_words, directory, chat):
    os.makedirs(directory + chat, exist_ok=True)
    with open(directory + chat + '/total.txt', mode='x', encoding='utf-8') as f:
        for key, val in tot_words.most_common():
            f.write("{0}: {1}".format(key, val) + "\n")
