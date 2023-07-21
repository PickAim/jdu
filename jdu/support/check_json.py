def has_similar(commission_json: dict[str, any]) -> bool:
    niche_list: set[str] = set()
    for niche_name in commission_json:
        niche_list.add(niche_name)
    return len(niche_list) != len(commission_json)
