import asyncio

from asyncio import AbstractEventLoop
from os.path import exists, isfile, join
from os import mkdir, listdir

from .sorters import score_object_names, sort_by_len_alphabet
from .request_utils import get_object_names, get_storage_dict, load_all_product_niche


def get_nearest_keywords(word: str) -> list[str]:
    names: list[str] = get_object_names(word)
    scored_dict: dict[float, list[str]] = score_object_names(word, names)
    result: list[str] = []
    for score in scored_dict.keys():
        result.extend(sort_by_len_alphabet(scored_dict[score]))
    return result


def get_storage_data(product_ids: [int]) -> dict[int, dict[int, int]]:
    # TODO needs to delete it after Database implements
    # TODO implements it in Provider classes
    main_dict: dict[int, dict[int, int]] = {}
    for product_id in product_ids:
        dicts = get_storage_dict(product_id)
        main_dict[product_id] = dicts
    return main_dict


def load_niche_info(text: str, output_dir: str, update: bool = False, pages_num: int = -1) -> None:
    # TODO needs to delete it after Database implements
    only_files: list[str] = []
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if exists(output_dir):
        only_files = [f.split('.')[0] for f in listdir(output_dir) if isfile(join(output_dir, f))]
    else:
        mkdir(output_dir)
    if not (text in only_files) or update:
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(load_all_product_niche(text, output_dir, pages_num))
        loop.close()


def load_cost_data_from_file(filename: str) -> list[float]:
    # TODO needs to delete it after Database implements
    result: list[float] = []
    with (open(filename, "r")) as file:
        lines: list[str] = file.readlines()
        for line in lines:
            for cost in line.split(","):
                if cost != "" and cost != "\n":
                    result.append(float(cost))
    return result
