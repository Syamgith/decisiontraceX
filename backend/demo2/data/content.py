"""
Dummy content data for content recommendation demo.

Simulates a content recommendation system for a streaming platform.
"""

# User profile (viewer requesting recommendations)
USER_PROFILE = {
    "user_id": "user_12345",
    "name": "Alex Thompson",
    "age": 28,
    "preferences": {
        "genres": ["sci-fi", "thriller", "documentary"],
        "languages": ["english", "spanish"],
        "content_types": ["movie", "series"]
    },
    "watch_history": [
        {"title": "Inception", "genre": "sci-fi", "rating": 5},
        {"title": "The Social Network", "genre": "drama", "rating": 4},
        {"title": "Planet Earth", "genre": "documentary", "rating": 5},
        {"title": "Black Mirror", "genre": "sci-fi", "rating": 5},
    ],
    "average_rating": 4.75,
    "watch_time_preference": "evening"
}

# Content pool (available content)
CONTENT_POOL = [
    # Sci-fi content (should rank high)
    {
        "content_id": "C001",
        "title": "Interstellar",
        "type": "movie",
        "genre": "sci-fi",
        "subgenre": "space-exploration",
        "language": "english",
        "duration_min": 169,
        "release_year": 2014,
        "rating": 4.6,
        "views": 15000000,
        "popularity_score": 0.95,
        "tags": ["space", "time-travel", "drama"]
    },
    {
        "content_id": "C002",
        "title": "Blade Runner 2049",
        "type": "movie",
        "genre": "sci-fi",
        "subgenre": "cyberpunk",
        "language": "english",
        "duration_min": 164,
        "release_year": 2017,
        "rating": 4.4,
        "views": 8000000,
        "popularity_score": 0.88,
        "tags": ["cyberpunk", "dystopia", "mystery"]
    },
    {
        "content_id": "C003",
        "title": "The Expanse",
        "type": "series",
        "genre": "sci-fi",
        "subgenre": "space-opera",
        "language": "english",
        "duration_min": 45,
        "release_year": 2015,
        "rating": 4.7,
        "views": 12000000,
        "popularity_score": 0.91,
        "tags": ["space", "politics", "thriller"]
    },

    # Thrillers (good match)
    {
        "content_id": "C004",
        "title": "Dark",
        "type": "series",
        "genre": "thriller",
        "subgenre": "mystery",
        "language": "german",
        "duration_min": 50,
        "release_year": 2017,
        "rating": 4.8,
        "views": 10000000,
        "popularity_score": 0.92,
        "tags": ["time-travel", "mystery", "dark"]
    },
    {
        "content_id": "C005",
        "title": "Mindhunter",
        "type": "series",
        "genre": "thriller",
        "subgenre": "crime",
        "language": "english",
        "duration_min": 55,
        "release_year": 2017,
        "rating": 4.5,
        "views": 9000000,
        "popularity_score": 0.87,
        "tags": ["crime", "psychology", "true-story"]
    },

    # Documentaries (match user preference)
    {
        "content_id": "C006",
        "title": "Cosmos: A Spacetime Odyssey",
        "type": "series",
        "genre": "documentary",
        "subgenre": "science",
        "language": "english",
        "duration_min": 43,
        "release_year": 2014,
        "rating": 4.9,
        "views": 7000000,
        "popularity_score": 0.89,
        "tags": ["science", "space", "education"]
    },
    {
        "content_id": "C007",
        "title": "Our Planet",
        "type": "series",
        "genre": "documentary",
        "subgenre": "nature",
        "language": "english",
        "duration_min": 50,
        "release_year": 2019,
        "rating": 4.9,
        "views": 25000000,
        "popularity_score": 0.96,
        "tags": ["nature", "wildlife", "environment"]
    },

    # Content that should fail filters
    {
        "content_id": "C008",
        "title": "Baby Shark Adventures",
        "type": "series",
        "genre": "kids",
        "subgenre": "animation",
        "language": "english",
        "duration_min": 12,
        "release_year": 2020,
        "rating": 3.2,
        "views": 50000000,
        "popularity_score": 0.75,
        "tags": ["kids", "music", "animation"]
    },
    {
        "content_id": "C009",
        "title": "Romantic Getaway",
        "type": "movie",
        "genre": "romance",
        "subgenre": "rom-com",
        "language": "english",
        "duration_min": 95,
        "release_year": 2023,
        "rating": 3.5,
        "views": 2000000,
        "popularity_score": 0.65,
        "tags": ["romance", "comedy", "light"]
    },
    {
        "content_id": "C010",
        "title": "Cooking Masterclass",
        "type": "series",
        "genre": "lifestyle",
        "subgenre": "cooking",
        "language": "french",
        "duration_min": 30,
        "release_year": 2022,
        "rating": 4.1,
        "views": 3000000,
        "popularity_score": 0.72,
        "tags": ["cooking", "tutorial", "food"]
    },

    # More good matches
    {
        "content_id": "C011",
        "title": "Arrival",
        "type": "movie",
        "genre": "sci-fi",
        "subgenre": "first-contact",
        "language": "english",
        "duration_min": 116,
        "release_year": 2016,
        "rating": 4.5,
        "views": 11000000,
        "popularity_score": 0.90,
        "tags": ["aliens", "linguistics", "drama"]
    },
    {
        "content_id": "C012",
        "title": "Stranger Things",
        "type": "series",
        "genre": "sci-fi",
        "subgenre": "supernatural",
        "language": "english",
        "duration_min": 50,
        "release_year": 2016,
        "rating": 4.7,
        "views": 30000000,
        "popularity_score": 0.98,
        "tags": ["supernatural", "80s", "mystery"]
    },
    {
        "content_id": "C013",
        "title": "The Martian",
        "type": "movie",
        "genre": "sci-fi",
        "subgenre": "survival",
        "language": "english",
        "duration_min": 144,
        "release_year": 2015,
        "rating": 4.6,
        "views": 20000000,
        "popularity_score": 0.93,
        "tags": ["space", "survival", "science"]
    },
    {
        "content_id": "C014",
        "title": "Sherlock",
        "type": "series",
        "genre": "thriller",
        "subgenre": "detective",
        "language": "english",
        "duration_min": 90,
        "release_year": 2010,
        "rating": 4.8,
        "views": 18000000,
        "popularity_score": 0.94,
        "tags": ["detective", "mystery", "clever"]
    },
    {
        "content_id": "C015",
        "title": "13th",
        "type": "movie",
        "genre": "documentary",
        "subgenre": "social",
        "language": "english",
        "duration_min": 100,
        "release_year": 2016,
        "rating": 4.7,
        "views": 5000000,
        "popularity_score": 0.85,
        "tags": ["social-justice", "history", "politics"]
    },

    # Edge cases
    {
        "content_id": "C016",
        "title": "Ancient Aliens",
        "type": "series",
        "genre": "documentary",
        "subgenre": "pseudoscience",
        "language": "english",
        "duration_min": 42,
        "release_year": 2009,
        "rating": 2.8,
        "views": 15000000,
        "popularity_score": 0.70,
        "tags": ["aliens", "conspiracy", "pseudoscience"]
    },
    {
        "content_id": "C017",
        "title": "Generic Action Movie 5",
        "type": "movie",
        "genre": "action",
        "subgenre": "explosions",
        "language": "english",
        "duration_min": 105,
        "release_year": 2023,
        "rating": 3.1,
        "views": 8000000,
        "popularity_score": 0.68,
        "tags": ["action", "explosions", "generic"]
    },
    {
        "content_id": "C018",
        "title": "Westworld",
        "type": "series",
        "genre": "sci-fi",
        "subgenre": "western-scifi",
        "language": "english",
        "duration_min": 60,
        "release_year": 2016,
        "rating": 4.4,
        "views": 14000000,
        "popularity_score": 0.89,
        "tags": ["AI", "western", "philosophy"]
    },
    {
        "content_id": "C019",
        "title": "Making a Murderer",
        "type": "series",
        "genre": "documentary",
        "subgenre": "true-crime",
        "language": "english",
        "duration_min": 60,
        "release_year": 2015,
        "rating": 4.6,
        "views": 9000000,
        "popularity_score": 0.88,
        "tags": ["true-crime", "justice", "investigation"]
    },
    {
        "content_id": "C020",
        "title": "The Crown",
        "type": "series",
        "genre": "drama",
        "subgenre": "historical",
        "language": "english",
        "duration_min": 58,
        "release_year": 2016,
        "rating": 4.5,
        "views": 16000000,
        "popularity_score": 0.91,
        "tags": ["history", "royalty", "drama"]
    }
]
