from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)

# Get the Product Service URL from the environment variable
product_service_url = os.environ.get(https://product-service-c4f6.onrender.com)


# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kachowcarts.db'  # SQLite database file name
db = SQLAlchemy(app)

# Define a Cart model
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

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

@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)  # Default to adding 1 item

    # Make an HTTP GET request to the Product Service to fetch product details
    product_response = requests.get(f'{product_service_url}/products/{product_id}')

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
