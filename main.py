import os
import pandas as pd
from flask import Flask
from surprise import dump
from google.cloud import storage
from collections import defaultdict

app = Flask("internal")

def get_df_predictions(predictions, n = 10):
  top_n = defaultdict(list)
  for uid, iid, true_r, est, iname in predictions:
    top_n[uid].append((iid, est, iname))
  for uid, user_ratings in top_n.items():
    user_ratings.sort(key = lambda x: x[1], reverse = True)
    top_n[uid] = user_ratings[: n ]
  preds_df = pd.DataFrame([(id, pair[0], pair[1], pair[2]) for id, row in top_n.items() for pair in row],
                      columns=["user_id" ,"items_id","event_name", "item_name"])
  return preds_df

def get_cat_predictions(predictions, n = 10):
  top_n = defaultdict(list)
  for uid, iid, true_r, est, _ in predictions:
    top_n[uid].append((iid, est))
  for uid, user_ratings in top_n.items():
    user_ratings.sort(key = lambda x: x[1], reverse = True)
    top_n[uid] = user_ratings[: n ]
  cat_df = pd.DataFrame([(id, pair[0], pair[1]) for id, row in top_n.items() for pair in row],
                      columns=["user_id", "category", "estimation"])
  return cat_df

def get_top_n(userid, preds_df, n = 10):
  pred_usr = preds_df[preds_df["user_id"] == (userid)]
  return pred_usr

def get_top_n_cat(userid, preds_df, n = 10):
  pred_cat = preds_df[preds_df["user_id"] == (userid)]
  return pred_cat

def downloadPredictions():
  storage_client = storage.Client("flowing-bonito-331815")
  bucket = storage_client.get_bucket('flowing-bonito-331815.appspot.com')
  blob = bucket.blob("predictionsv1")
  blob.download_to_filename('predictionsv1')
  blob = bucket.blob("categoriesv1")
  blob.download_to_filename('categoriesv1')

@app.route('/')
def startup():
  return 'Initialized'

@app.route("/predictions/items/<user_id>", methods=["GET"])
def getUserPrediction(user_id):
  data = get_top_n(userid = user_id, preds_df = predictions_df)
  js = data.to_json(orient = 'columns')
  return js, 200

@app.route("/predictions/categories/<user_id>", methods=["GET"])
def getCategoryPrediction(user_id):
  data = get_top_n_cat(userid = user_id, preds_df = categories_df)
  js = data.to_json(orient = 'columns')
  return js, 200

if __name__ == '__main__':
  downloadPredictions()
  print("READING ITEMS.......")
  file_name = os.path.expanduser('predictionsv1')
  loaded_predictions, _ = dump.load(file_name)
  predictions_df = get_df_predictions(predictions = loaded_predictions)
  print("FILE READ..........")

  print("READING CATEGORIES...")
  file_name = os.path.expanduser('categoriesv1')
  categories_predictions, _ = dump.load(file_name)
  categories_df = get_cat_predictions(predictions = categories_predictions)
  print("CATEGORIES READ.....")

  app.run("0.0.0.0", 8080)
