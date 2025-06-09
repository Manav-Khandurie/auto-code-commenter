import re

def is_palindrome(s):
    """Check if a string is a palindrome.
    
    A palindrome is a word, phrase, number, or other sequence of characters
    which reads the same backward as forward (ignoring spaces, punctuation,
    and capitalization).
    
    Args:
        s (str): The input string to check.
        
    Returns:
        bool: True if the string is a palindrome, False otherwise.
    """
    cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', s).lower()  # Remove non-alphanumeric chars and lowercase
    return cleaned_string == cleaned_string[::-1]  # Compare string with its reverse