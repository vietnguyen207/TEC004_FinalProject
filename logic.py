from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Student Analysis System</h1>
    <p>Welcome to my project</p>
    """

if __name__ == "__main__":
    app.run(debug=True)
    
def about():
    return """
    <h1>About</h1>
    <p>This project manages student scores.</p>
    """