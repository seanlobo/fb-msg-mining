import os
import shutil


class WordCloud:
    WORD_CLOUD_PATH = 'data/wordClouds/'
    WORD_CLOUD_TYPES = {'circular': ['output_name', 'dimensions', 'colors', 'input_name', 'num_words_to_include',
                                     'min_word_length'],
                        'rectangular': ['output_name', 'dimensions', 'colors', 'input_name', 'num_words_to_include',
                                        'min_word_length']}

    def __init__(self, wc_type, path):
        assert wc_type in WordCloud.WORD_CLOUD_TYPES

        self.wc_type = wc_type
        self.path = path

    def verify_word_cloud_setup(self) -> dict:
        """Verifies that all the settings for a word cloud are met
        Return:
            A dictionary with keys being files corresponding to qualities for this word cloud, and values being
            errors that arose when verifying conditions. If and only if the dictionary is empty is the word cloud
            fully ready for creation
        """
        verification = dict()
        if self.wc_type == "circular" or self.wc_type == "rectangular":
            file_names = ['output_name.txt', 'dimensions.txt', 'colors.txt', 'text.txt', 'num_words_to_include.txt']

        for file in file_names:
            try:
                self._read_in_file_and_check_assertions(file)
            except AssertionError as e:
                verification[file] = e

        return verification

    @staticmethod
    def freq_to_raw(freqs: str, output: str, key: lambda x: 'val', min_occurence: int =1):
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
        shutil.rmtree(WordCloud.WORD_CLOUD_PATH) if os.path.exists(WordCloud.WORD_CLOUD_PATH) else None
        os.makedirs(WordCloud.WORD_CLOUD_PATH, exist_ok=True)
        if os.path.isfile(self.path + 'excludedWords.txt'):
            shutil.copyfile(self.path + 'excludedWords.txt', WordCloud.WORD_CLOUD_PATH + 'excludedWords.txt')
        with open(WordCloud.WORD_CLOUD_PATH + 'type.txt', mode='w', encoding='utf-8') as f:
            f.write(self.wc_type)

    def read_dimensions(self):
        assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'dimensions.txt'), "dimensions.txt does not exist!"
        dimensions = []
        for line in open(WordCloud.WORD_CLOUD_PATH + 'dimensions.txt', mode='r').readlines():
            dimensions += [line]
        assert len(dimensions) == 2, "dimensions.txt has to many lines"
        return dimensions

    def read_colors(self):
        assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'colors.txt'), "colors.txt does not exist!"
        colors = []
        for line in open(WordCloud.WORD_CLOUD_PATH + 'colors.txt', mode='r').readlines():
            colors += [line]
        return colors

    def read_file(self, file_name):
        assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + file_name), "{0} does not exist!".format(file_name)
        with open(WordCloud.WORD_CLOUD_PATH + file_name, mode='r') as f:
            return f.readline()

    ######################################## WRITING TO FILES ########################################

    @staticmethod
    def set_dimensions(x: int, y: int):
        """Saves the specified integer dimensions to a file"""
        WordCloud.assert_dimensions_for_wc([x, y])

        with open(WordCloud.WORD_CLOUD_PATH + 'dimensions.txt', mode='w', encoding='utf-8') as f:
            f.write(str(x) + '\n' + str(y))

    @staticmethod
    def append_color(color: 'tuple or list (length 3) of ints'):
        """Appends the set colors to colors.txt if colors exists otherwise calls set_colors"""
        WordCloud.assert_color_for_wc(color)
        if os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'colors.txt'):
            with open(WordCloud.WORD_CLOUD_PATH + 'colors.txt', mode='a', encoding='utf-8') as f:
                f.write('{0}, {1}, {2}\n'.format(*color))
        else:
            with open(WordCloud.WORD_CLOUD_PATH + 'colors.txt', mode='w', encoding='utf-8') as f:
                f.write('{0}, {1}, {2}\n'.format(*color))

    @staticmethod
    def clear_colors():
        os.remove(WordCloud.WORD_CLOUD_PATH + 'colors.txt')

    @staticmethod
    def set_colors(*colors):
        WordCloud.clear_colors()
        for color in colors:
            WordCloud.append_color(color)

    @staticmethod
    def set_output_name(name: str):
        """Writes the passed name to output_name.txt"""
        WordCloud.assert_output_name_for_wc(name)

        with open(WordCloud.WORD_CLOUD_PATH + 'output_name.txt', mode='w', encoding='utf-8') as f:
            f.write(name)

    @staticmethod
    def set_num_words_to_include(limit: int):
        WordCloud.assert_num_words_to_include(limit)

        with open(WordCloud.WORD_CLOUD_PATH + 'num_words_to_include.txt', mode='w', encoding='utf-8') as f:
            f.write(str(limit))

    @staticmethod
    def set_min_word_length(min_length: int):
        WordCloud.assert_min_word_length(min_length)

        with open(WordCloud.WORD_CLOUD_PATH + 'min_word_length.txt', mode='w', encoding='utf-8') as f:
            f.write(str(min_length))

    ######################################## ASSERTING VALUES ARE VALID ########################################

    def _read_in_file_and_check_assertions(self, file):
        if file not in ['output_name.txt', 'dimensions.txt', 'colors.txt', 'text.txt', 'num_words_to_include.txt',
                        'min_word_length.txt']:
            raise ValueError("Invalid file name: {0}".format(file))

        if file == 'output_name.txt':
            output_name = self.read_file(file)
            self.assert_output_name_for_wc(output_name)
        elif file == 'dimensions.txt':
            dimensions = self.read_dimensions()
            try:
                self.assert_dimensions_for_wc([int(val) for val in dimensions])
            except ValueError as e:
                raise AssertionError(str(e))
        elif file == 'colors.txt':
            colors = self.read_colors()
            for line in colors:
                self.assert_color_string(line)
        elif file == 'text.txt':
            input_name = self.read_file(file)
        elif file == 'num_words_to_include.txt':
            limit = self.read_file(file)
            try:
                limit = int(limit)
            except ValueError:
                raise AssertionError("num_words_to_include.txt has bad form, must have an integer")
            self.assert_num_words_to_include(limit)
        elif file == 'min_word_length.txt':
            min_length = self.read_file(file)
            try:
                min_length = int(min_length)
            except ValueError:
                raise AssertionError("min_word_length.txt has bad form, must have an integer")
            self.assert_num_words_to_include(min_length)

    @staticmethod
    def assert_min_word_length(min_length):
        assert isinstance(min_length, int), "min_length must be an integer"
        assert min_length > 0, "...Why would I let you pick a min length less than 0? Must be greater than or equal to 1"

    @staticmethod
    def assert_num_words_to_include(limit):
        assert isinstance(limit, int), "limit must be an integer"
        assert 0 < limit, "This would be a very boring word cloud if I let you give a frequency less than 1"

    @staticmethod
    def assert_dimensions_for_wc(dimensions: 'list or tuple (length 2) of ints'):
        assert isinstance(dimensions, list) or isinstance(dimensions, tuple), "Dimensions is an invalid type"
        x, y = dimensions
        assert isinstance(x, int), "X needs to be an integer"
        assert isinstance(y, int), "Y needs to be an integer"
        assert 0 < x, "X must be greater than 0"
        assert 0 < y, "Y must be greater than 0"

    @staticmethod
    def assert_color_for_wc(color: 'list or tuple (length 3) of ints'):
        assert (isinstance(color, tuple) or isinstance(color, list)) and all(isinstance(ele, int) for ele in color), \
            "Color must be a tuple (or list) with 3 ints, e.g. (100, 100, 100)"
        assert all(0 <= val <= 255 for val in color), "All rgb values must be between 0 and 255"

    @staticmethod
    def assert_output_name_for_wc(name: str):
        assert isinstance(name, str), "Name should be a string"
        assert '.png' in name, "Name should be a .png file"
        assert ' ' not in name, "File names can't have spaces"

    @staticmethod
    def assert_num_text_set_for_wc(num: int):
        assert isinstance(num, int), "Num must be an integer"
        assert num >= 1, "Num should be greater than 1"

    @staticmethod
    def assert_color_string(color):
        split = color.split(', ')
        assert len(split) == 3, "color is invalid "
        try:
            split = list(map(int, split))
        except ValueError as e:
            raise AssertionError("color should be made of integers separated by commas and spaces, e.g. 0, 255, 255")
        WordCloud.assert_color_for_wc(split)
        return split

    # @staticmethod
    # def set_num_word_sets(num: int):
    #     """Saves the specified integer to a file"""
    #     WordCloud.assert_num_text_set_for_wc(num)
    #
    #     with open(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt', mode='w', encoding='utf-8') as f:
    #         f.write(str(num))
    #
    # @staticmethod
    # def create_text_set(set_num: int, raw_file_name: str, min_frequency: int = 1):
    #     """Creates a text file for the corresponding set_num specified with the raw attributes
    #     Parameters:
    #         set_num: The integer value specifying
    #         raw_file_name: A string representing the path to the file wanted
    #         min_frequency (optional): An integer representing the minimum number of times a word
    #                                 has to have to be counted
    #     """
    #     # ensures that there is a valid number of text sets in the wordCloud directory
    #     assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt'), "You need to specify a number " \
    #                                                                             "of text sets first"
    #     try:
    #         max_text_sets = 3
    #         read_num = open(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt').read()
    #         assert 0 < int(read_num), "The number of texts sets needs to be greater than 0..."
    #         assert int(read_num) <= max_text_sets, "Currently only support a maximum of {0} text sets" \
    #             .format(max_text_sets)
    #     except ValueError:
    #         assert False, "The value read from num_text_sets.txt is not a valid integer, please fix this"
    #
    #     # ensures set_num is valid
    #     assert isinstance(set_num, int), "set_num must be an integer"
    #     assert 0 < set_num < read_num, "set_num must be between 1 and {0}".format(read_num)
    #
    #     # Making sure min_frequency is valid
    #     assert isinstance(min_frequency, int), "min_frequency must be an integer"
    #     assert min_frequency >= 1, "min_frequency must be greater than or equal to 1"
    #
    #     # Making sure the specified raw file exists
    #     assert os.path.isfile(raw_file_name), "The specified file for word frequencies ({0}) does not exist" \
    #         .format(raw_file_name)
    #
    #     excluded_words = []
    #     if os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'excluded.txt'):
    #         for word in open(WordCloud.WORD_CLOUD_PATH + 'excluded.txt', mode='r').readlines():
    #             excluded_words.append(word)
    #     key = lambda x: x not in excluded_words
    #
    #     WordCloud.freq_to_raw(raw_file_name, WordCloud.WORD_CLOUD_PATH + 'word_set{0}.txt'.format(set_num), key,
    #                           min_occurence=min_frequency)


