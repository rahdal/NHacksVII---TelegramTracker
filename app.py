from flask import Flask, render_template
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = 'plotly_dark'

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')



@app.route("/result")
def result():
    
    CommonPairings = pd.read_csv('CommonPairings.csv')
    DailyActivity = pd.read_csv('DailyActivity.csv')
    HourlyActivity = pd.read_csv('HourlyActivity.csv')

    
    pairings = px.bar(CommonPairings, x = 'Messages', y = 'Pair', orientation = 'h', width=1600, height=400)
    mactivity = px.line(DailyActivity, x = 'Date', y = DailyActivity.columns[2:DailyActivity.shape[1]], width=1600, height=400)
    hactivity = px.line(HourlyActivity, x = 'Hour', y = HourlyActivity.columns[2:HourlyActivity.shape[1]], width=1600, height=400)

    graphJSON = json.dumps(pairings, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(mactivity, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(hactivity, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('result.html', graphJSON = graphJSON, graphJSON1 = graphJSON1,graphJSON2 = graphJSON2)