from flask import Flask, redirect, render_template, request ,url_for
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from werkzeug.utils import secure_filename
import os
import shutil

import dataCalculator


pio.templates.default = 'plotly_dark'

UPLOAD_FOLDER = os.path.join('mysite', 'JSON')
ALLOWED_EXTENSIONS = {'json'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            token = dataCalculator.generate_token()
            filename = f'result-{token}.json'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('result', token=token))

    return redirect(url_for('invalid'))

@app.route("/result/<token>")
def result(token: str):
    dataCalculator.main(token)

    CommonPairings = pd.read_csv(f'mysite/csvFiles/{token}/CommonPairings.csv')
    MonthlyActivity = pd.read_csv(f'mysite/csvFiles/{token}/MonthlyActivity.csv')
    DailyActivity = pd.read_csv(f'mysite/csvFiles/{token}/DailyActivity.csv')
    HourlyActivity = pd.read_csv(f'mysite/csvFiles/{token}/HourlyActivity.csv')
    textActivity = pd.read_csv(f'mysite/csvFiles/{token}/UserData.csv')


    pairings = px.bar(CommonPairings, x = 'Messages', y = 'Pair', orientation = 'h', width=1600, height=400,color='Messages')
    mactivity = px.line(MonthlyActivity, x = 'Month', y = MonthlyActivity.columns[2:], width=1600, height=400)
    dactivity = px.line(DailyActivity, x = 'Date', y = DailyActivity.columns[2:], width=1600, height=400)
    hactivity = px.line(HourlyActivity, x = 'Hour', y = HourlyActivity.columns[2:], width=1600, height=400)
    tactivty = px.bar(textActivity, x = 'User', y = textActivity.columns[2:], width=1600, height=400)

    graphJSON = json.dumps(pairings, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON1 = json.dumps(mactivity, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(dactivity, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(hactivity, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON4 = json.dumps(tactivty, cls=plotly.utils.PlotlyJSONEncoder)

    os.remove(f'mysite/JSON/result-{token}.json')
    shutil.rmtree(f'mysite/csvFiles/{token}/')

    return render_template('result.html', graphJSON = graphJSON, graphJSON1 = graphJSON1,graphJSON2 = graphJSON2,graphJSON3 = graphJSON3, graphJSON4 = graphJSON4)