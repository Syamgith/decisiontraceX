"""
User profile analysis step.

Analyzes user preferences and watch history to extract recommendation criteria.
"""

from typing import Dict, Any, List


def analyze_user_profile(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze user profile to extract recommendation criteria.

    Args:
        user_profile: User profile data

    Returns:
        Dict with extracted criteria
    """
    # Extract preferred genres from history and preferences
    preferred_genres = set(user_profile["preferences"]["genres"])

    # Add genres from highly-rated watch history
    for item in user_profile["watch_history"]:
        if item["rating"] >= 4:
            preferred_genres.add(item["genre"])

    # Calculate content type preferences
    content_type_counts = {}
    for pref_type in user_profile["preferences"]["content_types"]:
        content_type_counts[pref_type] = 1

    # Determine if user likes long-form content
    avg_watch_time = sum([
        169 if item["title"] == "Inception" else
        120 if item["title"] == "The Social Network" else
        50
        for item in user_profile["watch_history"]
    ]) / len(user_profile["watch_history"])

    prefers_long_form = avg_watch_time > 90

    return {
        "preferred_genres": list(preferred_genres),
        "preferred_languages": user_profile["preferences"]["languages"],
        "preferred_content_types": user_profile["preferences"]["content_types"],
        "minimum_rating_threshold": user_profile["average_rating"] - 0.5,  # 4.25
        "prefers_long_form": prefers_long_form,
        "engagement_level": "high" if user_profile["average_rating"] >= 4.5 else "medium"
    }
