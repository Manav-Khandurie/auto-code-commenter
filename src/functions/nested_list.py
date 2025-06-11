        def flatten(nested_list):
    """Flatten a nested list structure into a single flat list.

    Args:
        nested_list: A list that may contain nested lists as elements.

    Returns:
        A new list with all elements from nested_list and any sublists,
        in a single level of nesting.
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten(item))  # Recursively flatten sublists
        else:
            flat_list.append(item)
    return flat_list