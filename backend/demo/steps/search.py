"""
Candidate search step (mock API).

Simulates a product search API returning candidate products.
"""

import random
from typing import List, Dict, Any


def search_products(keyword: str, product_pool: List[Dict[str, Any]], limit: int = 50) -> Dict[str, Any]:
    """
    Mock product search API.

    Simulates searching for products matching a keyword.

    Args:
        keyword: Search keyword
        product_pool: Pool of available products
        limit: Maximum number of results to return

    Returns:
        Dict with total_results, candidates_fetched, and candidates list
    """
    # Simple keyword matching (case-insensitive)
    keyword_lower = keyword.lower()
    keyword_terms = set(keyword_lower.split())

    # Score each product by keyword relevance
    scored_products = []
    for product in product_pool:
        title_lower = product["title"].lower()
        title_terms = set(title_lower.split())

        # Count matching terms
        matching_terms = keyword_terms.intersection(title_terms)
        relevance_score = len(matching_terms)

        # Bonus for exact phrase match
        if keyword_lower in title_lower:
            relevance_score += 10

        scored_products.append({
            "product": product,
            "score": relevance_score
        })

    # Sort by relevance score (highest first)
    scored_products.sort(key=lambda x: x["score"], reverse=True)

    # Filter out products with score 0 (no matches)
    relevant_products = [sp["product"] for sp in scored_products if sp["score"] > 0]

    # If we have fewer relevant products than requested, add some random ones
    if len(relevant_products) < limit:
        remaining_products = [p for p in product_pool if p not in relevant_products]
        random.shuffle(remaining_products)
        additional_count = min(limit - len(relevant_products), len(remaining_products))
        relevant_products.extend(remaining_products[:additional_count])

    # Return top N results
    candidates = relevant_products[:limit]

    return {
        "total_results": len(product_pool) * 50,  # Simulate large result set
        "candidates_fetched": len(candidates),
        "candidates": candidates
    }
