import json
import pathlib


def set_metadata(spec, obj):
    if spec:
        spec_as_path = pathlib.Path(spec)
        if spec_as_path.exists() and spec_as_path.is_file():
            spec = spec_as_path.read_text(encoding='utf8')
        obj.metadata = json.loads(spec)
        return True
    return False
