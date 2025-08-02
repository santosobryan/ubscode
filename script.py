import re

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
        return '^$'
    # Basic character class patterns
    patterns.extend([
        r'^\d+$',    
        r'^\D+$',      
        r'^\w+$',     
        r'^[a-zA-Z]+$', 
        r'^[a-z]+$',   
        r'^[A-Z]+$',   
    ])
    # Character-specific patterns based on valid strings
    all_chars = set(''.join(valid_strings))
    for char in all_chars:
        if char.isalnum() or char in '.-_@':
            patterns.append(f'^[{re.escape(char)}].+$') 
            patterns.append(f'^.+[{re.escape(char)}]$')  
    # Structural patterns
    patterns.extend([
        r'^.+-.+$',        
        r'^.+\..+$',      
        r'^.+@.+$',        
        r'^.+@.+\..+$',    
    ])
    # Email-specific patterns
    patterns.extend([
        r'^\w+@\w+\.\w+$',
        r'^\D+@\w+\.\w+$',
        r'^[a-zA-Z]+@[a-zA-Z]+\.[a-zA-Z]+$',
    ])
    # Length-based patterns
    if valid_strings:
        min_len = min(len(s) for s in valid_strings)
        max_len = max(len(s) for s in valid_strings)
        if min_len == max_len:
            patterns.append(f'^.{{{min_len}}}$') 
        else:
            patterns.append(f'^.{{{min_len},{max_len}}}$') 
    for pattern in patterns:
        try:
            compiled_pattern = re.compile(pattern)
            valid_match = True
            for valid_str in valid_strings:
                if not compiled_pattern.fullmatch(valid_str):
                    valid_match = False
                    break
            if not valid_match:
                continue
            invalid_match = False
            for invalid_str in invalid_strings:
                if compiled_pattern.fullmatch(invalid_str):
                    invalid_match = True
                    break
            if not invalid_match:
                return pattern 
                
        except re.error:
            continue 
    fallback_patterns = [
        r'^.*$',
        r'^.+$',
    ]
    
    for pattern in fallback_patterns:
        try:
            compiled_pattern = re.compile(pattern)
            valid_match = True
            for valid_str in valid_strings:
                if not compiled_pattern.fullmatch(valid_str):
                    valid_match = False
                    break
            
            if not valid_match:
                continue
            invalid_match = False
            for invalid_str in invalid_strings:
                if compiled_pattern.fullmatch(invalid_str):
                    invalid_match = True
                    break
            
            if not invalid_match:
                return pattern
                
        except re.error:
            continue
    return '^.*$'

# Sample test cases:

# print(generate_gree_expression(["abc","def"],["123", "456"]))
# print(generate_gree_expression(["aaa", "abb", "acc"],["bbb", "bcc", "bca"],))        
# print(generate_gree_expression(["abc1", "bbb1", "ccc1"], ["abc", "bbb", "ccc"],))
# print(generate_gree_expression(["abc-1", "bbb-1", "cde-1"],["abc1", "bbb1", "cde1"],))
# print(generate_gree_expression(["foo@abc.com", "bar@def.net"],["baz@abc", "qux.com"]))
