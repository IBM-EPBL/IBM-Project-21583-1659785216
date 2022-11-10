from flask import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('ibm.html')



if __name__ == '__main__':
    app.run(debug=True)