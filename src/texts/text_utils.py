#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script for managing HAMELIN texts
Allows listing, showing and validating texts easily
"""

import sys
import os

# Add the src directory to the path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from texts import text_manager

def list_sections():
    """Lists all available sections."""
    print("📋 Available sections:")
    sections = text_manager.get_all_sections()
    for i, section in enumerate(sections, 1):
        print(f"   {i}. {section}")
    return sections

def list_subsections(section):
    """Lists all subsections of a section."""
    print(f"📄 Subsections in '{section}':")
    subsections = text_manager.get_subsections(section)
    for i, subsection in enumerate(subsections, 1):
        print(f"   {i}. {subsection}")
    return subsections

def show_text(section, subsection, key='content'):
    """Shows the text of a specific subsection."""
    text = text_manager.get_text(section, subsection, key)
    print(f"\n📝 {section}.{subsection}.{key}:")
    print("-" * 50)
    if key == 'content':
        # Show HTML without tags for better readability
        import re
        clean_text = re.sub('<[^<]+?>', '', text)
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        print(clean_text.strip())
    else:
        print(text)
    print("-" * 50)

def validate_html(section, subsection):
    """Validates that a subsection's HTML is basically correct."""
    content = text_manager.get_text(section, subsection, 'content')
    
    # Basic validations
    issues = []
    
    # Check balanced tags
    import re
    tags = re.findall(r'<(/?)(\w+)[^>]*>', content)
    tag_stack = []
    
    for is_closing, tag_name in tags:
        if is_closing:
            if not tag_stack or tag_stack[-1] != tag_name:
                issues.append(f"Unexpected closing tag: </{tag_name}>")
            else:
                tag_stack.pop()
        else:
            # Ignore self-closing tags
            if tag_name not in ['br', 'hr', 'img', 'meta']:
                tag_stack.append(tag_name)
    
    if tag_stack:
        issues.append(f"Unclosed tags: {', '.join(tag_stack)}")
    
    # Check balanced quotes in style
    style_quotes = content.count('style="') * 2
    total_quotes = content.count('"')
    if (total_quotes - style_quotes) % 2 != 0:
        issues.append("Unbalanced quotes")
    
    if issues:
        print(f"❌ Issues found in {section}.{subsection}:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"✅ {section}.{subsection} is correctly formatted")

def main():
    """Main script function."""
    if len(sys.argv) < 2:
        print("🔧 HAMELIN Text Manager")
        print("\nUsage:")
        print("  python text_utils.py list                    # List sections")
        print("  python text_utils.py show <section>          # Show subsections")
        print("  python text_utils.py show <section> <sub>    # Show text")
        print("  python text_utils.py validate                # Validate all texts")
        print("  python text_utils.py validate <section>      # Validate a section")
        print("\nExamples:")
        print("  python text_utils.py list")
        print("  python text_utils.py show clinical_trial")
        print("  python text_utils.py show clinical_trial primary_variable")
        print("  python text_utils.py validate")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_sections()
    
    elif command == "show":
        if len(sys.argv) < 3:
            list_sections()
        elif len(sys.argv) < 4:
            section = sys.argv[2]
            list_subsections(section)
        else:
            section = sys.argv[2]
            subsection = sys.argv[3]
            show_text(section, subsection)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            # Validate all
            print("🔍 Validating all texts...")
            for section in text_manager.get_all_sections():
                for subsection in text_manager.get_subsections(section):
                    validate_html(section, subsection)
        else:
            # Validate specific section
            section = sys.argv[2]
            print(f"🔍 Validating texts from '{section}'...")
            for subsection in text_manager.get_subsections(section):
                validate_html(section, subsection)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python text_utils.py' to see help")

if __name__ == "__main__":
    main()