import os
from os.path import join, abspath

splitted: list[str] = abspath(__file__).split(os.sep)[:-1]
splitted[0] += os.sep
rootpath: str = join(*splitted)

data_path: str = join(rootpath, "../data")
out_path: str = join(rootpath, "out")
