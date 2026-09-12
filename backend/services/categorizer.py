"""
Merchant categorization service for mapping transaction merchants to expense categories.
"""

CATEGORY_MAP: dict[str, list[str]] = {
    "Food": ["swiggy", "zomato", "canteen", "tea", "restaurant"],
    "Travel": ["ola", "uber", "rapido", "metro", "petrol"],
    "Shopping": ["dmart", "amazon", "flipkart", "myntra"],
    "Bills": ["recharge", "electricity", "wifi", "ticket", "bill"],
    "Health": ["pharmacy", "gym"],
}

CATEGORY_COLORS: dict[str, str] = {
    "Shopping": "#8E44AD",  # Royal Violet
    "Bills": "#2980B9",     # Ocean Blue
    "Food": "#E67E22",      # Vibrant Amber
    "Travel": "#16A085",    # Teal
    "Health": "#27AE60",    # Emerald
    "Other": "#7F8C8D",     # Slate Gray
}

def get_category(merchant_name: str) -> str:
    """Get the category for a given merchant name based on keywords"""
    merchant_clean = merchant_name.lower().strip()

    for category, keywords in CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword in merchant_clean:
                return category

    return "Other"

def get_category_color(category: str) -> str:
    """Return the designated UI color for a category"""
    return CATEGORY_COLORS.get(category, CATEGORY_COLORS["Other"])
