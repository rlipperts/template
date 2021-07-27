# template loader
Template loader that loads common formats and replaces placeholders

## installation

For installation with pip directly from this GitHub repository simply open a terminal and type
```
pip install git+ssh://git@github.com/rlipperts/template.git
```
There are no PyPI releases. Neither are they planned.

## usage

Import the package
```python
from template_loader import loader
```

Load json template files
```python
template_path = Path.cwd() / ('data/example_template.json')
check_me = loader.load(template_path, placeholder='replacement', something_else=3.14159, 
                       some_bool=True)
```

Load yaml template files
```python
template_path = Path.cwd() / ('data/example_template.yaml')
check_me = loader.load(template_path, placeholder='replacement', something_else=3.14159, 
                       some_bool=True)
```

Load toml template files
```python
template_path = Path.cwd() / ('data/example_template.toml')
check_me = loader.load(template_path, placeholder='replacement', something_else=3.14159, 
                       some_bool=True)
```

Pass replacements from dictionaries.

The optional `safe` parameter (default is `True`) makes the loader raise an KeyError, if there are 
any placeholders for which no replacements exist.
```python
replacements = {
    'Lorem': 'Lorem',
    'ipsum': 'ipsum',
    'adipiscing': 'adipiscing',
}
template_path = Path.cwd() / ('data/example_template.toml')
check_me = loader.load(template_path, safe=False, **replacements)
```

### non-string replacements

Replacement types are preserved, if possible:

* Loading `key="${int}"` with `int=123` from a json file will replace the placeholder like 
  this `key=123` before loading the json data into a python data structure.

* Loading `key="some text ${int}"` with `int=123` from a json file will replace the placeholder 
  like this `key="some text 123"` before loading the json data into a python data structure.
  
### full example

Code:

```python
import json
from pathlib import Path
from template_loader import loader

template_path = Path.cwd() / ('data/example_template.json')
replacements = {
    'placeholder': 'replacement',
    'float_placeholder': 3.14159,
}
loaded_json_data = loader.load(template_path, **replacements)

output_folder = Path.cwd() / 'out'
output_folder.mkdir(exist_ok=True)
output_path = output_folder / 'some_output.json'
with open(output_path, 'w') as file:
    json.dump(loaded_json_data, file)
```

Input json `data/example_template.json`:

```json
{
  "test": {
    "testA": ["testy", "testtest", "test ${placeholder}"],
    "testB": 125,
    "testC": {
      "testD": {
        "test": "${float_placeholder}"
      }
    }
  },
  "testB": true,
  "testC": 1.2345,
  "${placeholder}": "test"
}
```

Output json `out/some_output.json`:

```json
{
  "test": {
    "testA": ["testy", "testtest", "test replacement"],
    "testB": 125,
    "testC": {
      "testD": {
        "test": 3.14159
      }
    }
  },
  "testB": true,
  "testC": 1.2345,
  "replacement": "test"
}
```

