"""
Dummy product data for competitor selection demo.

Contains realistic product examples with various attributes to test filtering logic.
"""

# Reference product (seller's product)
REFERENCE_PRODUCT = {
    "asin": "B0XYZ123",
    "title": "ProBrand Stainless Steel Water Bottle 32oz Insulated",
    "price": 29.99,
    "rating": 4.2,
    "reviews": 1247,
    "category": "Sports & Outdoors > Water Bottles"
}

# Pool of candidate products with diverse attributes
PRODUCT_POOL = [
    # High-quality competitors (should pass filters)
    {
        "asin": "B0COMP01",
        "title": "HydroFlask 32oz Wide Mouth Insulated Bottle",
        "price": 44.99,
        "rating": 4.5,
        "reviews": 8932,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP02",
        "title": "Yeti Rambler 26oz Vacuum Insulated Bottle",
        "price": 34.99,
        "rating": 4.4,
        "reviews": 5621,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP07",
        "title": "Stanley Adventure Quencher 30oz Tumbler",
        "price": 35.00,
        "rating": 4.3,
        "reviews": 4102,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP08",
        "title": "Contigo Autoseal Insulated Travel Mug 24oz",
        "price": 24.99,
        "rating": 4.4,
        "reviews": 3245,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP09",
        "title": "CamelBak Chute Mag 32oz Water Bottle",
        "price": 22.99,
        "rating": 4.3,
        "reviews": 2876,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP10",
        "title": "Nalgene Wide Mouth 32oz BPA-Free Bottle",
        "price": 15.99,
        "rating": 4.5,
        "reviews": 7654,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP11",
        "title": "Klean Kanteen Classic 32oz Stainless Steel",
        "price": 28.50,
        "rating": 4.4,
        "reviews": 1892,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP12",
        "title": "Thermos Stainless King 32oz Beverage Bottle",
        "price": 32.99,
        "rating": 4.3,
        "reviews": 2134,
        "category": "Sports & Outdoors > Water Bottles"
    },

    # Products that should fail filters (edge cases)
    {
        "asin": "B0COMP03",
        "title": "Generic Plastic Water Bottle 32oz",
        "price": 8.99,
        "rating": 3.2,
        "reviews": 45,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP04",
        "title": "Bottle Cleaning Brush Set with Drying Rack",
        "price": 12.99,
        "rating": 4.6,
        "reviews": 3421,
        "category": "Sports & Outdoors > Accessories"
    },
    {
        "asin": "B0COMP05",
        "title": "Replacement Lid for HydroFlask Wide Mouth",
        "price": 9.99,
        "rating": 4.2,
        "reviews": 892,
        "category": "Sports & Outdoors > Accessories"
    },
    {
        "asin": "B0COMP06",
        "title": "Water Bottle Carrier Bag with Adjustable Strap",
        "price": 14.99,
        "rating": 4.1,
        "reviews": 567,
        "category": "Sports & Outdoors > Accessories"
    },
    {
        "asin": "B0COMP13",
        "title": "Premium Titanium Water Bottle 32oz Ultra-Light",
        "price": 89.00,
        "rating": 4.8,
        "reviews": 234,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP14",
        "title": "Budget Aluminum Bottle 32oz",
        "price": 6.99,
        "rating": 3.5,
        "reviews": 892,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP15",
        "title": "Luxury Crystal Water Bottle with Gold Accents",
        "price": 129.99,
        "rating": 3.9,
        "reviews": 78,
        "category": "Home & Kitchen > Drinkware"
    },
    {
        "asin": "B0COMP16",
        "title": "Collapsible Silicone Water Bottle 24oz",
        "price": 18.99,
        "rating": 4.0,
        "reviews": 1543,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP17",
        "title": "Kids Water Bottle with Cartoon Characters 16oz",
        "price": 12.99,
        "rating": 4.5,
        "reviews": 2345,
        "category": "Baby Products > Feeding"
    },
    {
        "asin": "B0COMP18",
        "title": "Glass Water Bottle with Protective Sleeve 32oz",
        "price": 26.99,
        "rating": 4.2,
        "reviews": 1234,
        "category": "Home & Kitchen > Drinkware"
    },
    {
        "asin": "B0COMP19",
        "title": "Smart Water Bottle with Hydration Tracker",
        "price": 54.99,
        "rating": 3.8,
        "reviews": 456,
        "category": "Sports & Outdoors > Water Bottles"
    },
    {
        "asin": "B0COMP20",
        "title": "Insulated Water Bottle 32oz - New Brand",
        "price": 19.99,
        "rating": 3.9,
        "reviews": 89,
        "category": "Sports & Outdoors > Water Bottles"
    }
]
