# ---------------------------------------------------------------- IMPORTS ----------------------------------------------------------------------------------- #

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
import matplotlib.pyplot as plt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import random
import datetime

# from forms import AddProducts



# ---------------------------------------------------------------- APP INTIALIZATION ----------------------------------------------------------------------------------- #

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tracker.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


# ---------------------------------------------------------------- DATABASE MODEL CLASSES ----------------------------------------------------------------------------------- #
# class User(db.Model, UserMixin):
#     __tablename__ = 'user'
#     user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String, nullable=False, unique=True)
#     password = db.Column(db.String, nullable=False)
#     trackers = db.relationship("Tracker")

#     def get_id(self):
#         return self.user_id
    
# class Tracker(db.Model):
#     __tablename__ = 'tracker'
#     tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
#     tracker_name = db.Column(db.String, nullable=False)
#     description = db.Column(db.String, nullable=False)
#     tracker_type = db.Column(db.String, nullable=False)
#     options = db.Column(db.String, nullable=True, default=None)
#     logs = db.relationship('Log')
#     # settings = db.relationship('Setting', uselist=False)

    

# class Log(db.Model):
#     __tablename__ = 'logger'
#     logger_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable=False)
#     log_value = db.Column(db.String, nullable=False)
#     comments = db.Column(db.String, nullable=True)
#     timestamp = db.Column(db.String, nullable=False, default=datetime.now())
#Grocery 


from datetime import datetime

# User model
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # Define a relationship to the sections managed by the user (store manager)
    # sections_managed = db.relationship('Section', backref='manager', lazy=True)
    # Define a relationship to the purchases made by the user
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)

    def get_id(self):
        return str(self.user_id)

# # Section model
# class Section(db.Model):
#     __tablename__ = 'section'
#     section_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     section_name = db.Column(db.String, nullable=False)
#     manager_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
#     # Define a relationship to categories in this section
#     categories = db.relationship('Category', backref='section', lazy=True)

# Category model
class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String, nullable=False)
    # section_id = db.Column(db.Integer, db.ForeignKey('section.section_id'), nullable=False)
    # Define a relationship to products in this category
    # products = db.relationship('Product', backref='category', lazy=True)

# Product model
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String, nullable=False)
    manufacture_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    rate_per_unit = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Purchase model
class Purchase(db.Model):
    __tablename__ = 'purchase'
    purchase_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# ShoppingList model
class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    user = db.relationship('User', backref=db.backref('shopping_lists', lazy=True))

# ProductCategory model
class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)



# Create the database tables
with app.app_context():
    db.create_all()
# Flask Admin
admin = Admin(app, name='Grocery Store Admin', template_mode='bootstrap3')

# Add your models to Flask-Admin
admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Section, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Purchase, db.session))
# admin.add_view(ModelView(Inventory, db.session))
admin.add_view(ModelView(ShoppingList, db.session))
admin.add_view(ModelView(ProductCategory, db.session))


# ---------------------------------------------------------------- LOGIN REQUIRED----------------------------------------------------------------------------------- #

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/logout', methods=['GET', 'POST'])
# @login_required
def logout():
    # logout_user()
    return render_template('welcome.html')
    
    # ---------------------------------------------------------------- LOGIN AUTHENTICATION----------------------------------------------------------------------------------- #

@app.route('/', methods=['GET', 'POST'])
def login_validation():
    global check1
    try:
        if request.method=='GET':
            return render_template('welcome.html')
        else:
            
            usr = request.form.get('username')
            pasw = request.form.get('password')
            check1 = User.query.filter_by(username=usr).first()
            check2 = User.query.filter_by(password=pasw).first()
            # print(check1.is_admin)
            # print(check2.user_id)
            
            if (usr=='') or (pasw==''):

                return render_template('welcome.html', error=1)
            else:
                if check1.user_id==check2.user_id:
                    # print("here")
                    response=login_user(check1, remember=True)
                    print(response)
                    if response['is_admin']==True:
                        return redirect(f'/AdminDashboard/{check1.user_id}')
                    else:
                        return redirect(f'/dashboard/{check1.user_id}')
                else:
                    return render_template('welcome.html', error=1)
    except Exception as e:
        print(e)
        return render_template('welcome.html', error=1)

@app.route('/AdminDashboard/<int:uid>', methods=['GET', 'POST'])
def AdminDashboard(uid):
    # if request.method == 'GET':
        # Retrieve user information and shopping lists
    user = User.query.get(uid)
    products = Product.query.all()
    categories = Category.query.all()
    print(categories)

    return render_template('AdminDashboard.html', user=user, categories=categories,products=products)

# ----------------------------------------------------------------REGISTRATION----------------------------------------------------------------------------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method=='GET':
            return render_template('register.html')
        if request.method=='POST':
            name = request.form.get('uname')
            pswrd = request.form.get('upass')
            existing_user = User.query.filter_by(username=name).first()
            if existing_user is not None:
                return render_template('register.html', error=1)
            else:
                if name=='admin':
                    new_user = User(username=name, password=pswrd,is_admin=True)
                    db.session.add(new_user)
                    db.session.commit()

                else:
                    new_user = User(username=name, password=pswrd)
                    db.session.add(new_user)
                    db.session.commit()

    except:
        print("error")
        return render_template('register.html', error=1)

    return redirect('/')
@app.route('/add_shopping_list', methods=['GET', 'POST'])
def add_shopping_list():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            pd_id = request.form.get('pd_id')
            uid = request.form.get('uid')
            quantity = request.form.get('quantity')
            # pswrd = request.form.get('upass')
            # existing_user = User.query.filter_by(username=name).first()
            # if existing_user is not None:
            #     return render_template('register.html', error=1)
            # else:
            new_list = ShoppingList(user_id=uid,quantity=quantity,product_id=pd_id)
            db.session.add(new_list)
            print(new_list)
            db.session.commit()
            print("here")
    except:
        print("error")
        return render_template('register.html', error=1)

    return redirect(f'/dashboard/{uid}')

# ---------------------------------------------------------------- DASHBOARD ----------------------------------------------------------------------------------- #

# @app.route('/dashboard/<int:uid>', methods=['GET', 'POST'])
# @login_required
# def dashboard(uid):
#     if request.method=='GET':
#         trackers=User.query.filter_by(user_id=uid).first()
#         return render_template('home.html', c=trackers, trackers=trackers.trackers)


@app.route('/dashboard/<int:uid>', methods=['GET', 'POST'])
# @login_required
def dashboard(uid):
    if request.method == 'GET':
        # Retrieve user information and shopping lists
        user = User.query.get(uid)
        shopping_lists = ShoppingList.query.filter_by(user_id=uid).all()
        products = Product.query.all()
        total=0
        # if not shopping_lists:
        #     return render_template('home.html', user=user, shopping_lists=shopping_lists, products=products,total=total)
        for pr in shopping_lists:
            for product in products:
                if product.product_id == pr.product_id:
                    # print(product.rate_per_unit,pr.quantity,type(product.rate_per_unit),type(pr.quantity))
                    total+=int(product.rate_per_unit * int(pr.quantity) if  pr.quantity else 0)
        print(total)

        print(User.is_admin)
        ll=[]

        return render_template('home.html', user=user, shopping_lists=shopping_lists, products=products,total=total,is_search=False,search_list=ll)
        #return render_template('home.html', user=user)
# addProducts route
# @app.route('/add_product_list',methods=['GET','POST'])
# def add_product_list():
#     # User.is_admin=True
#     # if User.is_admin==True:
#     #        return render_template("addProducts.html",title="Add Products")
#     # form=AddProducts()
#     # return render_template("addProducts.html",title="Add Products",form=form)
#     try:
#         # if request.method=='GET':
#         #     return render_template('register.html')
#         if request.method=='POST':
#             name = request.form.get('list_name')
#             user = request.form.get('uid')
#             print(user)
#             # pswrd = request.form.get('upass')
#             # existing_user = User.query.filter_by(username=name).first()
#             # if existing_user is not None:
#             #     return render_template('register.html', error=1)
#             # else:
#             new_list = Category(category_name=name)
#             db.session.add(new_list)
#             # print(new_list)
#             db.session.commit()
#             # print("here")
#     except Exception as e:
#         print(e)
#         return redirect(f'/AdminDashboard/{user}')

#     return redirect(f'/AdminDashboard/{user}')


@app.route('/add_product_list', methods=['GET', 'POST'])
def add_product_list():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            name = request.form.get('list_name')
            user = request.form.get('uid')
            check1 = Category.query.filter_by(category_name=request.form.get('product')).first()
            # pswrd = request.form.get('upass')
            # existing_user = User.query.filter_by(username=name).first()
            # if existing_user is not None:
            #     return render_template('register.html', error=1)
            # else:
            print(check1.category_id)

            new_list = Product(stock=random.randint(1,100),category_id=check1.category_id,    rate_per_unit=random.randint(1,50) ,    expiry_date=datetime.today() ,manufacture_date=datetime.today(),    product_name=name )
            db.session.add(new_list)
            # print(new_list)
            db.session.commit()
            # print("here")
    except Exception as e:
        print(e)
        return redirect(f'/AdminDashboard/{user}')

    return redirect(f'/AdminDashboard/{user}')

@app.route('/edit_product', methods=['GET', 'POST'])
def edit_product():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            imp_uid = request.form.get('pid')
            imp_value = request.form.get('value')
            imp_feild = request.form.get('feild')
            user = request.form.get('uid')
            print(imp_value)

            product = Product.query.filter_by(product_id=imp_uid).first()
            if imp_feild=='rate_per_unit':
                print("here")
                product.rate_per_unit = int(imp_value)
                db.session.commit()
            else:
                product.product_name = imp_value
                db.session.commit()
            # print("here")
    except Exception as e:
        print(e)
        return redirect(f'/AdminDashboard/{user}')

    return redirect(f'/AdminDashboard/{user}')

@app.route('/add_category_list', methods=['GET', 'POST'])
def add_category_list():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            name = request.form.get('list_name')
            user = request.form.get('uid')
            # check1 = Category.query.filter_by(category_name=request.form.get('product')).first()
            # pswrd = request.form.get('upass')
            # existing_user = User.query.filter_by(username=name).first()
            # if existing_user is not None:
            #     return render_template('register.html', error=1)
            # else:
            # print(check1.category_id)

            new_list = Category(category_name=name )
            db.session.add(new_list)
            # print(new_list)
            db.session.commit()
            # print("here")
    except Exception as e:
        print(e)
        return redirect(f'/AdminDashboard/{user}')

    return redirect(f'/AdminDashboard/{user}')

@app.route('/delete_category', methods=['GET', 'POST'])
def delete_category():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            # name = request.form.get('list_name')
            uid = request.form.get('uid')
            user = request.form.get('user')
            # check1 = Category.query.filter_by(category_name=request.form.get('product')).first()
            # pswrd = request.form.get('upass')
            # existing_user = User.query.filter_by(username=name).first()
            # if existing_user is not None:
            #     return render_template('register.html', error=1)
            # else:
            # print(check1.category_id)

            # new_list = Product(stock=random.randint(1,100),category_id=check1.category_id,    rate_per_unit=random.randint(1,50) ,    expiry_date=datetime.today() ,manufacture_date=datetime.today(),    product_name=name )
            # db.session.add(new_list)
            # db.de
            # print(new_list)
            Category.query.filter_by(category_id=uid).delete()
            db.session.commit()
            # print("here")
    except Exception as e:
        print(e)
        return redirect(f'/AdminDashboard/{user}')

    return redirect(f'/AdminDashboard/{user}')


@app.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            # name = request.form.get('list_name')
            uid = request.form.get('uid')
            user = request.form.get('user')
            # check1 = Category.query.filter_by(category_name=request.form.get('product')).first()
            # pswrd = request.form.get('upass')
            # existing_user = User.query.filter_by(username=name).first()
            # if existing_user is not None:
            #     return render_template('register.html', error=1)
            # else:
            # print(check1.category_id)

            # new_list = Product(stock=random.randint(1,100),category_id=check1.category_id,    rate_per_unit=random.randint(1,50) ,    expiry_date=datetime.today() ,manufacture_date=datetime.today(),    product_name=name )
            # db.session.add(new_list)
            # db.de
            # print(new_list)
            Product.query.filter_by(product_id=uid).delete()
            db.session.commit()
            # print("here")
    except Exception as e:
        print(e)
        return redirect(f'/AdminDashboard/{user}')

    return redirect(f'/AdminDashboard/{user}')

@app.route('/search', methods=['GET','POST'])
def search():
    try:
        # if request.method=='GET':
        #     return render_template('register.html')
        if request.method=='POST':
            # name = request.form.get('list_name')
            search = request.form.get('search')
            # print(search)
            products=Product.query.all()
            user = request.form.get('uid')
            # print("value"+ str(user))
            shopping_lists = ShoppingList.query.filter_by(user_id=user).all()
            products = Product.query.all()
            total=0
            # if not shopping_lists:
            #     return render_template('home.html', user=user, shopping_lists=shopping_lists, products=products,total=total)
            for pr in shopping_lists:
                for product in products:
                    if product.product_id == pr.product_id:
                        # print(product.rate_per_unit,pr.quantity,type(product.rate_per_unit),type(pr.quantity))
                        total+=int(product.rate_per_unit * int(pr.quantity) if  pr.quantity else 0)
            print(type(products))

            ll=[]
            for product in products:
                if product.product_name.startswith(search):
                    
                    ll.append(product)

            # db.session.commit()
            # print("here")
            print(len(ll))
    except Exception as e:
        print(e)
        return redirect(f'/Dashboard/{user}')

    return render_template('home.html', user=user, shopping_lists=shopping_lists, products=products,total=total,is_search=True,search_list=ll)


# @app.route('/buy', methods=['GET', 'POST'])
# def buy():
#     try:
#         # if request.method=='GET':
#         #     return render_template('register.html')
#         if request.method=='POST':
#             # name = request.form.get('list_name')
#             uid = request.form.get('total')
#             # user = request.form.get('user')
#             # check1 = Category.query.filter_by(category_name=request.form.get('product')).first()
#             # pswrd = request.form.get('upass')
#             # existing_user = User.query.filter_by(username=name).first()
#             # if existing_user is not None:
#             #     return render_template('register.html', error=1)
#             # else:
#             # print(check1.category_id)

#             # new_list = Product(stock=random.randint(1,100),category_id=check1.category_id,    rate_per_unit=random.randint(1,50) ,    expiry_date=datetime.today() ,manufacture_date=datetime.today(),    product_name=name )
#             # db.session.add(new_list)
#             # db.de
#             # print(new_list)
#             # Product.query.filter_by(product_id=uid).delete()
#             # db.session.commit()
#             # print("here")
#             alert
#     except Exception as e:
#         print(e)
#         return redirect(f'/AdminDashboard/{user}')

    # return redirect(f'/AdminDashboard/{user}')














#------------------------------------------ RUNNING THE APP ----------------------------------------------------------------------------------- #




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


