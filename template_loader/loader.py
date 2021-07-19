from pathlib import Path
import logging
import typing
import re

import json
import yaml
import toml

logger = logging.getLogger(__name__)

def load(path: Path, placeholder_marker_left='${', placeholder_marker_right='}',
         safe=True, **replacements: typing.Union[str, bool, int, float]):
    with open(path) as template:
        text = template.read()
        template.close()

    if replacements:
        left = re.escape(placeholder_marker_left)
        right = re.escape(placeholder_marker_right)
        # replace all placeholders in the string so we do not need to traverse the resulting datastructures

    if path.suffix == '.json':
        data = json.loads(text)
    elif path.suffix == '.yaml':
        data = yaml.safe_load(text)
    elif path.suffix == '.toml':
        data = toml.loads(text)
    else:
        raise NotImplementedError('Cannot handle templates of Type %s' % path.suffix)
