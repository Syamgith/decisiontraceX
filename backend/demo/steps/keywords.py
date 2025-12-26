"""
Keyword generation step (mock LLM).

Simulates an LLM extracting search keywords from product attributes.
"""

import re


def generate_keywords(product_title: str, category: str) -> list[str]:
    """
    Mock LLM keyword generation.

    Extracts key attributes from product title using simple string manipulation.

    Args:
        product_title: Product title
        category: Product category

    Returns:
        List of search keywords
    """
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'with', 'for', 'and', 'or', 'of', 'in', 'on'}

    # Convert to lowercase and split
    words = product_title.lower().split()
    filtered_words = [w for w in words if w not in stop_words]

    # Extract capacity if present (e.g., "32oz", "24oz")
    capacity_match = re.search(r'\d+oz', product_title.lower())
    capacity = capacity_match.group() if capacity_match else None

    # Build primary keyword (full product description)
    primary_keyword = ' '.join(filtered_words)

    # Build secondary keyword (material + type + capacity)
    keywords = [primary_keyword]

    # Add variation with capacity
    if capacity:
        variation = f"{'insulated' if 'insulated' in product_title.lower() else ''} bottle {capacity}"
        keywords.append(variation.strip())

    return keywords
