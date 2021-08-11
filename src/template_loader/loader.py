"""
Implements the template loading functionality.
Loads template files and replaces all placeholders.
"""
from pathlib import Path
import logging
import typing
import re

import json
import yaml  # type: ignore
import toml  # type: ignore

LOGGER = logging.getLogger(__name__)


class BadFormatError(json.JSONDecodeError, yaml.YAMLError, toml.TomlDecodeError):
    """
    Common error class for decoding errors of the supported file types.
    """


def load_dict(path: Path, placeholder_marker_left: str = '${', placeholder_marker_right: str = '}',
              safe=True, **replacements: typing.Union[str, bool, int, float]) -> dict:
    """
    Loads a template file from multiple possible formats while replacing placeholders.
    :param path: Path to the template file
    :param placeholder_marker_left: Left char/string that indicates a beginning placeholder
    :param placeholder_marker_right: Right char/string that indicates an ending placeholder
    :param safe: If True, placeholders that have no fitting replacement are ignored,
    else an error is raised
    :param replacements: Replacement of placeholders specified as keyword-args
    :return: Python dict-representation of the loaded template.
    """
    data = load(path, placeholder_marker_left, placeholder_marker_right, safe, **replacements)
    if isinstance(data, list):
        LOGGER.error('Expected to find a dictionary-style formatted file!')
        raise TypeError
    return data


def load(path: Path, placeholder_marker_left: str = '${', placeholder_marker_right: str = '}',
         safe=True, **replacements: typing.Union[str, bool, int, float]) \
        -> typing.Union[list, dict]:
    """
    Loads a template file from multiple possible formats while replacing placeholders.
    :param path: Path to the template file
    :param placeholder_marker_left: Left char/string that indicates a beginning placeholder
    :param placeholder_marker_right: Right char/string that indicates an ending placeholder
    :param safe: If True, placeholders that have no fitting replacement are ignored,
    else an error is raised
    :param replacements: Replacement of placeholders specified as keyword-args
    :return: Python representation of the loaded template.
    """
    try:
        with open(path) as template:
            text = template.read()
            template.close()
    except OSError as error:
        LOGGER.error('Could not read from file %s', path)
        LOGGER.error(
            'Make sure the file exists and you have the appropriate rights to read from it')
        raise error

    if replacements:
        # pylint: disable=C0321
        def replacer(match): return func_replacer(match, safe, **replacements)

        pattern = build_pattern(placeholder_marker_left, placeholder_marker_right)
        text = re.sub(pattern, replacer, text)

    try:
        if path.suffix == '.json':
            data = json.loads(text)
        elif path.suffix == '.yaml':
            data = yaml.safe_load(text)
        elif path.suffix == '.toml':
            data = toml.loads(text)
        else:
            raise NotImplementedError('Cannot handle templates of Type %s' % path.suffix)
        return data
    except (json.JSONDecodeError, yaml.YAMLError, toml.TomlDecodeError) as error:
        LOGGER.error('Could not decode file %s', path)
        LOGGER.error('Make sure it is formatted accordingly to the %s standard', path.suffix[1:])
        raise BadFormatError from error


def build_pattern(placeholder_marker_left: str, placeholder_marker_right: str) -> re.Pattern[str]:
    """
    Creates the pattern used to match the placeholders.
    :param placeholder_marker_left: Marks the beginning of placeholders - internally
    is escaped with re.escape
    :param placeholder_marker_right: Marks the ending of placeholders - internally
    is escaped with re.escape
    :return: Created pattern, that matches the placeholders as specified and optionally
    surrounding quotes with the following groups:
        # group 'prefix_quote': optional leading quote
        # group 'placeholder': everything in between left and right marker (smallest possible
        match only)
        # group 'prefix_quote': optional leading quote
    """
    left_marker = re.escape(placeholder_marker_left)
    right_marker = re.escape(placeholder_marker_right)
    prefix_quote = r'(?P<prefix_quote>"?)'
    suffix_quote = r'(?P<suffix_quote>"?)'
    placeholder = r'(?P<placeholder>.+?)'
    # regex matches everything between left and right marker, optionally in between quotes
    # see https://regex101.com/r/zEwq7N/1
    return re.compile(prefix_quote + left_marker + placeholder + right_marker + suffix_quote)


def func_replacer(match: re.Match, safe: bool,
                  **replacements: typing.Union[str, bool, int, float]) -> str:
    """
    Replaces given match with desired replacement. Preserves format of placeholders inside longer
    strings while transforming placeholders to replacement format when possible.
    :param match: Match in which the placeholder is to be replaced
    :param safe: If true, missing replacements for existing placeholders are ignored,
    if not raises a KeyError
    :param replacements: Keyword-style replacements in the format <placeholder='replacement'>
    :return: Text with performed replacement
    """
    prefix_quote = match.group('prefix_quote')
    placeholder = match.group('placeholder')
    suffix_quote = match.group('suffix_quote')
    try:
        # replace correctly so strings are not broken but non-strings are not converted to strings
        if prefix_quote and not suffix_quote:
            return prefix_quote + str(replacements[placeholder])
        if suffix_quote and not prefix_quote:
            return str(replacements[placeholder]) + suffix_quote
        if prefix_quote and suffix_quote:
            if not isinstance(replacements[placeholder], str):
                return str(replacements[placeholder])
            return prefix_quote + str(replacements[placeholder]) + suffix_quote
        return str(replacements[placeholder])
    except KeyError as error:
        if safe:
            return match.group(0)
        raise KeyError(f'Missing replacement for placeholder {placeholder}!') from error
