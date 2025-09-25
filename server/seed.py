from app import app, db
from models import Category, Product

# Categories
categories = [
    {"name": "Denim", "description": "All things denim, from jeans to skirts."},
    {"name": "Outerwear", "description": "Jackets, coats, and layers."},
    {"name": "Formalwear", "description": "Suits and clothing for special occasions."},
    {"name": "Casualwear", "description": "Everyday relaxed clothing."},
    {"name": "Accessories", "description": "Bags, hats, sunglasses, belts, and more."},
    {"name": "Footwear", "description": "Shoes, sneakers, and boots."},
    {"name": "Sportswear", "description": "Active and athleisure wear."},
    {"name": "Party Wear", "description": "Outfits for nightlife and celebrations."},
]

# Products mapped to categories
products = [
    {"name": "Retro Leather Jacket", "description": "Classic brown leather jacket.", "price": 120, "stock": 10, "category": "Outerwear"},
    {"name": "Vintage Denim Skirt", "description": "High-waist blue denim skirt.", "price": 45, "stock": 15, "category": "Denim"},
    {"name": "Retro Sunglasses", "description": "Round frame sunglasses from the 80s.", "price": 25, "stock": 30, "category": "Accessories"},
    {"name": "Classic Wool Coat", "description": "Elegant wool coat for winter fashion.", "price": 150, "stock": 8, "category": "Outerwear"},
    {"name": "Vintage Plaid Shirt", "description": "Comfortable cotton plaid shirt.", "price": 35, "stock": 20, "category": "Casualwear"},
    {"name": "Retro Sneakers", "description": "Classic white sneakers from the 90s.", "price": 60, "stock": 25, "category": "Footwear"},
    {"name": "Vintage Fedora Hat", "description": "Stylish fedora hat for a retro look.", "price": 30, "stock": 12, "category": "Accessories"},
    {"name": "Retro Leather Boots", "description": "High-quality brown leather boots.", "price": 110, "stock": 10, "category": "Footwear"},
    {"name": "Vintage Knit Sweater", "description": "Soft cozy sweater for autumn days.", "price": 55, "stock": 18, "category": "Casualwear"},
    {"name": "Retro Backpack", "description": "Canvas backpack with classic design.", "price": 40, "stock": 20, "category": "Accessories"},
    {"name": "Vintage Belt", "description": "Leather belt with brass buckle.", "price": 20, "stock": 25, "category": "Accessories"},
    {"name": "Retro Watch", "description": "Classic analog watch with leather strap.", "price": 80, "stock": 15, "category": "Accessories"},
]

def seed():
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        db.create_all()

        print("Adding categories...")
        category_objs = {}
        for cat in categories:
            c = Category(name=cat["name"], description=cat["description"])
            db.session.add(c)
            category_objs[cat["name"]] = c

        db.session.commit()

        print("Adding products...")
        for prod in products:
            p = Product(
                name=prod["name"],
                description=prod["description"],
                price=prod["price"],
                stock=prod["stock"],
                category=category_objs[prod["category"]],
            )
            db.session.add(p)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
