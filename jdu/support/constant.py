import os

splitted: list[str] = os.getcwd().split(os.sep)[:-1]
splitted[0] += os.sep
file_dir: str = os.path.join(*splitted)

COMMISSION_WILDBERRIES_JSON: str = os.path.join(file_dir, "commission.json")
COMMISSION_WILDBERRIES_CSV: str = os.path.join(file_dir, "commission.csv")

COMMISSION_KEY = "commission"
RETURN_PERCENT_KEY = "return_percent"
