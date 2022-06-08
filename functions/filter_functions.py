from fastapi import HTTPException


async def book_filtering(books: list[dict], filters: dict):
    # This is an excerpt from my grab-fork-from-libgen.
    # This is equivalent to the .get_all() method.

    filtered_results = []
    for book in books:
        meets_criteria = False
        for filter_key, filter_value in filters.items():
            try:
                # Checks if the current filter exists and equals to the value inside a book's dict.
                if book[filter_key] == filter_value:
                    # This runs if a filter matches, meaning that, for now at least, it match **all** the filters.
                    meets_criteria = True
                    continue
                else:
                    # If one filter doesn't match, then the book doesn't meet all criteria.
                    meets_criteria = False
                    break
            except KeyError:
                raise HTTPException(400, f"Invalid filter. Filter '{filter_key}' is not a valid filter.")

        # If, at the end of the loop, the book matches all the filters, then add it to the filtered_results.
        # Since this is still inside the first for loop, it will check for every book in the results' dict.
        if meets_criteria:
            filtered_results.append(book)

    # An empty list evaluates to false in bool()
    if bool(filtered_results) is False:
        HTTPException(400, "No entry matches the given filters.")
    return filtered_results
