"""
Content ranking and diversity scoring.

Ranks qualified content and ensures diversity in recommendations.
"""

from typing import Dict, Any, List


def rank_and_diversify(
    qualified_content: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Rank qualified content and ensure diversity.

    Ranking criteria:
    - Primary: Relevance score (genre match + rating)
    - Secondary: Popularity score
    - Tertiary: Recency (newer content preferred)

    Diversity: Ensure varied genres in top recommendations

    Args:
        qualified_content: List of content that passed filters
        user_profile: User profile for personalization
        top_n: Number of recommendations to return

    Returns:
        Dict with ranked content and diversity analysis
    """
    if not qualified_content:
        return {
            "ranked_content": [],
            "recommendations": [],
            "diversity_score": 0,
            "reason": "No qualified content available"
        }

    # Calculate scores for each content
    scored_content = []
    for content in qualified_content:
        # Relevance score (0-1)
        # Check if genre is in user's top preferences
        genre_relevance = 1.0 if content["genre"] in user_profile["preferences"]["genres"] else 0.7

        # Normalize rating (assuming max rating is 5)
        rating_score = content["rating"] / 5.0

        # Combine for relevance
        relevance_score = (genre_relevance * 0.6 + rating_score * 0.4)

        # Popularity score (already normalized 0-1)
        popularity_score = content["popularity_score"]

        # Recency score (newer is better)
        current_year = 2024
        years_old = current_year - content["release_year"]
        recency_score = max(0, 1 - (years_old / 20))  # Decay over 20 years

        # Weighted total score
        total_score = (
            relevance_score * 0.5 +      # 50% weight
            popularity_score * 0.3 +     # 30% weight
            recency_score * 0.2          # 20% weight
        )

        scored_content.append({
            "content": content,
            "scores": {
                "relevance_score": round(relevance_score, 2),
                "popularity_score": round(popularity_score, 2),
                "recency_score": round(recency_score, 2),
                "total_score": round(total_score, 2)
            }
        })

    # Sort by total score (highest first)
    scored_content.sort(key=lambda x: x["scores"]["total_score"], reverse=True)

    # Apply diversity: ensure genre variety in top N
    diverse_recommendations = []
    seen_genres = set()
    remaining_slots = top_n

    # First pass: one from each genre
    for sc in scored_content:
        if remaining_slots == 0:
            break
        genre = sc["content"]["genre"]
        if genre not in seen_genres:
            diverse_recommendations.append(sc)
            seen_genres.add(genre)
            remaining_slots -= 1

    # Second pass: fill remaining slots with highest scoring
    for sc in scored_content:
        if remaining_slots == 0:
            break
        if sc not in diverse_recommendations:
            diverse_recommendations.append(sc)
            remaining_slots -= 1

    # Build ranked list
    ranked_content = []
    for idx, sc in enumerate(scored_content[:top_n * 2], start=1):  # Show more in rankings
        content = sc["content"]
        ranked_content.append({
            "rank": idx,
            "content_id": content["content_id"],
            "title": content["title"],
            "type": content["type"],
            "genre": content["genre"],
            "metrics": {
                "rating": content["rating"],
                "views": content["views"],
                "release_year": content["release_year"]
            },
            "score_breakdown": sc["scores"]
        })

    # Calculate diversity score
    unique_genres = len(set(rec["content"]["genre"] for rec in diverse_recommendations))
    diversity_score = unique_genres / min(top_n, len(diverse_recommendations)) if diverse_recommendations else 0

    # Build final recommendations
    recommendations = []
    for idx, rec in enumerate(diverse_recommendations, start=1):
        content = rec["content"]
        recommendations.append({
            "position": idx,
            "content_id": content["content_id"],
            "title": content["title"],
            "type": content["type"],
            "genre": content["genre"],
            "rating": content["rating"],
            "score": rec["scores"]["total_score"],
            "reason": f"High relevance ({rec['scores']['relevance_score']}) and popularity ({rec['scores']['popularity_score']})"
        })

    return {
        "ranked_content": ranked_content,
        "recommendations": recommendations,
        "diversity_score": round(diversity_score, 2),
        "unique_genres": unique_genres,
        "total_candidates": len(qualified_content)
    }
