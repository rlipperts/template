from pathlib import Path
from string import Template
import logging
import typing
import json

logger = logging.getLogger(__name__)

def instantiate_from_json(path: Path, **replacements: typing.Union[str, bool]):
    # todo: Aint this bad practice? it is basically impossible to find this default replacement
    replacements['cwd'] = str(Path.cwd())

    # todo: also load other file formats (yml, ..)
    with open(path) as jsonFile:
        data = json.load(jsonFile)
        jsonFile.close()

        # todo: make this actually useful by replacing on multiple levels
        if isinstance(data, str):
            data = Template(data).safe_substitute(replacements)
        elif isinstance(data, list):
            data = [Template(v).safe_substitute(replacements) for v in data]
        elif isinstance(data, dict):
            data = {k: Template(v).safe_substitute(replacements) for k, v in data.items()}
        else:
            raise ValueError("Invalid data type in template file, couldn't load it!")
        return data
