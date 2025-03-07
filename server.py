from flask import Flask
from flask import render_template
from flask import request
from reshape import mnist_preprocess
from flask import jsonify, redirect
import numpy as np
from werkzeug.middleware.proxy_fix import ProxyFix
app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.before_request
def ensure_https():
    if request.is_secure and request.headers.get("X-Forwarded-Proto", "https") == "http":
        url = request.url.replace("http://", "https://", 1)
        return redirect(url,301)

def relu(x):
    return (x > 0) * x

def softmax(x):
  numerator = np.exp(x)
  denominator = np.sum(np.exp(x))
  y = numerator / denominator
  return y

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/homepage2")
def homepage2():
    return render_template("index2.html")

@app.route("/doodles_playground/", methods=["GET", "POST"])
def doodles_playground():
    mousePositions = request.get_json()
    image28by28 = mnist_preprocess(input_data = mousePositions)
    weights_1, weights_2 = load_doodles_weights()
    np.set_printoptions(suppress=True, precision=2, floatmode='fixed')
    output = predict(image28by28, weights_1, weights_2)
    inner_list = output[0]
    results = {"pizza":inner_list[0],  "tornado":inner_list[1]}
    print(results)
    return jsonify(results)

def load_doodles_weights():
    file = np.load("windows.npz")
    weights_1 = file["weights_1"]
    weights_2 = file["weights_2"]
    return weights_1, weights_2

@app.route("/mnist_playground/", methods=["GET", "POST"])
def mnist_playground():
    positions = request.json
    image28by28 = mnist_preprocess(input_data=positions)
    weights_1, weights_2 = load_model()
    output = predict(image28by28, weights_1, weights_2)
    np.set_printoptions(suppress=True, precision=2, floatmode='fixed')
    inner_list = output[0]
    prediction_dictionary = {}
    for i in range(0, 10):
        prediction_dictionary[i] = inner_list[i]
    print(prediction_dictionary)
    print(positions)
    return jsonify(prediction_dictionary)

def load_model(): 
    file = np.load("mnistV1.npz")
    weights_1 = file["weights_1"]
    weights_2 = file["weights_2"]
    return[weights_1, weights_2]

def predict(image28by28, weights_1, weights_2):
    reshapedimage784 = image28by28.reshape(1, 784)
    layer_1 = reshapedimage784
    layer_2 = relu(np.dot(layer_1, weights_1)) 
    layer_3 = softmax(np.dot(layer_2, weights_2))
    return layer_3 * 100

app.run(debug=True, host = "0.0.0.0")#