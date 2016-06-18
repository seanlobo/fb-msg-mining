import os
import shutil

from functions.baseconvoreader import BaseConvoReader

class WordCloud:
    word_cloud_path = 'data/wordClouds/'

    def __init__(self, path):
        self._path = path

    def verify_word_cloud_setup(self, type="circular"):
        """Verifies that all the settings for a word cloud are met"""
        verification = dict()
        if type == "circular":
            assertions = [self._assert_dimensions_for_wc, self._assert_num_text_set_for_wc,
                          self._assert_color_for_wc, self._assert_output_name_for_wc]
            file_names = ['dimensions.txt', 'num_text_sets.txt', 'colors.txt', 'output_name.txt']
            fn = lambda num: assertions[num]
            for i in range(4):
                try:
                    assert os.path.isfile(WordCloud.word_cloud_path + file_names[i]), \
                        "{0} is missing".format(file_names[i])
                    with open(WordCloud.word_cloud_path + file_names[i], mode='r') as f:
                        if i == 0:  # dimension
                            val = [int(ele) for ele in f.read().split('\n')]
                        elif i == 1:  # number of text sets
                            val = int(f.read())
                        elif i == 2:  # colors
                            val = [[int(col) for col in line.split(', ')] for line in f]
                        else:  # output name
                            val = f.read()
                    if i != 2:
                        fn(i)(val)
                    else:
                        [fn(2)(data) for data in val]
                except (AssertionError, ValueError) as e:
                    verification[file_names[i]] = e
        return verification

        # To run java stuff fro here
        # http://stackoverflow.com/questions/438594/how-to-call-java-objects-and-functions-from-cpython


    @staticmethod
    def freq_to_raw(freqs, output):
        string = ""
        with open(freqs) as f:
            for line in iter(f.readline, ''):
                word = line.split(': ')
                if len(word) == 2:
                    if '\n' in word[1]:
                        word[1] = word[1][:word[1].find('\n')]
                    if int(word[1]) >= 5:
                        string += (word[0] + " ") * int(word[1])

        with open(output, mode='x') as f:
            f.write(string)
        print('done\a')

    @staticmethod
    def set_dimensions(x, y):
        WordCloud._assert_dimensions_for_wc([x, y])

        with open(WordCloud.word_cloud_path + 'dimensions.txt', mode='w', encoding='utf-8') as f:
            f.write(str(x) + '\n' + str(y))

    @staticmethod
    def set_num_word_sets(num):
        WordCloud._assert_num_text_set_for_wc(num)

        with open(WordCloud.word_cloud_path + 'num_text_sets.txt', mode='w', encoding='utf-8') as f:
            f.write(str(num))

    @staticmethod
    def set_colors(color):
        """Writes the passed colors to the current colors.txt file"""
        WordCloud._assert_color_for_wc(color)

        with open(WordCloud.word_cloud_path + 'colors.txt', mode='w', encoding='utf-8') as f:
            f.write('{0}, {1}, {2}\n'.format(*color))

    @staticmethod
    def append_color(color):
        """Appends the set colors to colors.txt if colors exists otherwise calls set_colors"""
        WordCloud._assert_color_for_wc(color)
        if os.path.isfile(WordCloud.word_cloud_path + 'colors.txt'):
            with open(WordCloud.word_cloud_path + 'colors.txt', mode='a', encoding='utf-8') as f:
                f.write('{0}, {1}, {2}\n'.format(*color))
        else:
            WordCloud.set_colors(color)

    @staticmethod
    def set_output_name(name):
        """Writes the passed name to output_name.txt"""
        WordCloud._assert_output_name_for_wc(name)

        with open(WordCloud.word_cloud_path + 'output_name.txt', mode='w', encoding='utf-8') as f:
            f.write(name)

    @staticmethod
    def _assert_dimensions_for_wc(dimensions):
        assert isinstance(dimensions, list) or isinstance(dimensions, tuple), "Dimensions is an invalid type"
        x, y = dimensions
        assert isinstance(x, int), "X needs to be an integer"
        assert isinstance(y, int), "Y needs to be an integer"
        assert 0 < x, "X must be greater than 0"
        assert 0 < y, "Y must be greater than 0"

    @staticmethod
    def _assert_color_for_wc(color):
        assert (isinstance(color, tuple) or isinstance(color, list)) and all(isinstance(ele, int) for ele in color), \
            "Color must be a tuple (or list) with 3 ints, e.g. (100, 100, 100)"
        assert all(0 <= val <= 255 for val in color), "All rgb values must be between 0 and 255"

    @staticmethod
    def _assert_output_name_for_wc(name):
        assert isinstance(name, str), "Name should be a string"
        assert '.png' in name, "Name should be a .png file"

    @staticmethod
    def _assert_num_text_set_for_wc(num):
        assert isinstance(num, int), "Num must be an integer"
        assert num >= 1, "Num should be greater than 1"
