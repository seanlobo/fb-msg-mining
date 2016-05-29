import functions.emoji_values


#variables
EMOJI_UNICODE = functions.emoji_values.EMOJI_UNICODE
UNICODE_EMOJI = functions.emoji_values.UNICODE_EMOJI
SRC_CODES_TO_CAP_NAME = functions.emoji_values.SRC_CODES_TO_CAP_NAME
NAMES_TO_CODES = functions.emoji_values.NAMES_TO_CODES

def underscores_to_caps(string):
    return string.upper().replace('_', ' ')

def caps_to_underscores(string):
    """Converts a string to lowercase and replaces spaces with underscores"""
    return string.lower().replace(' ', '_')


def emojify(message):
    """Replaces python src codes with their corresponding emoji, if found"""
    if '\\' in repr(message):
        for key in SRC_CODES_TO_CAP_NAME:
            message = message.replace(key, src_to_emoiji(key))
    return message



def src_to_emoiji(code, safe=True):
    """Takes in a python src encoding in UTF8 of an emoji, and returns the emoji
    as a string if it exists in the above dictionary, otherwise the value passed
    as default
    """
    try:
        name = SRC_CODES_TO_CAP_NAME.get(code)
        if '_' not in name:
            name = caps_to_underscores(name)
        return EMOJI_UNICODE[':' + name + ':']
    except (AttributeError, KeyError, TypeError) as e:
        if safe:
            return code
        else:
            raise e



def emoji_to_src(emoji, safe=True):
    """Takes in an emoji as a string and returns the python src encoding string"""
    try:
        emoji = UNICODE_EMOJI[emoji].strip(':')
        return NAMES_TO_CODES[emoji.upper().replace('_', ' ')]
    except (AttributeError, KeyError) as e:
        if safe:
            return emoji
        else:
            raise e
