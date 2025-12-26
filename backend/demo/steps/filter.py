"""
Filter and selection logic for competitor products.

Applies business rules and ranking to select the best competitor.
"""

from typing import Dict, Any, List


def apply_filters(
    candidates: List[Dict[str, Any]],
    reference_product: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply filters to candidate products.

    Filters:
    - Price range: 0.5x - 2x of reference price
    - Rating: minimum 3.8 stars
    - Reviews: minimum 100 reviews

    Args:
        candidates: List of candidate products
        reference_product: Reference product for comparison

    Returns:
        Dict with filter results and qualified candidates
    """
    ref_price = reference_product["price"]
    price_min = ref_price * 0.5
    price_max = ref_price * 2.0

    evaluations = []
    qualified_candidates = []

    for candidate in candidates:
        # Evaluate each filter
        price_check = {
            "name": "price_range",
            "passed": price_min <= candidate["price"] <= price_max,
            "detail": f"${candidate['price']:.2f} {'is within' if price_min <= candidate['price'] <= price_max else 'outside'} ${price_min:.2f}-${price_max:.2f}"
        }

        rating_check = {
            "name": "min_rating",
            "passed": candidate["rating"] >= 3.8,
            "detail": f"{candidate['rating']} {'>=' if candidate['rating'] >= 3.8 else '<'} 3.8 threshold"
        }

        reviews_check = {
            "name": "min_reviews",
            "passed": candidate["reviews"] >= 100,
            "detail": f"{candidate['reviews']} {'>=' if candidate['reviews'] >= 100 else '<'} 100 minimum"
        }

        # Determine if candidate qualifies
        filters = [price_check, rating_check, reviews_check]
        qualified = all(f["passed"] for f in filters)

        # Build evaluation record
        evaluation = {
            "item_id": candidate["asin"],
            "item_data": {
                "title": candidate["title"],
                "price": candidate["price"],
                "rating": candidate["rating"],
                "reviews": candidate["reviews"]
            },
            "filters": filters,
            "qualified": qualified,
            "reasoning": "Passed all filters" if qualified else f"Failed: {', '.join(f['name'] for f in filters if not f['passed'])}"
        }

        evaluations.append(evaluation)

        if qualified:
            qualified_candidates.append(candidate)

    return {
        "evaluations": evaluations,
        "qualified_candidates": qualified_candidates,
        "total_evaluated": len(candidates),
        "passed": len(qualified_candidates),
        "failed": len(candidates) - len(qualified_candidates)
    }


def rank_and_select(
    qualified_candidates: List[Dict[str, Any]],
    reference_product: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Rank qualified candidates and select the best competitor.

    Ranking criteria:
    - Primary: Review count (more reviews = more established)
    - Secondary: Rating (higher rating = better quality)
    - Tertiary: Price proximity to reference

    Args:
        qualified_candidates: List of candidates that passed filters
        reference_product: Reference product for comparison

    Returns:
        Dict with ranked candidates and final selection
    """
    if not qualified_candidates:
        return {
            "ranked_candidates": [],
            "selection": None,
            "reason": "No qualified candidates available"
        }

    ref_price = reference_product["price"]

    # Calculate scores for each candidate
    max_reviews = max(c["reviews"] for c in qualified_candidates)
    max_rating = 5.0

    scored_candidates = []
    for candidate in qualified_candidates:
        # Normalize scores (0-1 range)
        review_count_score = candidate["reviews"] / max_reviews if max_reviews > 0 else 0
        rating_score = candidate["rating"] / max_rating

        # Price proximity score (closer to reference = higher score)
        price_diff = abs(candidate["price"] - ref_price)
        max_price_diff = ref_price  # Maximum expected difference
        price_proximity_score = 1 - min(price_diff / max_price_diff, 1)

        # Weighted total score (review count is most important)
        total_score = (
            review_count_score * 0.5 +  # 50% weight
            rating_score * 0.3 +          # 30% weight
            price_proximity_score * 0.2   # 20% weight
        )

        scored_candidates.append({
            "candidate": candidate,
            "scores": {
                "review_count_score": round(review_count_score, 2),
                "rating_score": round(rating_score, 2),
                "price_proximity_score": round(price_proximity_score, 2),
                "total_score": round(total_score, 2)
            }
        })

    # Sort by total score (highest first)
    scored_candidates.sort(key=lambda x: x["scores"]["total_score"], reverse=True)

    # Build ranked list
    ranked_candidates = []
    for idx, sc in enumerate(scored_candidates, start=1):
        candidate = sc["candidate"]
        ranked_candidates.append({
            "rank": idx,
            "asin": candidate["asin"],
            "title": candidate["title"],
            "metrics": {
                "price": candidate["price"],
                "rating": candidate["rating"],
                "reviews": candidate["reviews"]
            },
            "score_breakdown": sc["scores"]
        })

    # Select top candidate
    top_candidate = scored_candidates[0]["candidate"]
    top_scores = scored_candidates[0]["scores"]

    selection = {
        "asin": top_candidate["asin"],
        "title": top_candidate["title"],
        "price": top_candidate["price"],
        "rating": top_candidate["rating"],
        "reviews": top_candidate["reviews"],
        "reason": f"Highest overall score ({top_scores['total_score']}) - top review count ({top_candidate['reviews']:,}) with strong rating ({top_candidate['rating']}★)"
    }

    return {
        "ranked_candidates": ranked_candidates,
        "selection": selection
    }
