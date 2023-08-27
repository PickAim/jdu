import os
import pickle
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


__NICHE_TO_CATEGORY: Final[str] = get_path(file_dir, 'niche_to_category.paim')
with open(__NICHE_TO_CATEGORY, 'rb') as file:
    NICHE_TO_CATEGORY: Final[dict[str, str]] = pickle.load(file)
COMMISSION_WILDBERRIES_JSON: Final[str] = get_path(file_dir, 'commission.json')
COMMISSION_WILDBERRIES_CSV: Final[str] = get_path(file_dir, 'commission.csv')

COMMISSION_KEY: Final[str] = "commission"
RETURN_PERCENT_KEY: Final[str] = "return_percent"

WILDBERRIES_NAME: Final[str] = 'wildberries'
