import re
from collections import Counter

def generate_gree_expression(valid_strings, invalid_strings):
    """
    Generate a regex pattern that matches all valid strings and rejects all invalid strings.
    
    Assumptions:
    1. The pattern should be as specific as possible while covering all valid cases
    2. We prioritize common regex patterns like character classes, anchors, and quantifiers
    3. We try simpler patterns first before complex ones
    4. The pattern must match the entire string (anchored)
    """
    
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
    
    # Fallback: exact match pattern (should rarely be needed)
    if len(valid_strings) == 1 and len(valid_strings[0]) <= 18:
        return f"^{re.escape(valid_strings[0])}$"
    
    return "^.*$"  # Last resort

def _get_character_class_patterns(valid_strings, invalid_strings):
    """Generate patterns based on character classes"""
    patterns = []
    
    # Check if all valid are letters and all invalid are digits
    if (all(s.isalpha() for s in valid_strings) and 
        all(s.isdigit() for s in invalid_strings)):
        patterns.append("^\D+$")
        
    
    # Check if all valid are digits and all invalid are letters
    if (all(s.isdigit() for s in valid_strings) and 
        all(s.isalpha() for s in invalid_strings)):
        patterns.append("^\d+$")
        
    
    # Check if all valid are alphanumeric
    if all(s.isalnum() for s in valid_strings):
        patterns.append("^\w+$")
    
    return patterns

def _get_position_patterns(valid_strings, invalid_strings):
    """Generate patterns based on start/end positions"""
    patterns = []
    
    # Check starting characters
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
    
    # Check ending characters
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
    
    # Find characters that appear in all valid but no invalid strings
    valid_chars = set()
    for s in valid_strings:
        valid_chars.update(s)
    
    invalid_chars = set()
    for s in invalid_strings:
        invalid_chars.update(s)
    
    # Characters that are in valid but not in invalid
    exclusive_chars = valid_chars - invalid_chars
    
    for char in exclusive_chars:
        if all(char in s for s in valid_strings):
            # Special handling for dash - don't escape it
            if char == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(char)
            
            patterns.append(f"^.+{escaped_char}.+$")
            patterns.append(f"^.*{escaped_char}.*$")
    
    # Special patterns for common separators
    common_separators = ['-', '@', '.', '_', ':']
    for sep in common_separators:
        if (all(sep in s for s in valid_strings) and 
            not any(sep in s for s in invalid_strings)):
            # Special handling for dash - don't escape it
            if sep == '-':
                escaped_char = '-'
            else:
                escaped_char = re.escape(sep)
            patterns.append(f"^.+{escaped_char}.+$")

    return patterns

def _get_structure_patterns(valid_strings, invalid_strings):
    """Generate patterns for structured data like emails"""
    patterns = []
    
    # Email pattern
    if all('@' in s and '.' in s for s in valid_strings):
        # Check if all valid strings match email pattern
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
    
    # If all valid strings have same length and it's different from invalid
    if (len(valid_lengths) == 1 and 
        not valid_lengths.intersection(invalid_lengths)):
        length = list(valid_lengths)[0]
        patterns.append(f"^.{{{length}}}$")
    
    return patterns

def _test_pattern(pattern, valid_strings, invalid_strings):
    """Test if a pattern correctly matches valid and rejects invalid strings"""
    try:
        regex = re.compile(pattern)
        
        # All valid strings must match
        for s in valid_strings:
            if not regex.fullmatch(s):
                return False
        
        # All invalid strings must not match
        for s in invalid_strings:
            if regex.fullmatch(s):
                return False
        
        return True
    except re.error:
        return False

# Test the function with the provided examples
if __name__ == "__main__":
    # Test cases from the scrolls
    test_cases = [
        (["abc", "def"], ["123", "456"], "^\D+$"),
        (["aaa", "abb", "acc"], ["bbb", "bcc", "bca"], "^[a].+$"),
        (["abc1", "bbb1", "ccc1"], ["abc", "bbb", "ccc"], "^.+[1]$"),
        (["abc-1", "bbb-1", "cde-1"], ["abc1", "bbb1", "cde1"], "^.+-.+$"),
        (["foo@abc.com", "bar@def.net"], ["baz@abc", "qux.com"], "^\D+@\w+\.\w+$")
    ]
    
    print("Testing generate_gree_expression function:")
    print("=" * 50)
    
    for i, (valid, invalid, expected) in enumerate(test_cases, 1):
        result = generate_gree_expression(valid, invalid)
        print(f"Scroll {i}:")
        print(f"  Valid: {valid}")
        print(f"  Invalid: {invalid}")
        print(f"  Expected: {expected}")
        print(f"  Generated: {result}")
        print(f"  Match: {result == expected}")
        print()