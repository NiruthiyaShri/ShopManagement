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
	city = db.Column(db.String(20))
	email = db.Column(db.String(50),unique=True)
	ph_no = db.Column(db.String(10))


@app.route('/customers')
def customers():
	# if not Signup.is_authenticated:
	# 	return render_template('login.html')
	# else:
	# 	return render_template('customers.html',username=current_user.username)
	 return render_template('customers.html')
	#email=current_user.email
	
@app.route('/',methods=['POST','GET'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		address = request.form.get('address')
		city = request.form.get('city')
		email = request.form.get('email')
		ph_no = request.form.get('ph_no')
		#print(username,password)
		user = Signup.query.filter_by(email=email).first()
		if user:
			flash("email already exists")
			return render_template('index.html')
		encpassword = generate_password_hash(password)
		new_user = db.engine.execute(f"INSERT INTO `signup` (`username`,`password`,`address`,`city`,`email`,`ph_no`) VALUES ('{username}','{encpassword}','{address}','{city}','{email}','{ph_no}')")
		flash("Thanks for registering! please login")
	return render_template('index.html')


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
            return redirect(url_for('customers'))
        else:
            flash("invalid credentials","danger")
            return render_template('index.html')    

    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('successfully logged out!')
	return redirect(url_for('login'))

app.run(debug=True)