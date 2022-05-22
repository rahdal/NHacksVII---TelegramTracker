from flask import Flask, redirect, render_template, request ,url_for
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from werkzeug.utils import secure_filename
import os


pio.templates.default = 'plotly_dark'
UPLOAD_FOLDER = 'JSON/'
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
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      
    return redirect(url_for('result'))

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