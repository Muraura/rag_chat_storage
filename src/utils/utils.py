from collections import OrderedDict


async def sort_dict(unsorted_dict):
    sorted_dict = OrderedDict(sorted(unsorted_dict.items()))
    return sorted_dict
