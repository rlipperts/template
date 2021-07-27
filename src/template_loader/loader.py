from pathlib import Path
import logging
import typing
import re

import json
import yaml
import toml

logger = logging.getLogger(__name__)


def load(path: Path, placeholder_marker_left: str = '${', placeholder_marker_right: str = '}',
         safe=True, **replacements: typing.Union[str, bool, int, float]) \
        -> typing.Union[list, dict]:
    with open(path) as template:
        text = template.read()
        template.close()

    if replacements:
        pattern = build_pattern(placeholder_marker_left, placeholder_marker_right)
        def replacer(match): return func_replacer(match, safe, **replacements)
        text = re.sub(pattern, replacer, text)

    if path.suffix == '.json':
        data = json.loads(text)
    elif path.suffix == '.yaml':
        data = yaml.safe_load(text)
    elif path.suffix == '.toml':
        data = toml.loads(text)
    else:
        raise NotImplementedError('Cannot handle templates of Type %s' % path.suffix)
    return data


def build_pattern(placeholder_marker_left: str, placeholder_marker_right: str) -> re.Pattern[str]:
    left = re.escape(placeholder_marker_left)
    right = re.escape(placeholder_marker_right)
    # regex matches everything between left and right marker, optionally in between quotes
    # group 'prefix_quote': optional leading quote
    # group 'placeholder': everythin in between left and right marker (smallest possible match only)
    # group 'prefix_quote': optional leading quote
    # see https://regex101.com/r/zEwq7N/1
    return re.compile(r'(?P<prefix_quote>"?)' + left + r'(?P<placeholder>.+?)' +
                      right + r'(?P<suffix_quote>"?)')


def func_replacer(match: re.Match, safe: bool,
                  **replacements: typing.Union[str, bool, int, float]) -> str:
    prefix_quote = match.group('prefix_quote')
    placeholder = match.group('placeholder')
    suffix_quote = match.group('suffix_quote')
    try:
        # replace correctly so strings are not broken but non-strings are not converted to strings
        if prefix_quote and not suffix_quote:
            return prefix_quote + str(replacements[placeholder])
        elif suffix_quote and not prefix_quote:
            return str(replacements[placeholder]) + suffix_quote
        elif prefix_quote and suffix_quote:
            if not isinstance(replacements[placeholder], str):
                return str(replacements[placeholder])
            else:
                return prefix_quote + str(replacements[placeholder]) + suffix_quote
        else:
            return str(replacements[placeholder])
    except KeyError:
        if safe:
            return match.group(0)
        else:
            raise KeyError(f'Missing replacement for placeholder {placeholder}!')
