import os
import pandas as pd
from flask import Flask
from surprise import dump
from collections import defaultdict

app = Flask("internal")

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

def main(request):
  file_name = os.path.expanduser('predictionsv1')
  loadded_predictions, _ = dump.load(file_name)
  global predictions_df
  predictions_df = get_df_predictions(predictions = loadded_predictions)

  #Create a new app context for the internal app
  internal_ctx = app.test_request_context(path=request.full_path,
                                          method=request.method)
  
  #Copy main request data from original request
  #According to your context, parts can be missing. Adapt here!
  internal_ctx.request.data = request.data
  internal_ctx.request.headers = request.headers
  
  #Activate the context
  internal_ctx.push()
  #Dispatch the request to the internal app and get the result 
  return_value = app.full_dispatch_request()
  #Offload the context
  internal_ctx.pop()
  
  #Return the result of the internal app routing and processing      
  return return_value