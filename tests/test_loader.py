# pylint: disable=missing-function-docstring,protected-access
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
def test_pattern_creation(placeholder: str, prefix: str, suffix: str):
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
def test_func_replacer(text: str):
    replacements = {
        'Lorem': 'Lorem',
        'ipsum': 'ipsum',
        'adipiscing': 'adipiscing',
    }
    clean_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing'
    # pylint: disable=C0321
    def replacer(match): return loader.func_replacer(match, False, **replacements)
    assert re.sub(loader.build_pattern('${', '}'), replacer, text) == clean_text


def test_func_replacer_safe_ignores_missing_replacements():
    replacements = {
        'ipsum': 'ipsum',
    }
    text = 'Lorem ${ipsum} dolor sit amet, consectetur ${adipiscing}'
    clean_text = 'Lorem ipsum dolor sit amet, consectetur ${adipiscing}'
    # pylint: disable=C0321
    def replacer(match): return loader.func_replacer(match, True, **replacements)
    assert re.sub(loader.build_pattern('${', '}'), replacer, text) == clean_text


def test_func_replacer_unsafe_errors_if_missing_replacements():
    replacements = {
        'ipsum': 'ipsum',
    }
    text = 'Lorem ${ipsum} dolor sit amet, consectetur ${adipiscing}'
    # pylint: disable=C0321
    def replacer(match): return loader.func_replacer(match, False, **replacements)
    with pytest.raises(KeyError):
        re.sub(loader.build_pattern('${', '}'), replacer, text)


@pytest.mark.parametrize('file_ending', ['json', 'yaml', 'toml'])
def test_template_load(file_ending):
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


def test_dict_only_load_returns_same_dict_as_normal_load():
    template_path = Path.cwd() / 'data/example_template.json'
    assert loader.load_dict(template_path) == loader.load(template_path)


def test_dict_only_load_errors_on_list_json():
    template_path = Path.cwd() / 'data/list_template.json'
    with pytest.raises(TypeError):
        loader.load_dict(template_path)


def test_list_only_load_returns_same_list_as_normal_load():
    template_path = Path.cwd() / 'data/list_template.json'
    assert loader.load_list(template_path) == loader.load(template_path)


def test_list_only_load_errors_on_dict_json():
    template_path = Path.cwd() / 'data/example_template.json'
    with pytest.raises(TypeError):
        loader.load_list(template_path)


def test_list_only_load_errors_on_toml():
    template_path = Path.cwd() / 'data/invalid_template.toml'
    with pytest.raises(NotImplementedError):
        loader.load_list(template_path)
