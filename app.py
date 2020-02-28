from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


# rotate the image
def rotate_image():
    pass

if __name__ == '__main__':
    app.run()
