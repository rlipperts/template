"""
Tests template_loader.loader
"""
import json
import re
from pathlib import Path

import pytest

from template_loader import loader


@pytest.mark.parametrize('placeholder, prefix, suffix',
                         [('test', '${', '}'),
                          ('testy_test testy-test-test', '${', '}'),
                          ('test', '<<', '>>'),
                          ('testy test testy-test-test', '<<', '>>'), ])
def test_pattern_creation(placeholder: str, prefix: str, suffix: str):  #pylint: disable=C0116
    pattern = loader.build_pattern(prefix, suffix)
    text_fragment = ' Lorem ipsum dolor sit amet, consectetur adipiscing ' \
                    'elit, sed do eiusmod tempor incididunt ut labore et ' \
                    'dolore magna aliqua. '
    text_a = (text_fragment + placeholder + text_fragment) * 2
    text_b = text_fragment + placeholder + ' ' + placeholder + text_fragment
    matching = prefix + placeholder + suffix
    text = text_a + matching + text_b + matching + text_b
    result = re.sub(pattern, '', text)
    assert result == text_a + text_b + text_b


@pytest.mark.parametrize('text',
                         ['Lorem ${ipsum} dolor sit amet, consectetur adipiscing',
                          'Lorem ${ipsum} dolor sit amet, consectetur ${adipiscing}',
                          '${Lorem} ipsum dolor sit amet, consectetur ${adipiscing}', ])
def test_func_replacer(text: str):  #pylint: disable=C0116
    replacements = {
        'Lorem': 'Lorem',
        'ipsum': 'ipsum',
        'adipiscing': 'adipiscing',
    }
    clean_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing'
    def replacer(match): return loader.func_replacer(match, False, **replacements)  #pylint: disable=C0321
    assert re.sub(loader.build_pattern('${', '}'), replacer, text) == clean_text


def test_func_replacer_safe_ignores_missing_replacements():  #pylint: disable=C0116
    replacements = {
        'ipsum': 'ipsum',
    }
    text = 'Lorem ${ipsum} dolor sit amet, consectetur ${adipiscing}'
    clean_text = 'Lorem ipsum dolor sit amet, consectetur ${adipiscing}'
    def replacer(match): return loader.func_replacer(match, True, **replacements)  #pylint: disable=C0321
    assert re.sub(loader.build_pattern('${', '}'), replacer, text) == clean_text


def test_func_replacer_unsafe_errors_if_missing_replacements():  #pylint: disable=C0116
    replacements = {
        'ipsum': 'ipsum',
    }
    text = 'Lorem ${ipsum} dolor sit amet, consectetur ${adipiscing}'

    def replacer(match): return loader.func_replacer(match, False, **replacements)  #pylint: disable=C0321
    with pytest.raises(KeyError):
        re.sub(loader.build_pattern('${', '}'), replacer, text)


@pytest.mark.parametrize('file_ending', ['json', 'yaml', 'toml'])
def test_template_load(file_ending):  #pylint: disable=C0116
    result_path = Path.cwd() / 'data/replaced_placeholders.json'
    with open(result_path) as file:
        correct_data = json.load(file)
    template_path = Path.cwd() / ('data/example_template.' + file_ending)
    replacements = {
        'placeholder': 'replacement',
        'float_placeholder': 3.14159,
    }
    check_me = loader.load(template_path, **replacements)
    assert check_me == correct_data