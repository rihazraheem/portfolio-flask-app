from flask import Flask, render_template, abort

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<page>')
def pages(page):
    try:
        return render_template(f'{page}.html')
    except:
        abort(404)

if __name__ == "__main__":
    app.run()
