from flask import Flask

app = Flask("oui")


@app.route("/")
def a():
    return "oui"


app.run()
