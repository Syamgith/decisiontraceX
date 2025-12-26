# Demo Scenarios

This document describes the two demo applications included with DecisionTrace X-Ray.

## Why Two Demos?

Having two completely different demo applications proves that the X-Ray SDK is **truly general-purpose** and not tied to any specific domain. Both demos use the exact same SDK without modification, demonstrating the power of the metadata-based architecture.

---

## Demo 1: Competitor Product Selection (E-commerce)

### Scenario
An e-commerce seller wants to find the best competitor product to benchmark against their own product.

### Pipeline Flow

```
Reference Product (32oz water bottle, $29.99)
    ↓
[1] Keyword Generation (Mock LLM)
    ↓ Generates: ["stainless steel water bottle insulated", "insulated bottle 32oz"]
    ↓
[2] Candidate Search (Mock API)
    ↓ Retrieves: 20 products from catalog
    ↓
[3] Apply Filters
    ├─ Price: 0.5x - 2x of reference ($15 - $60)
    ├─ Rating: Minimum 3.8 stars
    └─ Reviews: Minimum 100 reviews
    ↓ Qualified: 11 products
    ↓
[4] Rank & Select
    ├─ Score by: Review count (50%), Rating (30%), Price proximity (20%)
    └─ Winner: HydroFlask 32oz ($44.99, 4.5★, 8,932 reviews)
```

### Key Metadata Patterns Used
- **LLM Metadata**: Model, tokens, temperature for keyword generation
- **Filter Evaluations**: Detailed pass/fail for each product
- **Ranked Candidates**: Score breakdown for top products

### Run Command
```bash
cd backend
python -m demo.pipeline
```

---

## Demo 2: Content Recommendation (Streaming Platform)

### Scenario
A streaming platform wants to recommend personalized content to a user based on their watch history and preferences.

### Pipeline Flow

```
User Profile (Alex Thompson, likes sci-fi/thriller/documentary)
    ↓
[1] User Profile Analysis
    ↓ Extracts: Preferred genres, minimum rating threshold (4.25★)
    ↓
[2] Content Retrieval
    ↓ Fetches: 20 content items from catalog
    ↓
[3] Content Filtering
    ├─ Genre: Must match user preferences
    ├─ Rating: Minimum 4.25 stars
    ├─ Language: English or user's languages
    └─ Type: Movie or Series (user's preferences)
    ↓ Qualified: 14 items
    ↓
[4] Ranking & Diversification
    ├─ Score by: Relevance (50%), Popularity (30%), Recency (20%)
    ├─ Apply diversity: Ensure genre variety
    └─ Top 5: Our Planet, Stranger Things, Mindhunter, The Crown, Interstellar
    ↓ Diversity Score: 0.8 (4 unique genres)
```

### Key Metadata Patterns Used
- **Custom Metadata**: User segment, analysis method, confidence scores
- **Filter Evaluations**: Genre/rating/language/type checks
- **Ranked Candidates**: Multi-factor scoring with diversity analysis

### Run Command
```bash
cd backend
python -m demo2.pipeline
```

---

## Comparison Table

| Aspect | Demo 1 (E-commerce) | Demo 2 (Streaming) |
|--------|---------------------|-------------------|
| **Domain** | Product selection | Content recommendation |
| **Input** | Product attributes | User profile + watch history |
| **Steps** | 4 | 4 |
| **LLM Usage** | Keyword generation | None (rule-based) |
| **Filter Count** | 3 filters | 4 filters |
| **Ranking Logic** | Review-heavy | Relevance-heavy |
| **Special Feature** | Price proximity | Genre diversity |
| **Data Size** | 20 products | 20 content items |

---

## What They Prove

### ✅ General-Purpose Design
Both demos use the same SDK with **zero code changes**:
- Same `XRay` context manager
- Same `add_evaluation()` helper
- Same metadata patterns
- Same dashboard rendering

### ✅ Flexible Metadata
Different workflows, different metadata:
- E-commerce: Price ranges, review counts, LLM tokens
- Streaming: User segments, diversity scores, relevance factors

### ✅ Pattern Detection
Dashboard automatically detects and renders:
- Filter evaluation tables
- LLM metadata cards
- Ranking results with scores
- Custom JSON for unknown patterns

### ✅ Real-World Applicability
Both scenarios represent **actual production use cases**:
- E-commerce platforms need competitor analysis
- Streaming platforms need personalized recommendations

---

## Viewing in the Dashboard

1. **Run both demos** to generate traces
2. **Start the API**: `uvicorn api.main:app --reload`
3. **Start the dashboard**: `cd frontend && npm run dev`
4. **Open**: http://localhost:5173

You'll see traces from both demos in the list. Click into any trace to see:
- Different pipeline structures
- Different filter evaluations
- Different ranking criteria
- Same beautiful visualization!

---

## Adding Your Own Demo

To add a third demo for a different domain:

1. **Create demo3/ directory** with:
   - `data/` - Your domain data
   - `steps/` - Your pipeline logic
   - `pipeline.py` - Main runner

2. **Use the same SDK**:
   ```python
   from decisiontrace import XRay

   xray = XRay()
   with xray.trace("your-workflow") as trace:
       with trace.step("your_step") as step:
           step.set_input({...})
           # Your logic here
           step.set_output({...})
           step.set_reasoning("...")
   ```

3. **Run it**: `python -m demo3.pipeline`

4. **It just works!** Dashboard automatically:
   - Lists your traces
   - Renders your steps
   - Detects your metadata patterns
   - Shows your decision trail

That's the power of a truly general-purpose system! 🚀
