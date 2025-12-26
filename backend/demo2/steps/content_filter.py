"""
Content filtering step.

Filters content based on user preferences and quality thresholds.
"""

from typing import Dict, Any, List


def filter_content(
    content_pool: List[Dict[str, Any]],
    criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Filter content based on recommendation criteria.

    Filters:
    - Genre match (must match at least one preferred genre)
    - Minimum rating (must be above threshold)
    - Language support (must be in user's languages OR english)
    - Content type (must match user's preferred types)

    Args:
        content_pool: List of available content
        criteria: Recommendation criteria from profile analysis

    Returns:
        Dict with filter results and qualified content
    """
    evaluations = []
    qualified_content = []

    for content in content_pool:
        # Genre filter
        genre_match = content["genre"] in criteria["preferred_genres"]
        genre_check = {
            "name": "genre_match",
            "passed": genre_match,
            "detail": f"Genre '{content['genre']}' {'matches' if genre_match else 'does not match'} preferences {criteria['preferred_genres']}"
        }

        # Rating filter
        rating_check = {
            "name": "minimum_rating",
            "passed": content["rating"] >= criteria["minimum_rating_threshold"],
            "detail": f"{content['rating']} {'>=' if content['rating'] >= criteria['minimum_rating_threshold'] else '<'} {criteria['minimum_rating_threshold']} threshold"
        }

        # Language filter (english is always acceptable)
        language_match = (
            content["language"] in criteria["preferred_languages"] or
            content["language"] == "english"
        )
        language_check = {
            "name": "language_support",
            "passed": language_match,
            "detail": f"Language '{content['language']}' {'is supported' if language_match else 'not supported'}"
        }

        # Content type filter
        type_match = content["type"] in criteria["preferred_content_types"]
        type_check = {
            "name": "content_type",
            "passed": type_match,
            "detail": f"Type '{content['type']}' {'matches' if type_match else 'does not match'} preferences {criteria['preferred_content_types']}"
        }

        # Determine if content qualifies
        filters = [genre_check, rating_check, language_check, type_check]
        qualified = all(f["passed"] for f in filters)

        # Build evaluation record
        evaluation = {
            "item_id": content["content_id"],
            "item_data": {
                "title": content["title"],
                "genre": content["genre"],
                "type": content["type"],
                "rating": content["rating"],
                "language": content["language"],
                "views": content["views"]
            },
            "filters": filters,
            "qualified": qualified,
            "reasoning": "Passed all filters" if qualified else f"Failed: {', '.join(f['name'] for f in filters if not f['passed'])}"
        }

        evaluations.append(evaluation)

        if qualified:
            qualified_content.append(content)

    return {
        "evaluations": evaluations,
        "qualified_content": qualified_content,
        "total_evaluated": len(content_pool),
        "passed": len(qualified_content),
        "failed": len(content_pool) - len(qualified_content)
    }
