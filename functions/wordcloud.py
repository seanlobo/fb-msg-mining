import os
import shutil
import datetime
import sys
import json


class WordCloud:
    WORD_CLOUD_INPUT_PATH = 'data/word_clouds/input_data/'
    WORD_CLOUD_OUTPUT_PATH = 'data/word_clouds/output/'
    WORD_CLOUD_TYPES = {'default': ['output_name', 'dimensions', 'colors', 'input_name', 'num_words_to_include',
                                    'min_word_length'],
                        }
    WORD_CLOUD_SHAPES = ['circular', 'rectangular']
    WORD_CLOUD_FONT_TYPES = ['linear', 'square_root']

    _DEFAULT_NUM_WORDS_TO_INCLUDE = 1000
    _DEFAULT_MIN_WORD_LENGTH = 3
    _DEFAULT_MAX_WORD_LENGTH = 100
    _DEFAULT_OUTPUT_NAME = 'word_cloud_created_at_{0}.png'.format(str(datetime.datetime.now()).replace(' ', '_'))
    _DEFAULT_INPUT_NAME = 'total.txt'
    _DEFAULT_DIMENSIONS = [1000, 1000]
    _DEFAULT_COLORS = [[255, 255, 255]]
    _DEFAULT_SHAPE = 'circular'
    _DEFAULT_MIN_FONT_SIZE = 10
    _DEFAULT_MAX_FONT_SIZE = 40
    _DEFAULT_FONT_TYPE = 'linear'

    def __init__(self, wc_type='default', preferences=None):
        if preferences is None:
            preferences = dict()
        assert isinstance(wc_type, str), "wc_type must be a string"
        assert wc_type in WordCloud.WORD_CLOUD_TYPES, "wc_type must be in WordCloud.WORD_CLOUD_TYPES: {0}"\
            .format(str(WordCloud.WORD_CLOUD_TYPES.keys()))
        assert isinstance(preferences, dict), "Preferences must be a dictionary, not a {0}".format(type(preferences))

        self.wc_type = wc_type
        self.__preferences = self._default_preferences()

        for key, val in preferences.items():
            self.__preferences[key] = val

        self.__safe_to_save = len(preferences) == 0
        self.setup_word_cloud_starter_files()

    def _default_preferences(self):
        return WordCloud.get_default_preferences(self.wc_type)

    @staticmethod
    def get_default_preferences(wc_type):
        if wc_type == 'default':
            return {'output_name': WordCloud._DEFAULT_OUTPUT_NAME,
                    'dimensions': WordCloud._DEFAULT_DIMENSIONS,
                    'colors': WordCloud._DEFAULT_COLORS,
                    'input_name': WordCloud._DEFAULT_INPUT_NAME,
                    'num_words_to_include': WordCloud._DEFAULT_NUM_WORDS_TO_INCLUDE,
                    'min_word_length': WordCloud._DEFAULT_MIN_WORD_LENGTH,
                    'max_word_length': WordCloud._DEFAULT_MAX_WORD_LENGTH,
                    'max_font_size': WordCloud._DEFAULT_MAX_FONT_SIZE,
                    'min_font_size': WordCloud._DEFAULT_MIN_FONT_SIZE,
                    'shape': WordCloud._DEFAULT_SHAPE,
                    'font_type': WordCloud._DEFAULT_FONT_TYPE
                    }

    def verify_word_cloud_setup(self) -> dict:
        """Verifies that all the settings for a word cloud are met
        Return:
            A dictionary with keys being files corresponding to qualities for this word cloud, and values being
            errors that arose when verifying conditions. If and only if the dictionary is empty is the word cloud
            fully ready for creation
        """
        verification = dict()
        if self.wc_type == 'default':
            attributes_to_check = {'output_name': WordCloud.assert_output_name_for_wc,
                                   'dimensions': WordCloud.assert_dimensions_for_wc,
                                   'colors': WordCloud.assert_colors_for_wc,
                                   'input_name': self.assert_input_name_for_wc,
                                   'num_words_to_include': WordCloud.assert_num_words_to_include,
                                   'min_word_length': lambda x: self.assert_word_length(x, 'min'),
                                   'max_word_length': lambda x: self.assert_word_length(x, 'max'),
                                   'max_font_size': lambda x: self.assert_font_size(x, 'max'),
                                   'min_font_size': lambda x: self.assert_font_size(x, 'min'),
                                   'font_type': WordCloud.assert_font_type_for_wc,
                                   'shape': WordCloud.assert_shape_for_wc
                                   }
        else:
            raise ValueError("Invalid word cloud type: {0}".format(self.wc_type))

        for attribute in attributes_to_check:
            try:
                assert attribute in self.__preferences, "Missing {0} attribute in preferences".format(attribute)

                # calls the assertion from attributes_to_check dictionary with value from preferences
                attributes_to_check[attribute](self.__preferences[attribute])
            except AssertionError as e:
                verification[attribute] = e

        self.__safe_to_save = len(verification) == 0
        if self.__safe_to_save:
            self.write_json()
        return verification

    @staticmethod
    def freq_to_raw(freqs: str, output: str, key=lambda x: True, min_occurence=5):
        """Converts a frequency file into a raw file, with passed constraints
        Parameters:
            freqs: the path to the frequency file
            output: the path to the new output file
            key: A filter to pass on words that determines whether they will be used
            min_occurence (optional): The minimum frequency of words that will be put into the raw file
        """
        string = ""
        with open(freqs) as f:
            for line in iter(f.readline, ''):
                word = line.split(': ')
                if len(word) == 2:
                    if '\n' in word[1]:
                        word[1] = word[1][:word[1].find('\n')]
                    if key(word[0]) and min_occurence <= int(word[1]):
                        string += (word[0] + " ") * int(word[1])

        with open(output, mode='x') as f:
            f.write(string)

    def setup_word_cloud_starter_files(self):
        """Creates the word cloud directory along with starter files"""
        shutil.rmtree(WordCloud.WORD_CLOUD_INPUT_PATH) if os.path.exists(WordCloud.WORD_CLOUD_INPUT_PATH) else None
        os.makedirs(WordCloud.WORD_CLOUD_INPUT_PATH, exist_ok=True)
        os.makedirs(WordCloud.WORD_CLOUD_OUTPUT_PATH, exist_ok=True)

    def write_json(self):
        assert self.__safe_to_save, "Preferences have not been verified yet, run `verify_word_cloud_setup()` first"

        with open(WordCloud.WORD_CLOUD_INPUT_PATH + 'word_cloud_data.txt', mode='w', encoding='utf-8') as file:
            preferences_copy = self.__preferences.copy()
            preferences_copy['input_name'] = 'text.txt'
            json.dump(preferences_copy, file)

    def get_preference(self, preference_name):
        return self.__preferences[preference_name] if preference_name in self.__preferences else None


    ######################################## ASSERTING VALUES ARE VALID ########################################

    def assert_word_length(self, length, min_or_max):
        assert min_or_max in ['min', 'max'], "must pass in argument 'min' or 'max'"

        assert isinstance(length, int), "length must be an integer"
        if min_or_max == 'max':
            assert length >= self.__preferences['min_word_length']
        else:
            assert 0 < length <= self.__preferences['max_word_length']

    @staticmethod
    def assert_num_words_to_include(limit):
        assert isinstance(limit, int), "limit must be an integer"
        assert 0 < limit, "This would be a very boring word cloud if I let you give a frequency less than 1"

    @staticmethod
    def assert_dimensions_for_wc(dimensions):
        assert isinstance(dimensions, list) or isinstance(dimensions, tuple), "Dimensions is an invalid type"
        x, y = dimensions
        assert isinstance(x, int), "X needs to be an integer"
        assert isinstance(y, int), "Y needs to be an integer"
        assert 0 < x, "X must be greater than 0"
        assert 0 < y, "Y must be greater than 0"

    @staticmethod
    def assert_colors_for_wc(colors):
        for color in colors:
            WordCloud._assert_color_for_wc(color)

    @staticmethod
    def assert_color_string(color):
        split = color.split(', ')
        assert len(split) == 3, "color is invalid "
        try:
            split = list(map(int, split))
        except ValueError as e:
            raise AssertionError("color should be made of integers separated by commas and spaces, e.g. 0, 255, 255")
        WordCloud._assert_color_for_wc(split)
        return split

    @staticmethod
    def _assert_color_for_wc(color):
        assert (isinstance(color, tuple) or isinstance(color, list)) and all(isinstance(ele, int) for ele in color), \
            "Color must be a tuple (or list) with 3 ints, e.g. (100, 100, 100)"
        assert all(0 <= val <= 255 for val in color), "All rgb values must be between 0 and 255"

    @staticmethod
    def assert_output_name_for_wc(name: str):
        assert isinstance(name, str), "Name should be a string"
        assert '.png' in name, "Name should be a .png file"
        assert ' ' not in name, "File names can't have spaces"

    @staticmethod
    def assert_shape_for_wc(shape: str):
        assert isinstance(shape, str), "Shape must be a string"
        assert shape in WordCloud.WORD_CLOUD_SHAPES, "shape must be in: {0}, not {1}"\
            .format(WordCloud.WORD_CLOUD_SHAPES, shape)

    @staticmethod
    def assert_font_type_for_wc(font_type):
        assert font_type in WordCloud.WORD_CLOUD_FONT_TYPES, "font_type needs to be in: {0}"\
            .format(WordCloud.WORD_CLOUD_FONT_TYPES)

    @staticmethod
    def assert_num_text_set_for_wc(num: int):
        assert isinstance(num, int), "Num must be an integer"
        assert num >= 1, "Num should be greater than 1"

    def assert_input_name_for_wc(self, name: str):
        if not os.path.isfile(WordCloud.WORD_CLOUD_INPUT_PATH + 'text.txt'):
            assert os.path.isfile(WordCloud.WORD_CLOUD_INPUT_PATH + name), "{0} does not exist".format(name)
            self.freq_to_raw(WordCloud.WORD_CLOUD_INPUT_PATH + name, WordCloud.WORD_CLOUD_INPUT_PATH + 'text.txt')

    def assert_font_size(self, value, min_or_max):
        assert min_or_max in ['min', 'max'], "Must pass a min_or_max in ['min', 'max']"
        assert isinstance(value, int), "Value must be an integer"
        if min_or_max == 'min':
            assert 0 < value < self.__preferences['max_font_size'], "The min value should be in between 0 and {0}"\
                .format(self.__preferences['max_font_size'])
        else:
            assert 0 < value and self.__preferences['min_font_size'] < value, \
                "The max font size should be greater than {0}".format(self.__preferences['min_font_size'])

