from collections import Counter


def has_similar(commission_json: dict[str, any]) -> bool:
    niche_list: list[str] = []
    for niche_commision_data_name in commission_json:
        niche_list.append(niche_commision_data_name)
    niche_dict_similar: dict = Counter(niche_list)
    for niche_name in niche_dict_similar:
        if niche_dict_similar[niche_name] > 1:
            return True
    return False
