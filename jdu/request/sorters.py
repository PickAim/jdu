

def sort_by_len_alphabet(names: list[str]) -> list[str]:
    length_dict: [int, list[str]] = {}
    for name in names:
        if not length_dict.__contains__(len(name)):
            length_dict[len(name)] = [name]
            continue
        length_dict[len(name)].append(name)
    sorted_tuples: list = sorted(length_dict.items())
    result: list[str] = []
    for length_tuple in sorted_tuples:
        result.extend(sorted(length_tuple[1]))
    return result


def score_object_names(searched_object: str, object_names: list[str]) -> dict[float, list[str]]:
    searched_object = searched_object.lower()
    good_match: float = 5.0
    intermediate_match: float = 2.5
    poor_match: float = 1.0
    searched_words = []
    if len(searched_object) > 1:
        searched_words: list[str] = searched_object.split(" ")
        if len(searched_words) == 1:
            mid_idx: int = len(searched_object) // 2
            searched_words = [searched_object[:mid_idx], searched_object[mid_idx:]]
    lower_names: list[str] = [lower_name.lower() for lower_name in object_names]
    result: dict[float, list[str]] = {good_match: [], intermediate_match: [], poor_match: []}
    for name in lower_names:
        words: list[str] = [word + " " for word in name.split(" ")]
        if words[: len(words) // 2].__contains__(searched_object + " ") \
                or words.__contains__(searched_object + " ") and len(words) < 3:
            result[good_match].append(name)
            continue
        flag: bool = False
        for word_to_match in searched_words:
            if any_contains(word_to_match, words):
                result[intermediate_match].append(name)
                flag = True
                break
        if flag:
            continue
        result[poor_match].append(name)
    return result


def any_contains(text_to_search: str, words: list[str]) -> bool:
    sentence: str = "".join(words)
    for word in words:
        if word.__contains__(text_to_search) and sentence.index(text_to_search) < len(sentence) // 2:
            return True
    return False

