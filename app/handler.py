def normalize_input(input_str):
    """
    Normalize input string to lowercase to simplify comparison.
    """
    return input_str.strip().lower()

def get_meeting_type(input_str):
    """
    Returns the normalized meeting type based on common variations or misspellings.
    """
    normalized_input = normalize_input(input_str)
    if normalized_input in ['mmm', 'mm', 'm3']:
        return 'MMM'
    elif normalized_input in ['client meet', 'cm', 'client', 'cmeet', 'client call', 'cc', 'call', 'ccall']:
        return 'Client Call'
    else:
        return None
    
def get_chat_type(input_str):
    """
    Returns the normalized type based on user selection.
    """
    normalized_input = normalize_input(input_str)
    if normalized_input in ['voice', 'vc', 'voic', 'voi', 'v', 'voicee', 'voce']:
        return 'voice'
    elif normalized_input in ['text', 'tet', 'txt', 't', 'textt', 'tex', 'ext', 'teext']:
        return 'text'
    else:
        return 'text'

def is_affirmative(input_str):
    """
    Checks if the input string is an affirmative response based on common variations.
    """
    normalized_input = normalize_input(input_str)
    affirmative_responses = ['yes', 'y', 'yeah', 'ya', 'yep', 'sure', 'absolutely', 'of course', 'ok', 'okay']
    return normalized_input in affirmative_responses

def is_negative(input_str):
    """
    Checks if the input string is a negative response based on common variations.
    """
    normalized_input = normalize_input(input_str)
    negative_responses = ['no', 'n', 'nope', 'nah', 'not', 'never']
    return normalized_input in negative_responses

def is_exit_command(input_str):
    """
    Determines if the input string is an exit command, considering common typos.
    """
    normalized_input = input_str.strip().lower()
    exit_variations = ['exit', 'exut', 'exi', 'exot', 'quit', 'close', 'bye', 'tada']
    return normalized_input in exit_variations or normalized_input.startswith('ex')

def get_action(input_str):
    """
    Returns the normalized action based on common variations or misspellings.
    """
    normalized_input = normalize_input(input_str)
    # Define variations for each action
    log_variations = ['log', 'logg', 'lg', 'log meeting', 'l']
    seek_variations = ['seek', 'seak', 'sik', 'advice', 'ask']
    exit_variations = ['exit', 'exut', 'exi', 'exot', 'quit', 'close', 'bye', 'tada']
    add_variations = ['add', 'ad', 'a', 'add more', 'continue', 'more', 'again']
    surf_variable = ['surf', 'web', 'surf web', 'surfing', 'surfing web']
    
    if normalized_input in log_variations:
        return 'log'
    elif normalized_input in seek_variations:
        return 'seek'
    elif normalized_input in exit_variations:
        return 'exit'
    elif normalized_input in add_variations:
        return 'add'
    elif normalized_input in surf_variable:
        return 'surf'
    else:
        return None
