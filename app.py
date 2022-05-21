from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def index():
    
    CommonPairings = pd.read_csv('CommonPairings.csv')
    pairings = px.bar(CommonPairings, x = 'Pair', y = 'Messages')
    
    graphJSON = json.dumps(pairings, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON = graphJSON)