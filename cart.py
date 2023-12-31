"""
Author: Bryan Montecino
File: cart.py
Date: September 24, 2023
Assignment: REST APIs
Objective: 
The objective of this assignment is to create a microservices application for grocery shopping.
Developed two Flask microservices, ”Product Service” and ”Cart Service,” with specific endpoints.
Deployed both services on the Render platform. 
Benefits:
This assignment helped me gain practical experience in microservices architecture, API development with Flask, and cloud deployment
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kachowcarts.db'
db = SQLAlchemy(app)

# Define Cart
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Endpoint to retrieve a cart, along with information for each item
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    user_cart = Cart.query.filter_by(user_id=user_id).all()
    cart_items = []
    for item in user_cart:
        cart_items.append({
            'id': item.id,
            'user_id': item.user_id,
            'product_id': item.product_id,
            'quantity': item.quantity
        })
    return jsonify(cart_items)

# Endpoint to add items to a cart, communicating with the Product Service
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)  # Default to adding 1 item

    # Make an HTTP GET request to the Product Service to fetch product details
    product_response = requests.get(f'https://product-service-c4f6.onrender.com/products/{product_id}')

    if product_response.status_code == 200:
        product_data = product_response.json()
        
        # Check if the product is available in sufficient quantity
        if product_data['quantity'] >= quantity:
            # Product is available, add it to the user's cart
            new_cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_cart_item)
            db.session.commit()
            return jsonify({'message': 'Product added to cart'}), 200
        else:
            return jsonify({'message': 'Product quantity is insufficient'}), 400
    else:
        return jsonify({'message': 'Product not found'}), 404

# Endpoint to remove item(s) from a cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)  # Default to removing 1 item

    # Implement logic to remove the product from the user's cart
    cart_item_to_remove = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item_to_remove:
        if cart_item_to_remove.quantity > quantity:
            cart_item_to_remove.quantity -= quantity
        else:
            db.session.delete(cart_item_to_remove)
        db.session.commit()
        return jsonify({'message': 'Product removed from cart'}), 200
    return jsonify({'message': 'Product not found in cart'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
