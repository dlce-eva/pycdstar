"""
Utilities used in pycdstar commands.
"""
import json
import pathlib
from typing import Union

from pycdstar.resource import Object


def set_metadata(spec: Union[str, pathlib.Path], obj: Object) -> bool:
    """Set the metadata of Object reading JSON data from string or file."""
    if spec:
        spec_as_path = pathlib.Path(spec)
        if spec_as_path.exists() and spec_as_path.is_file():
            spec = spec_as_path.read_text(encoding='utf8')
        obj.metadata = json.loads(spec)
        return True
    return False
