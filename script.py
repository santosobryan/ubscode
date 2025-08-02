import re
from collections import Counter

def generate_gree_expression(valid_strings, invalid_strings):
    if not valid_strings:
        return "^$"
    
    # Try various pattern strategies
    patterns_to_try = []
    
    # Strategy 1: Character class patterns
    patterns_to_try.extend(_get_character_class_patterns(valid_strings, invalid_strings))
    
    # Strategy 2: Position-based patterns (start/end)
    patterns_to_try.extend(_get_position_patterns(valid_strings, invalid_strings))
    
    # Try structure patterns before content patterns
    patterns_to_try.extend(_get_structure_patterns(valid_strings, invalid_strings))
    patterns_to_try.extend(_get_content_patterns(valid_strings, invalid_strings))
    
    # Strategy 5: Length patterns
    patterns_to_try.extend(_get_length_patterns(valid_strings, invalid_strings))
    
    # Test each pattern
    for pattern in patterns_to_try:
        if len(pattern) <= 20 and _test_pattern(pattern, valid_strings, invalid_strings):
            return pattern
    if len(valid_strings) == 1 and len(valid_strings[0]) <= 18:
        return f"^{re.escape(valid_strings[0])}$"
    
    return "^.*$" 

def _get_character_class_patterns(valid_strings, invalid_strings):
    """Generate patterns based on character classes"""
    patterns = []

    if (all(s.isalpha() for s in valid_strings) and all(s.isdigit() for s in invalid_strings)):
        patterns.append("^\D+$")
        
    if (all(s.isdigit() for s in valid_strings) and all(s.isalpha() for s in invalid_strings)):
        patterns.append("^\d+$")
        
    if all(s.isalnum() for s in valid_strings): 
        patterns.append("^\w+$")
    
    return patterns

def _get_position_patterns(valid_strings, invalid_strings):
    """Generate patterns based on start/end positions"""
    patterns = []
    start_chars = set(s[0] for s in valid_strings if s)
    if len(start_chars) == 1:
        start_char = list(start_chars)[0]
        if not any(s.startswith(start_char) for s in invalid_strings):
            if start_char == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(start_char)
            patterns.append(f"^[{escaped_char}].+$")
            patterns.append(f"^{escaped_char}.*$")

    end_chars = set(s[-1] for s in valid_strings if s)
    if len(end_chars) == 1:
        end_char = list(end_chars)[0]
        if not any(s.endswith(end_char) for s in invalid_strings):
            if end_char == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(end_char)
            patterns.append(f"^.+[{escaped_char}]$")
            patterns.append(f"^.*{escaped_char}$")
    
    return patterns

def _get_content_patterns(valid_strings, invalid_strings):
    """Generate patterns based on content presence/absence"""
    patterns = []
    valid_chars = set()
    for s in valid_strings:
        valid_chars.update(s)
    
    invalid_chars = set()
    for s in invalid_strings:
        invalid_chars.update(s)
    exclusive_chars = valid_chars - invalid_chars
    
    for char in exclusive_chars:
        if all(char in s for s in valid_strings):
            if char == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(char)
            
            patterns.append(f"^.+{escaped_char}.+$")
            patterns.append(f"^.*{escaped_char}.*$")

    common_separators = ['-', '@', '.', '_', ':']
    for sep in common_separators:
        if (all(sep in s for s in valid_strings) and 
            not any(sep in s for s in invalid_strings)):
            if sep == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(sep)
            patterns.append(f"^.+{escaped_char}.+$")

    return patterns

def _get_structure_patterns(valid_strings, invalid_strings):
    """Generate patterns for structured data like emails"""
    patterns = []
    if all('@' in s and '.' in s for s in valid_strings):
        email_pattern = r"^\D+@\w+\.\w+$"
        if _test_pattern(email_pattern, valid_strings, invalid_strings):
            patterns.append(email_pattern)  
        
        patterns.append(r"^[^@]+@[^@]+\.[^@]+$")
        patterns.append(r"^\w+@\w+\.\w+$")
    
    return patterns

def _get_length_patterns(valid_strings, invalid_strings):
    """Generate patterns based on string length"""
    patterns = []
    
    valid_lengths = set(len(s) for s in valid_strings)
    invalid_lengths = set(len(s) for s in invalid_strings)
    if (len(valid_lengths) == 1 and 
        not valid_lengths.intersection(invalid_lengths)):
        length = list(valid_lengths)[0]
        patterns.append(f"^.{{{length}}}$")
    
    return patterns

def _test_pattern(pattern, valid_strings, invalid_strings):
    """Test if a pattern correctly matches valid and rejects invalid strings"""
    try:
        regex = re.compile(pattern)
        for s in valid_strings:
            if not regex.fullmatch(s):
                return False
        for s in invalid_strings:
            if regex.fullmatch(s):
                return False
        
        return True
    except re.error:
        return False

if __name__ == "__main__":
    test_cases = [
        (["abc", "def"], ["123", "456"], "^\D+$"),
        (["aaa", "abb", "acc"], ["bbb", "bcc", "bca"], "^[a].+$"),
        (["abc1", "bbb1", "ccc1"], ["abc", "bbb", "ccc"], "^.+[1]$"),
        (["abc-1", "bbb-1", "cde-1"], ["abc1", "bbb1", "cde1"], "^.+-.+$"),
        (["foo@abc.com", "bar@def.net"], ["baz@abc", "qux.com"], "^\D+@\w+\.\w+$")
    ]
    
    for i, (valid, invalid, expected) in enumerate(test_cases, 1):
        result = generate_gree_expression(valid, invalid)
        print(f"Scroll {i}:")
        print(f"  Valid: {valid}")
        print(f"  Invalid: {invalid}")
        print(f"  Expected: {expected}")
        print(f"  Generated: {result}")
        print(f"  Match: {result == expected}")
        print()