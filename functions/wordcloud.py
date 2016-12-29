import os
import shutil
import json
import glob
from PIL import Image


class WordCloud:
    WORD_CLOUD_INPUT_PATH = 'data/word_clouds/input_data/'
    WORD_CLOUD_OUTPUT_PATH = 'data/word_clouds/output/'
    WORD_CLOUD_EXCLUDED_WORDS_PATH = 'data/word_clouds/excluded_words/'
    WORD_CLOUD_IMAGE_PATH = 'data/word_clouds/background_images/'

    WORD_CLOUD_TYPES = ['default', 'polarity', 'layered']
    WORD_CLOUD_SHAPES = ['circular', 'rectangular', 'image']
    WORD_CLOUD_FONT_TYPES = ['linear', 'square_root']

    DEFAULT_NUM_WORDS_TO_INCLUDE = 1000
    DEFAULT_MIN_WORD_LENGTH = 3
    DEFAULT_MAX_WORD_LENGTH = 100
    DEFAULT_OUTPUT_NAME = 'TIME_OF_CREATION.png'
    DEFAULT_INPUT_NAME = 'total.txt'
    DEFAULT_DIMENSIONS = [1000, 1000]
    DEFAULT_COLORS = [[255, 255, 255]]
    DEFAULT_POLAR_COLOR_1 = [[255, 0, 0]]
    DEFAULT_POLAR_COLOR_2 = [[0, 255, 0]]
    DEFAULT_SHAPE = 'circular'
    DEFAULT_MIN_FONT_SIZE = 10
    DEFAULT_MAX_FONT_SIZE = 40
    DEFAULT_FONT_TYPE = 'linear'
    DEFAULT_EXCLUDED_WORDS = []
    DEFAULT_IMAGE_NAME = "None"

    def __init__(self, wc_type='default', preferences=None):
        if preferences is None:
            preferences = dict()
        assert isinstance(wc_type, str), "wc_type must be a string"
        assert wc_type in WordCloud.WORD_CLOUD_TYPES, "wc_type must be in WordCloud.WORD_CLOUD_TYPES: {0}"\
            .format(str(WordCloud.WORD_CLOUD_TYPES))
        assert isinstance(preferences, dict), "Preferences must be a dictionary, not a {0}".format(type(preferences))

        self.wc_type = wc_type
        self.__preferences = self._default_preferences()

        for key, val in preferences.items():
            self.__preferences[key] = val

        self.__safe_to_save = len(preferences) == 0
        self.issues = None
        self.setup_word_cloud_starter_files()

    @staticmethod
    def newest_file(path=WORD_CLOUD_OUTPUT_PATH, suffix='.png', strip_output=False):
        """Returns the newest created file in the directory
        http://stackoverflow.com/a/34551233/6587177
        """

        file = max(glob.iglob('{}*{}'.format(path, suffix)), key=os.path.getctime)
        if strip_output:
            return file.replace(path, '')
        return file

    @staticmethod
    def get_image_size(fname):
        try:
            with Image.open(fname) as image:
                return image.size
        except OSError:
            return 0, 0

    @staticmethod
    def get_excluded_word_files():
        return [f for f in os.listdir(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH)
                if os.path.isfile(os.path.join(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH, f))]

    @staticmethod
    def get_input_text_files():
        files = [f for f in os.listdir(WordCloud.WORD_CLOUD_INPUT_PATH)
                if os.path.isfile(os.path.join(WordCloud.WORD_CLOUD_INPUT_PATH, f)) and f.endswith('freq.txt')]
        files = ['total.txt'] + files
        return files

    @staticmethod
    def get_image_files():
        return [f for f in os.listdir(WordCloud.WORD_CLOUD_IMAGE_PATH)
                if os.path.isfile(os.path.join(WordCloud.WORD_CLOUD_IMAGE_PATH, f)) and
                (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.bmp'))]

    def _default_preferences(self):
        return WordCloud.get_default_preferences(self.wc_type)

    @staticmethod
    def get_default_preferences(wc_type):
        if wc_type == 'default':
            return {
                'num_words_to_include': WordCloud.DEFAULT_NUM_WORDS_TO_INCLUDE,
                'min_word_length': WordCloud.DEFAULT_MIN_WORD_LENGTH,
                'max_word_length': WordCloud.DEFAULT_MAX_WORD_LENGTH,
                'excluded_words': WordCloud.DEFAULT_EXCLUDED_WORDS,
                'max_font_size': WordCloud.DEFAULT_MAX_FONT_SIZE,
                'min_font_size': WordCloud.DEFAULT_MIN_FONT_SIZE,
                'output_name': WordCloud.DEFAULT_OUTPUT_NAME,
                'dimensions': WordCloud.DEFAULT_DIMENSIONS,
                'input_name': WordCloud.DEFAULT_INPUT_NAME,
                'image_name': WordCloud.DEFAULT_IMAGE_NAME,
                'font_type': WordCloud.DEFAULT_FONT_TYPE,
                'colors': WordCloud.DEFAULT_COLORS,
                'shape': WordCloud.DEFAULT_SHAPE,
                'type': wc_type,
            }
        elif wc_type == 'polarity':
            return {
                'num_words_to_include': WordCloud.DEFAULT_NUM_WORDS_TO_INCLUDE,
                'min_word_length': WordCloud.DEFAULT_MIN_WORD_LENGTH,
                'max_word_length': WordCloud.DEFAULT_MAX_WORD_LENGTH,
                'excluded_words': WordCloud.DEFAULT_EXCLUDED_WORDS,
                'max_font_size': WordCloud.DEFAULT_MAX_FONT_SIZE,
                'min_font_size': WordCloud.DEFAULT_MIN_FONT_SIZE,
                'output_name': WordCloud.DEFAULT_OUTPUT_NAME,
                'color_set_1': WordCloud.DEFAULT_POLAR_COLOR_1,
                'color_set_2': WordCloud.DEFAULT_POLAR_COLOR_2,
                'dimensions': WordCloud.DEFAULT_DIMENSIONS,
                'text_set_1': WordCloud.DEFAULT_INPUT_NAME,
                'text_set_2': WordCloud.DEFAULT_INPUT_NAME,
                'image_name': WordCloud.DEFAULT_IMAGE_NAME,
                'font_type': WordCloud.DEFAULT_FONT_TYPE,
                'shape': WordCloud.DEFAULT_SHAPE,
                'type': wc_type,
            }
        elif wc_type == 'layered':
            return {
                'num_words_to_include': WordCloud.DEFAULT_NUM_WORDS_TO_INCLUDE,
                'min_word_length': WordCloud.DEFAULT_MIN_WORD_LENGTH,
                'max_word_length': WordCloud.DEFAULT_MAX_WORD_LENGTH,
                'excluded_words': WordCloud.DEFAULT_EXCLUDED_WORDS,
                'max_font_size': WordCloud.DEFAULT_MAX_FONT_SIZE,
                'min_font_size': WordCloud.DEFAULT_MIN_FONT_SIZE,
                'output_name': WordCloud.DEFAULT_OUTPUT_NAME,
                'dimensions': WordCloud.DEFAULT_DIMENSIONS,
                'font_type': WordCloud.DEFAULT_FONT_TYPE,
                'type': wc_type,

                'num_text_sets': None,
                'text_sets': [],
                'image_sets': [],
                'color_sets': []
            }
        else:
            raise ValueError("Invalid word cloud type: {}".format(wc_type))

    def verify_word_cloud_setup(self) -> dict:
        """Verifies that all the settings for a word cloud are met
        Return:
            A dictionary with keys being files corresponding to qualities for this word cloud, and values being
            errors that arose when verifying conditions. If and only if the dictionary is empty is the word cloud
            fully ready for creation
        """
        verification = dict()
        if self.wc_type == 'default':
            attributes_to_check = {
                'num_words_to_include': self.assert_num_words_to_include,
                'min_word_length': lambda x: self.assert_word_length(x, 'min'),
                'max_word_length': lambda x: self.assert_word_length(x, 'max'),
                'excluded_words': lambda x: list(map(self.assert_excluded_words_for_wc, x)),
                'max_font_size': lambda x: self.assert_font_size(x, 'max'),
                'min_font_size': lambda x: self.assert_font_size(x, 'min'),
                'output_name': self.assert_output_name_for_wc,
                'image_name': self.assert_image_name_for_wc,
                'dimensions': self.assert_dimensions_for_wc,
                'input_name': self.assert_input_name_for_wc,
                'font_type': self.assert_font_type_for_wc,
                'colors': self.assert_colors_for_wc,
                'shape': self.assert_shape_for_wc
            }
        elif self.wc_type == 'polarity':
            attributes_to_check = {
                'num_words_to_include': self.assert_num_words_to_include,
                'min_word_length': lambda x: self.assert_word_length(x, 'min'),
                'max_word_length': lambda x: self.assert_word_length(x, 'max'),
                'excluded_words': lambda x: list(map(self.assert_excluded_words_for_wc, x)),
                'max_font_size': lambda x: self.assert_font_size(x, 'max'),
                'min_font_size': lambda x: self.assert_font_size(x, 'min'),
                'output_name': self.assert_output_name_for_wc,
                'color_set_1': self.assert_colors_for_wc,
                'color_set_2': self.assert_colors_for_wc,
                'dimensions': self.assert_dimensions_for_wc,
                'text_set_1': lambda name: self.assert_text_set(name, 1),
                'text_set_2': lambda name: self.assert_text_set(name, 2),
                'image_name': self.assert_image_name_for_wc,
                'font_type': self.assert_font_type_for_wc,
                'shape': self.assert_shape_for_wc,
            }
        elif self.wc_type == 'layered':
            attributes_to_check = {
                'num_words_to_include': self.assert_num_words_to_include,
                'min_word_length': lambda x: self.assert_word_length(x, 'min'),
                'max_word_length': lambda x: self.assert_word_length(x, 'max'),
                'excluded_words': lambda x: list(map(self.assert_excluded_words_for_wc, x)),
                'max_font_size': lambda x: self.assert_font_size(x, 'max'),
                'min_font_size': lambda x: self.assert_font_size(x, 'min'),
                'output_name': self.assert_output_name_for_wc,
                'dimensions': self.assert_dimensions_for_wc,
                'color_sets': lambda x: list(map(self.assert_colors_for_wc, x)),
                'image_sets': lambda x: list(map(self.assert_image_name_for_wc, x)),
                'text_sets': self.assert_text_set,
                'font_type': self.assert_font_type_for_wc,
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
        self.issues = verification
        if self.__safe_to_save:
            self.write_json()
        return verification

    def ready(self):
        return self.__safe_to_save

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

    @staticmethod
    def setup_word_cloud_starter_files():
        """Creates the word cloud directory along with starter files"""
        shutil.rmtree(WordCloud.WORD_CLOUD_INPUT_PATH) if os.path.exists(WordCloud.WORD_CLOUD_INPUT_PATH) else None
        os.makedirs(WordCloud.WORD_CLOUD_INPUT_PATH, exist_ok=True)
        os.makedirs(WordCloud.WORD_CLOUD_OUTPUT_PATH, exist_ok=True)
        os.makedirs(WordCloud.WORD_CLOUD_EXCLUDED_WORDS_PATH, exist_ok=True)
        os.makedirs(WordCloud.WORD_CLOUD_IMAGE_PATH, exist_ok=True)

    def write_json(self):
        assert self.__safe_to_save, "Preferences have not been verified yet, run `verify_word_cloud_setup()` first"

        with open(WordCloud.WORD_CLOUD_INPUT_PATH + 'word_cloud_data.txt', mode='w', encoding='utf-8') as file:
            preferences_copy = self.__preferences.copy()
            if preferences_copy['type'] == 'default':
                preferences_copy['input_name'] = 'text.txt'
            elif preferences_copy['type'] == 'polarity':
                preferences_copy['text_set_1'] = 'text_set1.txt'
                preferences_copy['text_set_2'] = 'text_set2.txt'
            elif preferences_copy['type'] == 'layered':
                for i in range(len(preferences_copy['text_sets'])):
                    preferences_copy['text_sets'][i] = 'text_set{0}.txt'.format(i + 1)
            json.dump(preferences_copy, file)

    def get_preference(self, preference_name):
        return self.__preferences[preference_name] if preference_name in self.__preferences else None

    def set_output_name(self, output_name):
        self.assert_output_name_for_wc(output_name)
        self.__preferences['output_name'] = output_name

    # -------------------------------------   ASSERTING VALUES ARE VALID ----------------------------------- #

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
        assert 0 < limit, "This would be a very boring word cloud with no words"

    @staticmethod
    def assert_dimensions_for_wc(dimensions):
        assert isinstance(dimensions, list) or isinstance(dimensions, tuple), "Dimensions is an invalid type"
        x, y = dimensions
        assert isinstance(x, int), "width needs to be an integer"
        assert isinstance(y, int), "height needs to be an integer"
        assert 0 < x, "width must be greater than 0"
        assert 0 < y, "height must be greater than 0"

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
        except ValueError:
            raise AssertionError("color should be made of integers separated by commas and spaces, e.g. 0, 255, 255")
        WordCloud._assert_color_for_wc(split)
        return split

    @staticmethod
    def _assert_color_for_wc(color):
        assert (isinstance(color, tuple) or isinstance(color, list)) and all(isinstance(ele, int) for ele in color), (
            "Color must be a tuple (or list) with 3 ints, e.g. "
            "(100, 100, 100). Received {}: {}".format(type(color), str(color))
        )
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
            if os.path.isfile(WordCloud.WORD_CLOUD_INPUT_PATH + name):
                self.freq_to_raw(WordCloud.WORD_CLOUD_INPUT_PATH + name,
                                 WordCloud.WORD_CLOUD_INPUT_PATH + 'text.txt')
            else:
                assert os.path.isfile(name), "{0} does not exist".format(name)
                self.freq_to_raw(name, WordCloud.WORD_CLOUD_INPUT_PATH + 'text.txt')

    def assert_text_set(self, name, set_num=None):
        if set_num is None:
            for i in range(1, len(name) + 1):
                self.assert_text_set(name[i - 1], i)
            return
        if not os.path.isfile(WordCloud.WORD_CLOUD_INPUT_PATH + 'text_set{0}.txt'.format(set_num)):
            if os.path.isfile(WordCloud.WORD_CLOUD_INPUT_PATH + name):
                self.freq_to_raw(WordCloud.WORD_CLOUD_INPUT_PATH + name,
                                 WordCloud.WORD_CLOUD_INPUT_PATH + 'text_set{0}.txt'.format(set_num))
            else:
                assert os.path.isfile(name), "{0} does not exist".format(name)
                self.freq_to_raw(name, WordCloud.WORD_CLOUD_INPUT_PATH +
                                 'text_set{0}.txt'.format(set_num))

    def assert_font_size(self, value, min_or_max):
        assert min_or_max in ['min', 'max'], "Must pass a min_or_max in ['min', 'max']"
        assert isinstance(value, int), "Value must be an integer"
        if min_or_max == 'min':
            assert 0 < value < self.__preferences['max_font_size'], "The min value should be in between 0 and {0}"\
                .format(self.__preferences['max_font_size'])
        else:
            assert 0 < value and self.__preferences['min_font_size'] < value, \
                "The max font size should be greater than {0}".format(self.__preferences['min_font_size'])

    @staticmethod
    def assert_excluded_words_for_wc(file_path):
        assert isinstance(file_path, str), "file_path must be a string"
        assert os.path.isfile(file_path), "the specified file_path does not exist"

    def assert_image_name_for_wc(self, img_name):
        assert isinstance(img_name, str), "image_name should be of type string"
        if self.__preferences.get('shape') == 'image' or self.__preferences.get('type') == 'layered':
            assert os.path.isfile(img_name), "the specified image file_path does not exist: {}".format(img_name)
        else:
            assert img_name == 'None', (
                'Only word clouds of shape "image" can have a background image. Current type is '
                '{}'.format(self.__preferences['shape'])
            )

    @staticmethod
    def valid_picture(picture_name):
        return ' ' not in picture_name and ('.png' in picture_name or '.bmp' in picture_name)

    @staticmethod
    def hex_to_rgb(value):
        """Return (red, green, blue) for the color given as a hex string '#rrggbb'.
        http://stackoverflow.com/a/214657/6587177
        """
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
