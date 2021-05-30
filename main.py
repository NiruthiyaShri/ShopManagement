from flask import Flask,flash,render_template,request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
#db connection
local_server = True
app = Flask(__name__)
app.secret_key = "athirai"

login_manager = LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
	return Signup.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#db model
class Signup(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20),unique=True)
	password = db.Column(db.String(100))
	address = db.Column(db.String(50))
	email = db.Column(db.String(50),unique=True)
	ph_no = db.Column(db.String(10))


class Admin(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20),unique=True)
	password = db.Column(db.String(100))

class Products(UserMixin,db.Model):
	p_id=db.Column(db.Integer,primary_key=True)
	p_name = db.Column(db.String(20),unique=True)
	quantity = db.Column(db.String(100))
	cost_price=db.Column(db.String(100))
	selling_price=db.Column(db.String(100))

class Orders(UserMixin,db.Model):
	o_id=db.Column(db.Integer,primary_key=True)
	p_id=db.Column(db.Integer)
	o_name=db.Column(db.String(50))
	email = db.Column(db.String(50))
	quantity = db.Column(db.String(100))
	cost=db.Column(db.String(100))
	status=db.Column(db.String(100))

class Expenses(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	o_id=db.Column(db.Integer)
	p_id=db.Column(db.Integer)
	cost_price=db.Column(db.String(10))
	selling_price=db.Column(db.String(10))
	profit=db.Column(db.String(10))

#customers home page
# @app.route('/customers')
# @login_required
# def customers():
#     return render_template('customers.html')

#updating users details
@app.route("/update/<string:id>",methods=['POST','GET'])
@login_required
def update(id):
	posts=Signup.query.filter_by(id=id).first()
	if request.method=="POST":
		username = request.form.get('username')
		address = request.form.get('address')
		email = request.form.get('email')
		ph_no = request.form.get('ph_no')
		db.engine.execute(f"UPDATE `signup` SET `username` = '{username}', `address` = '{address}', `email` = '{email}', `ph_no` = '{ph_no}'  WHERE `signup`.`id` = {id}")
		flash("Details changed successfully","success")
		return redirect('/personal-info')

#displaying user's info
@app.route('/personal-info')
@login_required
def personal_info():
	# if not Signup.is_authenticated:
	# 	return render_template('login.html')
	# else:
	# 	return render_template('customers.html',username=current_user.username)
    em=current_user.email
    query=db.engine.execute(f"SELECT *FROM `signup` WHERE email='{em}'")
    return render_template('personal-info.html',query=query)
	#email=current_user.email

#login function for admin
@app.route('/admin',methods=['POST','GET'])
def admin():
	if request.method == "POST":
		username=request.form.get('username')
		password=request.form.get('password')
		user=Admin.query.filter_by(username=username).first()

		if user and user.password==password:
			login_user(user)
			flash('Login Success!','blue')
			#return redirect(url_for('https://www.google.com/'))
			return render_template('admin.html')
		else:
			flash("invalid credentials","danger")
			return render_template('index.html')    

	return render_template('index.html')

#signup for user
@app.route('/',methods=['POST','GET'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		address = request.form.get('address')
		email = request.form.get('email')
		ph_no = request.form.get('ph_no')
		#print(username,password)
		user = Signup.query.filter_by(email=email).first()
		if user:
			flash("email already exists")
			return render_template('index.html')
		encpassword = generate_password_hash(password)
		new_user = db.engine.execute(f"INSERT INTO `signup` (`username`,`password`,`address`,`email`,`ph_no`) VALUES ('{username}','{encpassword}','{address}','{email}','{ph_no}')")
		flash("Thanks for registering! please login")
	return render_template('index.html')

#login function for user
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Signup.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash('Login Success!','primary')
            #return redirect(url_for('https://www.google.com/'))
            return redirect('/personal-info')
        else:
            flash("invalid credentials","danger")
            return render_template('index.html')    

    return render_template('index.html')

#function for entering products
@app.route('/product-details',methods=['POST','GET'])
def product_details():
	if request.method == 'POST':
		p_id = request.form.get('p_id')
		p_name = request.form.get('p_name')
		quantity = request.form.get('quantity')
		cost_price = request.form.get('cost_price')
		selling_price = request.form.get('selling_price')
		user = Products.query.filter_by(p_id=p_id).first()
		if user:
			flash("product already exists..so update the quantity")
			return render_template('admin.html')
		new_user = db.engine.execute(f"INSERT INTO `products` (`p_id`,`p_name`,`quantity`,`cost_price`,`selling_price`) VALUES ('{p_id}','{p_name}','{quantity}','{cost_price}','{selling_price}')")
		flash("product successfully entered!")
	return render_template('admin.html')

#function for displaying products
@app.route('/products',methods=['POST','GET'])
def products():
	if Admin.is_authenticated:
		query=db.engine.execute("SELECT * FROM `products`")
		return render_template('products.html',query=query)

#function for editing products	
@app.route("/edit/<string:p_id>",methods=['POST','GET'])
def update_products(p_id):
	posts=Products.query.filter_by(p_id=p_id).first()
	if request.method=="POST":
		p_id = request.form.get('p_id')
		p_name = request.form.get('p_name')
		quantity = request.form.get('quantity')
		cost_price = request.form.get('cost_price')
		selling_price = request.form.get('selling_price')
		db.engine.execute(f"UPDATE `products` SET `p_id` = '{p_id}', `p_name` = '{p_name}', `quantity` = '{quantity}', `cost_price` = '{cost_price}', `selling_price` = '{selling_price}'  WHERE `products`.`p_id` = {p_id}")
		flash("Details changed successfully","success")
		return redirect('/products')
	return render_template('edit.html',posts=posts)

#function for inserting orders
@app.route('/orders-customers',methods=['POST','GET'])
@login_required
def orderscust():
	flag = 0
	if request.method == 'POST':
		o_name = request.form.get('o_name')
		em=current_user.email
		email = em
		quantity = request.form.get('quantity')
		p_id=request.form.get('p_id')
		status="not delivered"
		query=db.engine.execute(f"SELECT * FROM `products` WHERE `products`.`p_id`='{p_id}'")
		for post in query:
			cost = str(int(quantity) * post.selling_price)
			if int(quantity)>int(post.quantity):
				flag = 1
		if(flag):
			flash('Items not in stock') 
			return render_template('orders-customers.html')
		user = Products.query.filter_by(p_id=p_id).first()
		if user:
			new_user = db.engine.execute(f"INSERT INTO `orders` (`o_name`,`email`,`quantity`,`p_id`,`cost`,`status`) VALUES ('{o_name}','{email}','{quantity}','{p_id}','{cost}','{status}')")
			flash("Order Placed")
		else:
			flash('product does not exist!')
		return render_template('orders-customers.html')
	return render_template('orders-customers.html')

#function for deleting product
@app.route("/delete/<string:p_id>",methods=['POST','GET'])
def delete(p_id):
    db.engine.execute(f"DELETE FROM `products` WHERE `products`.`p_id`={p_id}")
    flash("Product Deleted Successful","danger")
    return redirect('/products')

#function for accepting order	
@app.route("/accept/<string:o_id>",methods=['POST','GET'])
def accept_order(o_id):
	posts=Orders.query.filter_by(o_id=o_id).first()
	status = "delivered"
	db.engine.execute(f"UPDATE `orders` SET `status` = '{status}'  WHERE `orders`.`o_id` = {o_id}")
	flash("Order Accepted and is out for delivery","success")
	expenses(o_id)
	return redirect('/orders')
	#return render_template('orders.html')

#function for deleting order
@app.route("/delete-order/<string:o_id>",methods=['POST','GET'])
def delete_order(o_id):
    db.engine.execute(f"DELETE FROM `orders` WHERE `orders`.`o_id`={o_id}")
    flash("Order Deleted Successful","danger")
    return redirect('/orders')


#order page
@app.route('/orders',methods=['POST','GET'])
def orders():
	if Admin.is_authenticated:
		query=db.engine.execute("SELECT * FROM `orders`")
		return render_template('orders.html',query=query)
	#return render_template('orders.html')

def expenses(o_id):
	print('working')
	query=db.engine.execute(f"SELECT * FROM `orders` WHERE `orders`.`o_id`={o_id} ")
	for post in query:
		o_id = post.o_id
		p_id = post.p_id
		quan = post.quantity
	query2=db.engine.execute(f"SELECT * FROM `products` WHERE `products`.`p_id`={p_id}")
	for post in query2:
		selling_price = post.selling_price
		cost_price = post.cost_price
		profit = str(int(selling_price)-int(cost_price))
	db.engine.execute(f"INSERT INTO `expenses` (`o_id`, `p_id`, `cost_price`, `selling_price`, `profit`) VALUES ('{o_id}', '{p_id}', '{cost_price}', '{selling_price}','{profit}');")
	# query1=db.engine.execute("SELECT * FROM `expenses`")
	return redirect('/orders')

@app.route('/expenses',methods=['POST','GET'])
def disp_exp():
	cursor= db.engine.execute("SELECT SUM(profit) AS totalsum FROM `expenses`")
	query=db.engine.execute("SELECT * FROM `expenses`")
	return render_template('expenses.html',query=query,cursor=cursor)

@app.route('/your-orders')
@login_required
def orders_customers():
	em=current_user.email
	email = em
	query=db.engine.execute(f"SELECT * FROM `orders` WHERE `orders`.`email`='{email}' ")
	return render_template('your-orders.html',query=query)

@app.route('/products-user')
@login_required
def products_user():
	query=db.engine.execute("SELECT * FROM `products`")
	return render_template('products-user.html',query=query)

#logout function
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('successfully logged out!')
	return redirect(url_for('login'))

app.run(debug=True)