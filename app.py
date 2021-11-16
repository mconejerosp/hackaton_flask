from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route("/model", methods=["POST", "GET"])
def getModel():
  data = {'user_id': 'TEST', 'item_id': 'UUID', 'event_name': 'purchase'}
  return jsonify(data), 200

if __name__ == '__main__':
   app.run()