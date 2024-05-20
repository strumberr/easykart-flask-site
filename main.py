from flask import Flask, render_template, request
from components.database import *


DEVELOPMENT_ENV = True

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


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
    
    stats_username = get_all_stats_username(username)
    
    detailed_stats = detailedUserStats(username)
    
    # print(detailed_stats)
    
    return render_template("user.html", stats_username=stats_username, username=username)


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





if __name__ == "__main__":
    app.run(debug=True)