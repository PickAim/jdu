def split_to_chunks(any_list: list[any], chunk_size: int) -> list[any]:
    return list(__divide_chunks(any_list, chunk_size))


def __divide_chunks(any_list: list[any], chunk_size: int):
    for i in range(0, len(any_list), chunk_size):
        yield any_list[i:i + chunk_size]
