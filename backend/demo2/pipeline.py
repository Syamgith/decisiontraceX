"""
Content recommendation pipeline demo.

Demonstrates the DecisionTrace X-Ray SDK with a content recommendation workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path to import decisiontrace
sys.path.insert(0, str(Path(__file__).parent.parent))

from decisiontrace import XRay
from demo2.data.content import USER_PROFILE, CONTENT_POOL
from demo2.steps.profile_analysis import analyze_user_profile
from demo2.steps.content_filter import filter_content
from demo2.steps.ranking import rank_and_diversify


def run_content_recommendation_pipeline():
    """
    Run the complete content recommendation pipeline with X-Ray tracing.
    """
    # Initialize X-Ray SDK
    xray = XRay()

    # Create a trace for this execution
    with xray.trace("content-recommendation-pipeline") as trace:
        print("\n" + "="*80)
        print("CONTENT RECOMMENDATION PIPELINE - X-RAY DEMO")
        print("="*80)

        print(f"\n👤 User: {USER_PROFILE['name']}")
        print(f"   Preferred genres: {', '.join(USER_PROFILE['preferences']['genres'])}")
        print(f"   Average rating: {USER_PROFILE['average_rating']}★")

        # ─────────────────────────────────────────────────────
        # Step 1: User Profile Analysis
        # ─────────────────────────────────────────────────────
        with trace.step("user_profile_analysis") as step:
            print("\n[STEP 1] Analyzing user profile...")

            step.set_input({
                "user_id": USER_PROFILE["user_id"],
                "name": USER_PROFILE["name"],
                "preferences": USER_PROFILE["preferences"],
                "watch_history_count": len(USER_PROFILE["watch_history"]),
                "average_rating": USER_PROFILE["average_rating"]
            })

            # Analyze profile
            criteria = analyze_user_profile(USER_PROFILE)

            step.set_output({
                "criteria": criteria
            })

            step.set_reasoning(
                f"Extracted {len(criteria['preferred_genres'])} preferred genres from watch history "
                f"and preferences. Set minimum rating threshold to {criteria['minimum_rating_threshold']} "
                f"based on user's average rating pattern."
            )

            # Add custom metadata
            step.set_metadata({
                "analysis_method": "collaborative-filtering",
                "confidence": 0.85,
                "user_segment": criteria["engagement_level"]
            })

            print(f"  Preferred genres: {criteria['preferred_genres']}")
            print(f"  Minimum rating: {criteria['minimum_rating_threshold']}★")
            print(f"  Engagement: {criteria['engagement_level']}")

        # ─────────────────────────────────────────────────────
        # Step 2: Content Retrieval (Simulated)
        # ─────────────────────────────────────────────────────
        with trace.step("content_retrieval") as step:
            print("\n[STEP 2] Retrieving content from catalog...")

            step.set_input({
                "catalog_query": {
                    "genres": criteria["preferred_genres"],
                    "languages": criteria["preferred_languages"]
                },
                "limit": len(CONTENT_POOL)
            })

            # In real system, this would query a database
            retrieved_content = CONTENT_POOL

            step.set_output({
                "total_retrieved": len(retrieved_content),
                "content_types": {
                    "movie": len([c for c in retrieved_content if c["type"] == "movie"]),
                    "series": len([c for c in retrieved_content if c["type"] == "series"])
                },
                "genre_distribution": {}
            })

            step.set_reasoning(
                f"Retrieved {len(retrieved_content)} content items from catalog matching "
                f"user's language and broad genre preferences"
            )

            print(f"  Retrieved {len(retrieved_content)} content items")

        # ─────────────────────────────────────────────────────
        # Step 3: Apply Filters
        # ─────────────────────────────────────────────────────
        with trace.step("content_filtering") as step:
            print("\n[STEP 3] Applying quality and preference filters...")

            step.set_input({
                "content_count": len(retrieved_content),
                "filters": {
                    "genre_match": criteria["preferred_genres"],
                    "minimum_rating": criteria["minimum_rating_threshold"],
                    "languages": criteria["preferred_languages"],
                    "content_types": criteria["preferred_content_types"]
                }
            })

            # Apply filters
            filter_results = filter_content(retrieved_content, criteria)

            # Set metadata with evaluations (using helper method)
            for evaluation in filter_results["evaluations"]:
                step.add_evaluation(
                    item_id=evaluation["item_id"],
                    item_data=evaluation["item_data"],
                    filters=evaluation["filters"],
                    qualified=evaluation["qualified"],
                    reasoning=evaluation["reasoning"]
                )

            step.set_output({
                "total_evaluated": filter_results["total_evaluated"],
                "passed": filter_results["passed"],
                "failed": filter_results["failed"],
                "pass_rate": round(filter_results["passed"] / filter_results["total_evaluated"] * 100, 1)
            })

            step.set_reasoning(
                f"Applied 4 filters (genre, rating, language, type) to narrow content "
                f"from {filter_results['total_evaluated']} to {filter_results['passed']} items. "
                f"Pass rate: {round(filter_results['passed'] / filter_results['total_evaluated'] * 100, 1)}%"
            )

            print(f"  Evaluated {filter_results['total_evaluated']} items")
            print(f"  ✓ Passed: {filter_results['passed']}")
            print(f"  ✗ Failed: {filter_results['failed']}")

            # Store qualified content for next step
            qualified_content = filter_results["qualified_content"]

        # ─────────────────────────────────────────────────────
        # Step 4: Rank and Diversify
        # ─────────────────────────────────────────────────────
        with trace.step("ranking_and_diversification") as step:
            print("\n[STEP 4] Ranking content and ensuring diversity...")

            step.set_input({
                "qualified_count": len(qualified_content),
                "target_recommendations": 5,
                "ranking_criteria": {
                    "primary": "relevance_score",
                    "secondary": "popularity_score",
                    "tertiary": "recency_score"
                }
            })

            # Rank and diversify
            ranking_results = rank_and_diversify(qualified_content, USER_PROFILE, top_n=5)

            step.set_metadata({
                "ranking_criteria": {
                    "primary": "relevance_score",
                    "secondary": "popularity_score",
                    "tertiary": "recency_score"
                },
                "ranked_candidates": ranking_results["ranked_content"],
                "diversity_analysis": {
                    "diversity_score": ranking_results["diversity_score"],
                    "unique_genres": ranking_results["unique_genres"],
                    "target_diversity": 0.8
                }
            })

            step.set_output({
                "recommendations": ranking_results["recommendations"],
                "diversity_score": ranking_results["diversity_score"],
                "unique_genres": ranking_results["unique_genres"]
            })

            step.set_reasoning(
                f"Ranked {len(qualified_content)} qualified items using relevance (50%), "
                f"popularity (30%), and recency (20%) weights. Applied diversity algorithm to "
                f"ensure genre variety, achieving diversity score of {ranking_results['diversity_score']}"
            )

            print(f"\n  🎬 TOP 5 RECOMMENDATIONS:")
            for rec in ranking_results["recommendations"]:
                print(f"     {rec['position']}. {rec['title']} ({rec['type']}, {rec['genre']})")
                print(f"        Rating: {rec['rating']}★ | Score: {rec['score']}")

            print(f"\n  📊 Diversity Score: {ranking_results['diversity_score']} ({ranking_results['unique_genres']} unique genres)")

        print("\n" + "="*80)
        print(f"PIPELINE COMPLETED - Trace ID: {trace.trace.trace_id}")
        print("="*80)
        print(f"\nView this trace in the dashboard at:")
        print(f"http://localhost:5173/trace/{trace.trace.trace_id}")
        print()

    # Close X-Ray
    xray.close()


if __name__ == "__main__":
    run_content_recommendation_pipeline()
