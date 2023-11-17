import os
from pathlib import Path
from typing import Final

splitted: list[str] = os.getcwd().split(os.sep)[:-1]
splitted[0] += os.sep
file_dir: str = os.path.join(*splitted)


def get_path(dir_to_search: str, file_to_search: str):
    try:
        return str(next(Path(dir_to_search).rglob(file_to_search)))
    except StopIteration:
        return os.path.join(dir_to_search, file_to_search)


COMMISSION_KEY: Final[str] = "commission"
RETURN_PERCENT_KEY: Final[str] = "return_percent"

WILDBERRIES_NAME: Final[str] = 'wildberries'
