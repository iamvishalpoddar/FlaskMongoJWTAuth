from flask import Flask, render_template, request, redirect, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import pymongo
from datetime import timedelta
import hashlib

#mongoDB connection
connection_string = f"mongodb+srv://iamvishalpoddar:Vip012345@cluster0.mpgci.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(connection_string)
new_database = client["db"]
new_collection = new_database["users"]

app = Flask(__name__)
jwt = JWTManager(app)

# Configuration
app.config["JWT_SECRET_KEY"] = "supersecret"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

users = new_collection.db.users

# Helpers
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users.find_one({"username": username}):
            return "User already exists", 400

        users.insert_one({
            "username": username,
            "password": hash_password(password)
        })
        return redirect('/login')

    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.find_one({"username": username})

        if user and user["password"] == hash_password(password):
            token = create_access_token(identity=username)
            response = redirect('/protected')
            set_access_cookies(response, token)
            return response
        return "Invalid credentials", 401

    return render_template("login.html")

@app.route('/protected')
@jwt_required(locations=['cookies'])
def protected():
    user = get_jwt_identity()
    return f"Hello, {user}. You are authenticated!"

if __name__ == '__main__':
    app.run(debug=True)
