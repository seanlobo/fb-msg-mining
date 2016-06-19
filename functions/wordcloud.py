import os
import shutil


class WordCloud:
    WORD_CLOUD_PATH = 'data/wordClouds/'
    WORD_CLOUD_TYPES = ['circular', 'rectangular']

    def __init__(self, wc_type, path):
        self.wc_type = wc_type
        self.path = path

    def verify_word_cloud_setup(self):
        """Verifies that all the settings for a word cloud are met
        Return:
            A dictionary with keys being files corresponding to qualities for this word cloud, and values being
            errors that arose when verifying conditions. If and only if the dictionary is empty is the word cloud
            fully ready for creation
        """
        verification = dict()
        if self.wc_type == "circular":
            assertions = [WordCloud.assert_dimensions_for_wc, WordCloud.assert_output_name_for_wc,
                          WordCloud.assert_color_for_wc, lambda x: None]
            file_names = ['dimensions.txt', 'output_name.txt', 'colors.txt', 'text.txt']
            fn = lambda num: assertions[num]
            for i in range(len(assertions)):
                try:
                    assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + file_names[i]), \
                        "{0} is missing".format(file_names[i])
                    with open(WordCloud.WORD_CLOUD_PATH + file_names[i], mode='r') as f:
                        if i == 0:  # dimension
                            val = [int(ele) for ele in f.read().split('\n')]
                        elif i == 1:  # output name
                            val = f.read()
                        elif i == 2:  # colors
                            val = [[int(col) for col in line.split(', ')] for line in f]
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
    def freq_to_raw(freqs, output, key, min_occurence=1):
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

    @staticmethod
    def set_dimensions(x, y):
        """Saves the specified integer dimensions to a file"""
        WordCloud.assert_dimensions_for_wc([x, y])

        with open(WordCloud.WORD_CLOUD_PATH + 'dimensions.txt', mode='w', encoding='utf-8') as f:
            f.write(str(x) + '\n' + str(y))

    @staticmethod
    def set_num_word_sets(num):
        """Saves the specified integer to a file"""
        WordCloud.assert_num_text_set_for_wc(num)

        with open(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt', mode='w', encoding='utf-8') as f:
            f.write(str(num))

    @staticmethod
    def create_text_set(set_num, raw_file_name, min_frequency=1):
        """Creates a text file for the corresponding set_num specified with the raw attributes
        Parameters:
            set_num: The integer value specifying 
        """
        # ensures that there is a valid number of text sets in the wordCloud directory
        assert os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt'), "You need to specify a number " \
                                                                                "of text sets first"
        try:
            max_text_sets = 3
            read_num = open(WordCloud.WORD_CLOUD_PATH + 'num_text_sets.txt').read()
            assert 0 < int(read_num), "The number of texts sets needs to be greater than 0..."
            assert int(read_num) <= max_text_sets, "Currently only support a maximum of {0} text sets"\
                .format(max_text_sets)
        except ValueError:
            assert False, "The value read from num_text_sets.txt is not a valid integer, please fix this"

        # ensures set_num is valid
        assert isinstance(set_num, int), "set_num must be an integer"
        assert 0 < set_num < read_num, "set_num must be between 1 and {0}".format(read_num)

        # Making sure min_frequency is valid
        assert isinstance(min_frequency, int), "min_frequency must be an integer"
        assert min_frequency >= 1, "min_frequency must be greater than or equal to 1"

        # Making sure the specified raw file exists
        assert os.path.isfile(raw_file_name), "The specified file for word frequencies ({0}) does not exist"\
            .format(raw_file_name)

        excluded_words = []
        if os.path.isfile(WordCloud.WORD_CLOUD_PATH + 'excluded.txt'):
            for word in open(WordCloud.WORD_CLOUD_PATH + 'excluded.txt', mode='r').readlines():
                excluded_words.append(word)
        key = lambda x: x not in excluded_words

        WordCloud.freq_to_raw(raw_file_name, WordCloud.WORD_CLOUD_PATH + 'word_set{0}.txt'.format(set_num), key,
                              min_occurence=min_frequency)

    @staticmethod
    def append_color(color):
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
    def set_output_name(name):
        """Writes the passed name to output_name.txt"""
        WordCloud.assert_output_name_for_wc(name)

        with open(WordCloud.WORD_CLOUD_PATH + 'output_name.txt', mode='w', encoding='utf-8') as f:
            f.write(name)

    @staticmethod
    def set_num_words_to_include(limit):
        WordCloud.assert_num_words_to_include(limit)

        with open(WordCloud.WORD_CLOUD_PATH + 'set_num_words_to_include.txt', mode='w', encoding='utf-8') as f:
            f.write(str(limit))

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
    def assert_color_for_wc(color):
        assert (isinstance(color, tuple) or isinstance(color, list)) and all(isinstance(ele, int) for ele in color), \
            "Color must be a tuple (or list) with 3 ints, e.g. (100, 100, 100)"
        assert all(0 <= val <= 255 for val in color), "All rgb values must be between 0 and 255"

    @staticmethod
    def assert_output_name_for_wc(name):
        assert isinstance(name, str), "Name should be a string"
        assert '.png' in name, "Name should be a .png file"
        assert ' ' not in name, "File names can't have spaces"

    @staticmethod
    def assert_num_text_set_for_wc(num):
        assert isinstance(num, int), "Num must be an integer"
        assert num >= 1, "Num should be greater than 1"
