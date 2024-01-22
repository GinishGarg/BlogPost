from flask import Flask,render_template


app=Flask(__name__)


@app.route("/")
def home():
    return render_template('homepage.html')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')




app.run(debug=True)
