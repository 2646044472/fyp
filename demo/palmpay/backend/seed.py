from .db import Session
from .models import Merchant, Product, Terminal, Wallet

PRODUCTS = [
    ("americano", "Americano", "Coffee", 2000),
    ("iced-latte", "Iced Latte", "Coffee", 2500),
    ("cappuccino", "Cappuccino", "Coffee", 2500),
    ("apple-espresso", "Apple Espresso", "Coffee", 2500),
    ("matcha", "Matcha Latte", "Non-coffee", 2500),
    ("chocolate", "Sea Salt Chocolate", "Non-coffee", 2000),
    ("pomelo", "Honey Pomelo", "Non-coffee", 2000),
]

def seed():
    with Session.begin() as db:
        if db.get(Merchant, "cklc"):
            return
        db.add(Merchant(id="cklc", name="CKLC Coffee"))
        db.flush()
        db.add_all([Terminal(id="register-01", merchant_id="cklc", name="Register 01"),
                    Wallet(id="cklc", merchant_id="cklc", balance=0)])
        for key, name, category, price in PRODUCTS:
            db.add(Product(id=key, merchant_id="cklc", name=name, category=category,
                           price=price, image=f"/drinks/{key}.jpg"))

