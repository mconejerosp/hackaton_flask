import os
import pandas as pd
from flask import Flask
from surprise import dump
from collections import defaultdict

app = Flask(__name__)
f = None

def get_df_predictions(predictions, n = 10):
  top_n = defaultdict(list)
  for uid, iid, true_r, est, _ in predictions:
    top_n[uid].append((iid, est))
  for uid, user_ratings in top_n.items():
    user_ratings.sort(key = lambda x: x[1], reverse = True)
    top_n[uid] = user_ratings[: n ]
  preds_df = pd.DataFrame([(id, pair[0],pair[1]) for id, row in top_n.items() for pair in row],
                      columns=["user_id" ,"items_id","event_name"])
  return preds_df

def get_top_n(userid, preds_df, n = 10):
  pred_usr = preds_df[preds_df["user_id"] == (userid)]
  return pred_usr

@app.route('/')
def startup():
  return 'Initialized'

@app.route("/prediction/<user_id>", methods=["GET"])
def getPrediction(user_id):
  data = get_top_n(userid = int(user_id), preds_df = predictions_df)
  js = data.to_json(orient = 'columns')
  return js, 200

def run_server(request):
  file_name = os.path.expanduser('predictionsv1')
  loadded_predictions, _ = dump.load(file_name)
  predictions_df = get_df_predictions(predictions = loadded_predictions)
  app.run()
