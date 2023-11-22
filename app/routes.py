from app import app
from flask import render_template, request, redirect, url_for, flash, jsonify
from .models import Cart, User, Product
from flask_login import current_user, login_required, login_user
from .auth.forms import AddProductForm, MakeAdminForm
from .apiauthhelper import basic_auth_required, token_auth_required
from werkzeug.security import check_password_hash

@app.route('/', methods=["GET", "POST"])
def base():
    return render_template('base.html')

@app.route('/<int:product_id>', methods=["GET"])
def getproduct(product_id):
    product = product.query.get(product_id)
    return render_template('singleproduct.html', product=product)

@login_required
@app.route("/cart")
def cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    product = []
    final_total = 0
    for item in cart_items:
        product = product.query.get(item.product_id)
        product.quantity = item.quantity
        final_total += product.price *product.quantity
        product.append(product)
    return render_template('cart.html', cart=product, final_total = final_total)


@app.route('/<int:product_id>/add_to_cart', methods=["POST", "GET"])
def add_to_cart(product_id):

    if current_user.is_authenticated:
        user_id = current_user.id
        cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()
        if cart_item:
            cart_item.quantity += 1
            cart_item.saveToDB()
        else:
            cart = Cart(product_id=product_id, user_id=user_id, quantity=1)
            cart.saveToDB()
    else:
        flash('You need to log in to add items to your cart', category='danger')
        return redirect(url_for('auth.loginPage'))
    return redirect(url_for('cart'))

@app.route('/cart/<int:product_id>/remove', methods=["POST", "GET"])
def remove_from_cart(product_id):
    user_id = current_user.id
    cart_item = Cart.query.filter_by(product_id=product_id, user_id=user_id).first()

    if not cart_item:
        return redirect(url_for('cart'))

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.saveToDB()
    else:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=["POST", "GET"])
def clear_cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    for cart_item in cart_items:
        cart_item.deleteFromDB()

    return redirect(url_for('cart'))

@app.route("/<int:product_id>/delete", methods=["POST", "GET"])
def deleteproduct(product_id):
    product = Product.query.get(product_id)

    product.deleteFromDB()
    return redirect(url_for('product'))

# Update your route for adding a product
@app.route("/addproducts", methods=["POST", "GET"])
def addproduct():
    if current_user.is_authenticated:
        if current_user.admin == True:
            form2 = MakeAdminForm()
            form = AddProductForm()
            products = Product.query.all()  # Update to use Product model
            if request.method == "POST":
                
                if form.submit.data and form.validate():
                    
                    title = form.title.data
                    img_url = form.img_url.data
                    caption = form.caption.data
                    price = form.price.data
                    quantity = form.quantity.data
                    
                    product = Product(title, img_url, caption, price, quantity)  # Update to use Product model
                    product.saveToDB()
                    
                    flash("Successfully Added product to Database!", category='success')
                    return render_template('addproducts.html', form = form, products = products, form2 = form2)
                
                elif form2.submitadmin.data and form2.validate():
                    
                    username = form2.username.data
                    return render_template('makeadmin.html', username = username)
                else:
                    flash("Form didn't pass validation.", category='danger')
                    return render_template('addproducts.html', form = form, products = products, form2 = form2)
                
            elif request.method == "GET":
                return render_template('addproducts.html', form = form, products = products, form2 = form2)
        else:
            return redirect(url_for('products'))
    else:
        return redirect(url_for('products'))
            
@app.route("/makeadmin/<username>", methods=["POST", "GET"])
def MakeAdmin(username):
    
    user = User.query.filter_by(username=username).first()
    user.makeAdmin()
    
    return redirect(url_for('addproduct'))

@app.route("/makeadmin/", methods=["POST", "GET"])
def MakeAdminPage():
    
    return render_template('makeadmin.html')

@app.route('/meanproductsapi', methods=["GET", "POST"])
def meanproductsapi():
    products = Product.query.all()
    return jsonify([m.to_dict() for m in products])

@app.route('/meanproductsapi/signup', methods=["GET", "POST"])
def signUpPage():
    data = request.json
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    # add user to database
    user = User(username, email, password)

    user.saveToDB()

    return {
        "response": "ok",
        "message": "Successfully signed up maybe"
    }

@app.route('/meanproductsapi/signin', methods=["GET", "POST"])
def signInPage():
    data = request.json
    
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    if user:
        #if user exists, check if passwords match
        if check_password_hash(user.password, password):
                   
            return {
                "response": "ok",
                "message": "Successfully signed in maybe",
                "user": user.to_dict()
            }

        else:
            return {
                'status': 'not ok',
                'message': 'wrong password'
            }

    else:
        return {
                'status': 'not ok',
                'message': 'user does not exist'
            }