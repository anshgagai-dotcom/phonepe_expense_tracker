CATEGORY_MAP: dict[str, list[str]] = {
                                        "Food": ["swiggy", "zomato", "canteen", "tea", "restaurant"],
                                        "Travel" : ["ola", "uber", "rapido", "metro", "petrol"],
                                        "Shopping": ["dmart", "amazon", "flipkart", "myntra"],
                                        "Bills": ["recharge", "electricity", "wifi", "ticket", "bill"],
                                        "Health": ["pharmacy", "gym"],
                                    }

def get_category(merchant_name: str) -> str: 
    """ Get the category for a given merchant name"""
    merchant_clean = merchant_name.lower().strip() 

    for category, keywords in CATEGORY_MAP.items(): 
        for keyword in keywords:
            if keyword in merchant_clean: 
                return category 

    return "Other"

# if __name__ == "__main__":
#     print(get_category("Uber Ride"))
#     print(get_category("I am going to goa"))





