from flask import Flask


from utils.generate_suggestion import generate_suggestion
app = Flask(__name__)

@app.route("/")
def hello_world():

    return "<p>Hello, World!</p>"



@app.route("/suggest")
def suggest():
    suggestion = generate_suggestion()

    return suggestion