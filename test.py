#!/usr/bin/env python3
"""
Test Python file for MCP Demo Server
Author: Vipin Ruhal
Description: Python string methods examples and demonstrations
"""


def string_methods_demo():
    """Demonstrate various Python string methods with examples."""
    
    print("=" * 60)
    print("Python String Methods Demo")
    print(f"Created by: Vipin Ruhal")
    print("=" * 60)
    
    # Sample strings for demonstration
    sample_text = "  Hello World! Welcome to Python Programming.  "
    name = "vipin ruhal"
    mixed_case = "PyThOn PrOgRaMmInG"
    
    print("\n1. CASE CONVERSION METHODS")
    print("-" * 30)
    print(f"Original: '{name}'")
    print(f"upper(): '{name.upper()}'")
    print(f"lower(): '{name.lower()}'")
    print(f"title(): '{name.title()}'")
    print(f"capitalize(): '{name.capitalize()}'")
    print(f"swapcase(): '{mixed_case.swapcase()}'")
    
    print("\n2. WHITESPACE METHODS")
    print("-" * 30)
    print(f"Original: '{sample_text}'")
    print(f"strip(): '{sample_text.strip()}'")
    print(f"lstrip(): '{sample_text.lstrip()}'")
    print(f"rstrip(): '{sample_text.rstrip()}'")
    
    print("\n3. SEARCHING METHODS")
    print("-" * 30)
    search_string = "Python is awesome and Python is powerful"
    print(f"String: '{search_string}'")
    print(f"find('Python'): {search_string.find('Python')}")
    print(f"rfind('Python'): {search_string.rfind('Python')}")
    print(f"index('is'): {search_string.index('is')}")
    print(f"count('Python'): {search_string.count('Python')}")
    print(f"startswith('Python'): {search_string.startswith('Python')}")
    print(f"endswith('powerful'): {search_string.endswith('powerful')}")
    
    print("\n4. REPLACEMENT METHODS")
    print("-" * 30)
    replace_text = "Java is great, Java is popular"
    print(f"Original: '{replace_text}'")
    print(f"replace('Java', 'Python'): '{replace_text.replace('Java', 'Python')}'")
    print(f"replace('Java', 'Python', 1): '{replace_text.replace('Java', 'Python', 1)}'")
    
    print("\n5. SPLITTING AND JOINING METHODS")
    print("-" * 30)
    csv_data = "apple,banana,orange,grape"
    sentence = "Python is a programming language"
    print(f"CSV data: '{csv_data}'")
    print(f"split(','): {csv_data.split(',')}")
    print(f"Sentence: '{sentence}'")
    print(f"split(): {sentence.split()}")
    
    fruits = ["apple", "banana", "orange"]
    print(f"List: {fruits}")
    print(f"'-'.join(fruits): '{'-'.join(fruits)}'")
    print(f"' | '.join(fruits): '{' | '.join(fruits)}'")
    
    print("\n6. VALIDATION METHODS")
    print("-" * 30)
    test_strings = ["Hello123", "12345", "HelloWorld", "hello world", "HELLO"]
    for test_str in test_strings:
        print(f"String: '{test_str}'")
        print(f"  isalnum(): {test_str.isalnum()}")
        print(f"  isalpha(): {test_str.isalpha()}")
        print(f"  isdigit(): {test_str.isdigit()}")
        print(f"  islower(): {test_str.islower()}")
        print(f"  isupper(): {test_str.isupper()}")
        print(f"  isspace(): {test_str.isspace()}")
        print()
    
    print("\n7. FORMATTING METHODS")
    print("-" * 30)
    text = "python"
    print(f"Original: '{text}'")
    print(f"center(20, '*'): '{text.center(20, '*')}'")
    print(f"ljust(15, '-'): '{text.ljust(15, '-')}'")
    print(f"rjust(15, '-'): '{text.rjust(15, '-')}'")
    print(f"zfill(10): '{text.zfill(10)}'")
    
    print("\n8. PARTITION METHODS")
    print("-" * 30)
    partition_text = "name@domain.com"
    print(f"Email: '{partition_text}'")
    print(f"partition('@'): {partition_text.partition('@')}")
    print(f"rpartition('.'): {partition_text.rpartition('.')}")
    
    print("\n9. ENCODING/DECODING METHODS")
    print("-" * 30)
    unicode_text = "Vipin Ruhal - Python Developer"
    print(f"Original: '{unicode_text}'")
    encoded = unicode_text.encode('utf-8')
    print(f"encode('utf-8'): {encoded}")
    decoded = encoded.decode('utf-8')
    print(f"decode('utf-8'): '{decoded}'")
    
    print("\n10. STRING FORMATTING EXAMPLES")
    print("-" * 30)
    name = "Vipin Ruhal"
    age = 25
    language = "Python"
    
    # Old style formatting (% formatting)
    old_style = "Hello, my name is %s and I'm %d years old" % (name, age)
    print(f"Old style result: '{old_style}'")
    
    # .format() method
    format_style = "Hello, my name is {} and I love {}".format(name, language)
    print(f"Format method result: '{format_style}'")
    
    # f-strings (formatted string literals)
    f_string_style = f"Hello, my name is {name} and I love {language}"
    print(f"F-string result: '{f_string_style}'")
    
    print("\n" + "=" * 60)
    print("String methods demonstration completed!")
    print("=" * 60)


if __name__ == "__main__":
    string_methods_demo()
