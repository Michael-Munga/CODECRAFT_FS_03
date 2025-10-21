from app import app, db
from models import Category, Product, User

# Category seed data
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
    {
        "name": "Retro Leather Jacket",
        "description": "Classic brown leather jacket.",
        "price": 120,
        "stock": 10,
        "category": "Outerwear",
        "image_url": "https://i.pinimg.com/1200x/0b/81/5e/0b815e775d917bd15b5bc21b3ea5840b.jpg",
    },
    {
        "name": "Vintage Denim Skirt",
        "description": "High-waist blue denim skirt.",
        "price": 45,
        "stock": 15,
        "category": "Denim",
        "image_url": "https://i.pinimg.com/1200x/21/3c/ea/213cea7b7b7860b746d979d07ff05d90.jpg",
    },
    {
        "name": "Retro Sunglasses",
        "description": "Round frame sunglasses from the 80s.",
        "price": 25,
        "stock": 30,
        "category": "Accessories",
        "image_url": "https://i.pinimg.com/1200x/0f/2b/58/0f2b58cb5ab3a1352d3335b81b2440a3.jpg",
    },
    {
        "name": "Classic Wool Coat",
        "description": "Elegant wool coat for winter fashion.",
        "price": 150,
        "stock": 8,
        "category": "Outerwear",
        "image_url": "https://i.pinimg.com/736x/1a/c8/88/1ac88833dcb7df656b9cc12e19d9643b.jpg",
    },
    {
        "name": "Vintage Plaid Shirt",
        "description": "Comfortable cotton plaid shirt.",
        "price": 35,
        "stock": 20,
        "category": "Casualwear",
        "image_url": "https://i.pinimg.com/1200x/2b/c8/51/2bc85157bd24da514b908a7ef801f19e.jpg",
    },
    {
        "name": "Retro Sneakers",
        "description": "Classic white sneakers from the 90s.",
        "price": 60,
        "stock": 25,
        "category": "Footwear",
        "image_url": "https://i.pinimg.com/1200x/6c/20/fe/6c20fe13bd22e3681dfb5c4632b658bf.jpg",
    },
    {
        "name": "Vintage Fedora Hat",
        "description": "Stylish fedora hat for a retro look.",
        "price": 30,
        "stock": 12,
        "category": "Accessories",
        "image_url": "https://i.pinimg.com/1200x/ba/d5/b7/bad5b794d6b9b98153ebe227d8cbef53.jpg",
    },
    {
        "name": "Retro Leather Boots",
        "description": "High-quality brown leather boots.",
        "price": 110,
        "stock": 10,
        "category": "Footwear",
        "image_url": "https://i.pinimg.com/1200x/3b/b1/de/3bb1dea3e867be2ebf6db18be806af5c.jpg",
    },
    {
        "name": "Vintage Knit Sweater",
        "description": "Soft cozy sweater for autumn days.",
        "price": 55,
        "stock": 18,
        "category": "Casualwear",
        "image_url": "https://i.pinimg.com/1200x/08/6f/22/086f22b4b78bca51a24e2509e1bd4c84.jpg",
    },
    {
        "name": "Retro Backpack",
        "description": "Canvas backpack with classic design.",
        "price": 40,
        "stock": 20,
        "category": "Accessories",
        "image_url": "https://i.pinimg.com/736x/1f/8a/f6/1f8af6439f73a647a236850160aba7e4.jpg",
    },
    {
        "name": "Vintage Belt",
        "description": "Leather belt with brass buckle.",
        "price": 20,
        "stock": 25,
        "category": "Accessories",
        "image_url": "https://i.pinimg.com/1200x/06/af/d1/06afd1b2780a786034e277131561e117.jpg",
    },
    {
        "name": "Retro Watch",
        "description": "Classic analog watch with leather strap.",
        "price": 80,
        "stock": 15,
        "category": "Accessories",
        "image_url": "https://i.pinimg.com/1200x/d7/89/c2/d789c2fc78b6503fde52069e7eed22c6.jpg",
    },
]


def seed():
    with app.app_context():
        print("Resetting database...")
        db.drop_all()
        db.create_all()

        print("Adding categories...")
        category_objs = {}
        for cat in categories:
            existing = Category.query.filter_by(name=cat["name"]).first()
            if not existing:
                c = Category(name=cat["name"], description=cat["description"])
                db.session.add(c)
                category_objs[cat["name"]] = c
            else:
                category_objs[cat["name"]] = existing

        db.session.commit()

        print("Adding products...")
        for prod in products:
            category = category_objs.get(prod["category"])
            if not category:
                print(f"Warning: Category not found for product '{prod['name']}'")
                continue

            p = Product(
                name=prod["name"],
                description=prod["description"],
                price=prod["price"],
                stock=prod["stock"],
                image_url=prod["image_url"],
                category_id=category.id,
            )
            db.session.add(p)

        db.session.commit()

        print("Adding admin user...")
        existing_admin = User.query.filter_by(email="admin@gmail.com").first()
        if not existing_admin:
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@gmail.com",
                phone_number="+10000000000",
                role="admin",
            )
            admin.set_password("1234")
            db.session.add(admin)
            db.session.commit()

        print("Database seeded successfully.")


if __name__ == "__main__":
    seed()
