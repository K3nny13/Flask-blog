from flask import Flask, render_template, url_for


app = Flask(__name__)

posts = [{
    'author': 'Kenny',
    'title': 'First Blog',
    'content': 'This is a First Blog Post',
    'date': '14 December 2018' 
},
{
    'author': 'Kenny',
    'title': 'First Blog',
    'content': 'This is a First Blog Post',
    'date': '14 December 2018' 
}]


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', posts=posts, title='Index')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == "__main__":
    app.run(debug=True)