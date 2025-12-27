"""
Competitor selection pipeline demo.

Demonstrates the DecisionTrace X-Ray SDK with a 3-step workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path to import decisiontrace
sys.path.insert(0, str(Path(__file__).parent.parent))

from decisiontrace import XRay
from demo.data.products import REFERENCE_PRODUCT, PRODUCT_POOL
from demo.steps.keywords import generate_keywords
from demo.steps.search import search_products
from demo.steps.filter import apply_filters, rank_and_select


def run_competitor_selection_pipeline():
    """
    Run the complete competitor selection pipeline with X-Ray tracing.
    """
    # Initialize X-Ray SDK
    xray = XRay()

    # Create a trace for this execution
    with xray.trace("competitor-selection-pipeline") as trace:
        print("\n" + "="*80)
        print("COMPETITOR SELECTION PIPELINE - X-RAY DEMO")
        print("="*80)

        # ─────────────────────────────────────────────────────
        # Step 1: Keyword Generation (Mock LLM)
        # ─────────────────────────────────────────────────────
        with trace.step("keyword_generation") as step:
            print("\n[STEP 1] Generating search keywords...")

            step.set_input({
                "product_title": REFERENCE_PRODUCT["title"],
                "category": REFERENCE_PRODUCT["category"]
            })

            # Generate keywords
            keywords = generate_keywords(
                REFERENCE_PRODUCT["title"],
                REFERENCE_PRODUCT["category"]
            )

            step.set_output({
                "keywords": keywords,
                "count": len(keywords)
            })

            # Build dynamic reasoning based on what was actually extracted
            attributes_found = []
            title_lower = REFERENCE_PRODUCT["title"].lower()

            # Check what attributes were identified
            if "stainless steel" in title_lower:
                attributes_found.append("material (stainless steel)")
            if "32oz" in title_lower:
                attributes_found.append("capacity (32oz)")
            if "insulated" in title_lower:
                attributes_found.append("feature (insulated)")

            # Generate dynamic reasoning
            if attributes_found:
                step.set_reasoning(
                    f"Generated {len(keywords)} search keywords by extracting key attributes: "
                    f"{', '.join(attributes_found)}. Primary keyword: '{keywords[0]}'"
                )
            else:
                step.set_reasoning(
                    f"Generated {len(keywords)} search keywords from product title. "
                    f"Primary keyword: '{keywords[0]}'"
                )

            # Add LLM metadata
            step.add_llm_metadata(
                model="mock-gpt-4",
                tokens_used=45,
                temperature=0.7
            )

            print(f"  Generated {len(keywords)} keywords: {keywords}")

        # ─────────────────────────────────────────────────────
        # Step 2: Candidate Search (Mock API)
        # ─────────────────────────────────────────────────────
        with trace.step("candidate_search") as step:
            print("\n[STEP 2] Searching for candidate products...")

            primary_keyword = keywords[0]
            step.set_input({
                "keyword": primary_keyword,
                "limit": 50
            })

            # Search for products
            search_results = search_products(primary_keyword, PRODUCT_POOL, limit=50)

            step.set_output({
                "total_results": search_results["total_results"],
                "candidates_fetched": search_results["candidates_fetched"],
                "candidates_sample": [
                    {
                        "asin": c["asin"],
                        "title": c["title"],
                        "price": c["price"],
                        "rating": c["rating"],
                        "reviews": c["reviews"]
                    }
                    for c in search_results["candidates"][:5]  # Show first 5 as sample
                ]
            })

            step.set_reasoning(
                f"Fetched top {search_results['candidates_fetched']} results by relevance; "
                f"{search_results['total_results']:,} total matches found in database"
            )

            print(f"  Found {search_results['total_results']:,} total results")
            print(f"  Fetched {search_results['candidates_fetched']} candidates")

            # Store full candidates for next step
            candidates = search_results["candidates"]

        # ─────────────────────────────────────────────────────
        # Step 3: Apply Filters
        # ─────────────────────────────────────────────────────
        with trace.step("apply_filters") as step:
            print("\n[STEP 3] Applying filters to candidates...")

            step.set_input({
                "candidates_count": len(candidates),
                "reference_product": {
                    "asin": REFERENCE_PRODUCT["asin"],
                    "title": REFERENCE_PRODUCT["title"],
                    "price": REFERENCE_PRODUCT["price"],
                    "rating": REFERENCE_PRODUCT["rating"],
                    "reviews": REFERENCE_PRODUCT["reviews"]
                }
            })

            # Apply filters
            filter_results = apply_filters(candidates, REFERENCE_PRODUCT)

            # Set metadata with evaluations (using helper method)
            for evaluation in filter_results["evaluations"]:
                step.add_evaluation(
                    item_id=evaluation["item_id"],
                    item_data=evaluation["item_data"],
                    filters=evaluation["filters"],
                    qualified=evaluation["qualified"],
                    reasoning=evaluation["reasoning"]
                )

            # Also set high-level metadata
            step.set_metadata({
                "filters_applied": {
                    "price_range": {
                        "min": REFERENCE_PRODUCT["price"] * 0.5,
                        "max": REFERENCE_PRODUCT["price"] * 2.0,
                        "rule": "0.5x - 2x of reference price"
                    },
                    "min_rating": {
                        "value": 3.8,
                        "rule": "Must be at least 3.8 stars"
                    },
                    "min_reviews": {
                        "value": 100,
                        "rule": "Must have at least 100 reviews"
                    }
                }
            })

            step.set_output({
                "total_evaluated": filter_results["total_evaluated"],
                "passed": filter_results["passed"],
                "failed": filter_results["failed"]
            })

            step.set_reasoning(
                f"Applied price, rating, and review count filters to narrow candidates "
                f"from {filter_results['total_evaluated']} to {filter_results['passed']}"
            )

            print(f"  Evaluated {filter_results['total_evaluated']} candidates")
            print(f"  ✓ Passed: {filter_results['passed']}")
            print(f"  ✗ Failed: {filter_results['failed']}")

            # Store qualified candidates for next step
            qualified_candidates = filter_results["qualified_candidates"]

        # ─────────────────────────────────────────────────────
        # Step 4: Rank and Select
        # ─────────────────────────────────────────────────────
        with trace.step("rank_and_select") as step:
            print("\n[STEP 4] Ranking and selecting best competitor...")

            step.set_input({
                "candidates_count": len(qualified_candidates),
                "reference_product": {
                    "asin": REFERENCE_PRODUCT["asin"],
                    "title": REFERENCE_PRODUCT["title"],
                    "price": REFERENCE_PRODUCT["price"],
                    "rating": REFERENCE_PRODUCT["rating"],
                    "reviews": REFERENCE_PRODUCT["reviews"]
                }
            })

            # Rank and select
            ranking_results = rank_and_select(qualified_candidates, REFERENCE_PRODUCT)

            step.set_metadata({
                "ranking_criteria": {
                    "primary": "review_count",
                    "secondary": "rating",
                    "tertiary": "price_proximity"
                },
                "ranked_candidates": ranking_results["ranked_candidates"]
            })

            step.set_output({
                "selected_competitor": ranking_results["selection"]
            })

            step.set_reasoning(ranking_results["selection"]["reason"] if ranking_results["selection"] else "No qualified candidates")

            if ranking_results["selection"]:
                print(f"\n  🏆 SELECTED COMPETITOR:")
                print(f"     {ranking_results['selection']['title']}")
                print(f"     Price: ${ranking_results['selection']['price']:.2f}")
                print(f"     Rating: {ranking_results['selection']['rating']}★")
                print(f"     Reviews: {ranking_results['selection']['reviews']:,}")
                print(f"     Reason: {ranking_results['selection']['reason']}")
            else:
                print("  ⚠️  No qualified competitor found")

        print("\n" + "="*80)
        print(f"PIPELINE COMPLETED - Trace ID: {trace.trace.trace_id}")
        print("="*80)
        print(f"\nView this trace in the dashboard at:")
        print(f"http://localhost:5173/trace/{trace.trace.trace_id}")
        print()

    # Close X-Ray
    xray.close()


if __name__ == "__main__":
    run_competitor_selection_pipeline()
