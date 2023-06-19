from flask import *
from DbConnection import get_sql_connection
import mysql.connector
import json
import customers
import products
import units
import stripe
from datetime import datetime
import ast


publishable_key="pk_test_51NDkvVFxh55otoCcyBoCb71RT1JRWeg66zXK1YiNLklNlkQvxkhrdT5Cbutmr1qiCHNqHLTi2fWJXsWgOTdcIMHZ00yZ4K5ip6"
stripe.api_key = 'sk_test_51NDkvVFxh55otoCcrrUkpUQPdzZVhMIYSKp1TTxZ2xGbDZTzo3HuG2eTvWWxOZQe1XPLhWJo4bAv4OM5BpMDYD5S00sYrYCrwW'

user_id = 2
cart_items=[]
total_price = "0.0"
logged_in = 0

app = Flask(__name__)
app.secret_key = 'Th@run666'
connection = get_sql_connection()

def user_details(email):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customer_details WHERE email = %s", (email,))
    return cursor.fetchone()

def get_products():
    cursor = connection.cursor()
    cursor.execute("select products.product_id, products.product, products.price_per_unit, units.unit_name from products inner join units on products.unit_id=units.unit_id")
    products = cursor.fetchall()
    return products

def customer_orders():
    cursor = connection.cursor()
    cursor.execute("SELECT o.order_id, cd.firstname, cd.lastname, o.total, o.date FROM orders o JOIN customer_details cd ON o.customer_id = cd.cid ORDER BY o.order_id DESC;")
    return cursor.fetchall()

def get_order_details(cid):
    cursor = connection.cursor()
    cursor.execute("SELECT o.order_id, GROUP_CONCAT(p.product SEPARATOR ', ') AS products, o.total, o.date FROM orders o JOIN order_details od ON o.order_id = od.order_id JOIN products p ON od.product_id = p.product_id WHERE o.customer_id = %s GROUP BY o.order_id, o.total, o.date ORDER BY o.order_id DESC;",(cid,))
    orders = cursor.fetchall()
    return orders

def get_product_details(id):
    cursor = connection.cursor()
    cursor.execute("SELECT products.product, order_details.quantity, order_details.total_price FROM order_details join products on order_details.product_id = products.product_id WHERE order_details.order_id = %s",(id,))
    return cursor.fetchall()

def user_details_id(id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM customer_details WHERE cid = %s", (id,))
    return cursor.fetchone()

def get_product_id(name):
    cursor = connection.cursor()
    cursor.execute("SELECT product_id FROM products WHERE product = %s", (name,))
    result = cursor.fetchone()
    return result[0]

def convert_string_to_list(string):
    string = string.replace('[', '').replace(']', '').replace(' ', '')
    dict_strings = string.split('},')
    result = []
    for dict_str in dict_strings:
        if '}' not in dict_str:
            dict_str += '}'
        dictionary = ast.literal_eval(dict_str)
        result.append(dictionary)
    return result


@app.route('/pay', methods=['POST'])
def pay():
    cartlist1 = request.form.get('cartlist')
    cartlist = convert_string_to_list(cartlist1)
    amount = int( request.form.get('amount'))
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer = customer.id,
        description='Shop',
        amount = amount,
        currency='inr',
    )
    cursor = connection.cursor()
    query = ("INSERT INTO orders "
             "(customer_id, total, date)"
             "VALUES (%s, %s, %s)")
    data = (user_id, amount/100, datetime.now())
    cursor.execute(query, data)
    order_id = cursor.lastrowid
    connection.commit()
    cursor = connection.cursor()
    orders_query = ("INSERT INTO order_details "
             "(order_id, product_id, quantity, total_price)"
             "VALUES (%s, %s, %s, %s)")
    orders_data=[]
    for order_detail_record in cartlist:
        orders_data.append([
            order_id,
            int(get_product_id(order_detail_record['name'])),
            int(order_detail_record['quantity']),
            int(order_detail_record['subtotal'])
        ])
    cursor.executemany(orders_query, orders_data)
    connection.commit()
    customer_details = user_details_id(user_id)
    print(customer_details)
    order_details = get_product_details(order_id)
    return render_template('order.html', order_details=order_details,customer_address=customer_details,total_amount = amount/100)

@app.route('/index')
def index():
    user = user_details_id(user_id)
    return redirect(url_for('home',username=user[1],logged_in = logged_in))

@app.route('/mycart',methods=['GET', 'POST'])
def mycart():
    content_type = request.headers.get('Content-Type')
    if content_type and content_type == 'application/json' and request.method == 'POST':
        data = request.json
        global cart_items
        cart_items = data['cart']
    # Calculate total price
        global total_price
        total_price=0
        for item in cart_items:
            subtotal=0
            quantity = int(item['quantity'])
            price = float(item['price'])
            subtotal = quantity*price
            total_price += subtotal
            item['subtotal']=subtotal
        total_price = ("%.2f" % float(total_price))
        return render_template('mycart.html',totalPrice=total_price)  
    if request.method == 'GET':
        return render_template('mycart.html', cartItems=cart_items, totalPrice=total_price)

@app.route('/')
def home():
    username = request.args.get('username')
    cursor = connection.cursor()
    cursor.execute("select products.product_id, products.product, products.price_per_unit, units.unit_name from products inner join units on products.unit_id=units.unit_id")
    products = cursor.fetchall()
    cursor.close()
    print(logged_in)
    return render_template('index.html', username=username,products=products, logged_in = logged_in)

@app.route('/admin')
def admin():
    orders_placed = customer_orders()
    return render_template('admin.html',customer_orders = orders_placed)

@app.route('/manageproduct')
def manageproduct():
    return render_template('manage-product.html')

@app.route('/order')
def order():
    return render_template('order.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html' )
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'admin@gmail.com' and password == 'admin':
            return redirect(url_for('admin'))
        user = user_details(email)
        if user and user[4] == password:
            flash('Login successful!', 'success')
            global user_id
            user_id = user[0]
            global logged_in
            logged_in = 1
            return redirect(url_for('home',username=user[1],logged_in = logged_in))
        else:
            # Wrong email or password
            flash('Wrong email or password!', 'error')
    
    return render_template('login.html')


@app.route('/profile')
def profile():
    user = user_details_id(user_id)
    orders = get_order_details(user[0])
    return render_template('profile.html', firstname=user[1], lastname=user[2],email=user[3],address=user[5], city=user[6], state=user[7],zipcode=user[8], country=user[9], phone=user[10], orders = orders)


@app.route('/logout')
def logout():
    global logged_in
    logged_in = 0
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home', logged_in = logged_in))


@app.route('/insertCustomer', methods=['POST'])
def insert_customer(request_payload):
    cid = customers.insert_new_customer(connection, request_payload)
    response = jsonify({
        'cid': cid
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/register',methods=['POST','GET'])   
def register():
    if request.method == 'GET':
        return render_template('register.html')  
    elif request.method == 'POST':
        a={}
        a['firstname'] = request.form['firstName']
        a['lastname'] = request.form['lastName']
        a['email'] = request.form['email']
        a['password'] = request.form['password']
        a['address'] = request.form['address']
        a['city'] = request.form['city']
        a['state'] = request.form['state']        
        a['zipcode'] = request.form['zipcode']
        a['country'] = request.form['country']
        a['phone'] = request.form['phone']
        insert_customer(a)
        flash("Registration Successful!!!")
        return redirect('/login')


@app.route('/getProducts', methods=['GET'])
def get_products():
    response = products.get_all_products(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
@app.route('/getUnits', methods=['GET'])
def get_unit():
    response = units.get_units(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = json.loads(request.form['data'])
    product_id = products.insert_new_product(connection, request_payload)
    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/insertOrder',methods=['POST'])
def insert_order():
    request_payload = json.loads(request.form['data'])
    product_id = products.insert_new_product(connection, request_payload)
    response = jsonify({
        'product_id': product_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    return_id = products.delete_product(connection, request.form['product_id'])
    response = jsonify({
        'product_id': return_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/update_product', methods=['POST'])
def update_product():
    data = request.get_json()
    # Handle the updated product details
    name = data['name']
    price = float(data['price'])
    cursor = connection.cursor()
    cursor.execute("UPDATE products SET price_per_unit = %s WHERE product = %s",(price, name,))
    connection.commit()
    return jsonify(success=True)



if __name__ == '__main__':
    app.run(debug=True)
