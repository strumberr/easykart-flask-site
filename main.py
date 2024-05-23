from flask import Flask, render_template, request, redirect, url_for, flash
from components.database import *
# import component as db
# todo: sdsd
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import bcrypt
from dotenv import load_dotenv


load_dotenv()


DEVELOPMENT_ENV = True

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_KEY")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

database_handler = Users()


class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    
@login_manager.user_loader
def load_user(user_id):
    user_data = database_handler.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['email'])
    return None



@app.route("/")
def index():
    top_20_all = get_top_20_best_all_categories()
    
    print(top_20_all)
    
    return render_template("index.html", top_20_all=top_20_all)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        easykart_username = request.form.get('easykart_username')
        

        database_handler.create_user(email, password, username, easykart_username)
        flash("Account created successfully", "success")
        
        return redirect(url_for('login'))
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        
        email = request.form.get('email')
        password = request.form.get('password')
        user_data = database_handler.get_user_by_email(email)
        
        if user_data and database_handler.authenticate_user(email, password):
            
            user = User(user_data['id'], user_data['email'])
            
            
            login_user(user)
            
            return redirect(url_for('index'))
        else:
            flash("Login failed. Check your email and password", "danger")
    return render_template("login.html")


@app.route("/search", methods=["GET"])
def search():
    username = request.args.get('username')

    if username is None:
        return render_template("searchUsername.html")
    else:
        similar_usernames = search_all_similar_usernames(username)

    return render_template("searchUsername.html", stats_username=similar_usernames, username=username)


@app.route("/user", methods=["GET"])
def user():
    username = request.args.get('username')

    # stats_username = get_all_stats_username(username)
    
    stats_username = detailedUserStats(username)
    
    print(stats_username)
    
    return render_template("user.html", stats_username=stats_username, username=username)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # get the username from the current user
    user_email = current_user.email
    username = database_handler.get_user_by_email(user_email)['username_easykart']
    
    print(username)
    
    # stats_username = get_all_stats_username(username)
    
    stats_username = detailedUserStats(username)
    
    print(stats_username)
    
    return render_template("dashboard.html", stats_username=stats_username, username=username)






@app.route("/api/getBestScore", methods=["POST"])
def getBestScore():
    
    if request.method == "POST":
        username = request.json.get('username')
        category = request.json.get('category')
        
        data = getBestScoreUsername(username, category)
    else:
        data = None

        
    return {"stats": data}


@app.route("/api/detailedUserStats", methods=["POST"])
def detailedUserStatsRoute():
    
    if request.method == "POST":
        username = request.json.get('username')
        
        
        data = detailedUserStats(username)
    else:
        data = None

        
    return {"stats": data}


@app.route("/api/easykart_username_search", methods=["POST"])
def all_usernames():
    
    if request.method == "POST":
        username = request.json.get('username')
        
        if username is None:
            return {"stats": "Username is required"}
        
        
        data = database_handler.get_all_easykart_users(username)
    else:
        data = None

        
    return {"stats": data}





if __name__ == "__main__":
    app.run(debug=True)