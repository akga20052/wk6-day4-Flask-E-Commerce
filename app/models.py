from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from secrets import token_hex
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

followers = db.Table('followers', 
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    apitoken = db.Column(db.String(500))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.apitoken = token_hex(16)

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
        
    def makeAdmin(self):
        self.admin = True
        db.session.commit()
        
    def to_dict(self):
        return {"id": self.id, 
                "username": self.username, 
                "email": self.email, 
                "token": self.apitoken
                }

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String, nullable=False)
    caption = db.Column(db.String(1000))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, title, img_url, caption, price, quantity):
        self.title = title
        self.img_url = img_url
        self.caption = caption
        self.price = price
        self.quantity = quantity

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
        
    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {"id": self.id, 
                "title": self.title, 
                "img_url": self.img_url, 
                "caption": self.caption, 
                "price": self.price, 
                "quantity": self.quantity}

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mug_id = db.Column(db.Integer, db.ForeignKey('mugs.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def __init__(self, user_id, mug_id, quantity=1):
        self.user_id = user_id
        self.mug_id = mug_id
        self.quantity = quantity

    def update_quantity(self, quantity):
        self.quantity += quantity
        db.session.commit()

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
        
    like = db.Table('like',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable=False, primary_key=True),
    )