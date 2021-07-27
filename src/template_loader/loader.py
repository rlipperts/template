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
    return re.compile(r'(' + left + r')(.+)(' + right + r')')


def func_replacer(match: re.Match, safe: bool,
                  **replacements: typing.Union[str, bool, int, float]) -> str:
    placeholder = match.group(2)
    try:
        return str(replacements[placeholder])
    except KeyError:
        if safe:
            return str(match)
        else:
            raise KeyError(f'Missing replacement for placeholder {placeholder}!')
