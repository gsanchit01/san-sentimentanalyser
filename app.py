# importing libraries for flask, database, model
import os
from datetime import datetime, timedelta
from pickle import load

import pytz
from flask import Flask, jsonify, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob

# from model_nltk import predict_sentiment

app = Flask(__name__, template_folder='templates')

# "sqlite:///data.sqlite"
# /// for relative path
# //// for absolute path
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'DATABASE_URL', "sqlite:///data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'thisissecret')
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=12)

db = SQLAlchemy(app)

# since the app is hosted on heroku so this line of code is to change the timezone
IST = pytz.timezone('Asia/Kolkata')


# I have creted two models but I am using model_nltk because of its high accurcy and less execution time.
# textblob is used for ploting the subjectivity and polarity curve for the input data

# class for creating and initialising database
class New_Data(db.Model):

    Id = db.Column(db.Integer, primary_key=True)
    Text = db.Column(db.Text)
    Sentiment = db.Column(db.String(20))
    # .now(IST).strftime('%Y-%m-%d %H:%M:%S'))
    Date = db.Column(db.DateTime, default=datetime.now(
        IST).strftime('%Y-%m-%d %H:%M:%S'))

    def __init__(self, Text, Sentiment):
        self.Text = Text
        self.Sentiment = Sentiment


# loading classifier
with open('my_classifier.pickle', 'rb') as f:
    classifier = load(f)


def allowed_file(filename):
    '''Checking file extension i.e. text file or not'''
    return '.' in filename and filename.split('.')[1] == 'txt'


# route for home page
@app.route('/', methods=['POST', 'GET'])
def home():
    # if request.method == 'POST':
    #     sentence = request.form.get('twt')

    #     sentiment = predict_sentiment(sentence, classifier)

    #     # adding emoji to the sentiment
    #     if sentiment == "Positive":
    #         sentiment += " \U0001f600"

    #     elif sentiment == "Negative":
    #         sentiment += " \U0001F641"

    #     else:
    #         pass

    #     # creating an instance of the data table for the database and commiting the changes
    #     usr_data = New_Data(sentence, sentiment.split()[0])
    #     db.session.add(usr_data)
    #     db.session.commit()

    #     text = "You have entered \"" + sentence + "\""
    # return render_template('index.html', text=text, sentiment="Sentiment: " + sentiment)

    return render_template('index.html', script=True)


# route for about page
@app.route('/about')
def about():
    return render_template('about.html')


# route for members page
# @app.route('/member')
# def contact():
#     return render_template('members.html')


# route for fastapi
# setting default value for the api
# @app.route('/fast-api/', defaults={'sentence': 'Great'})
# @app.route('/fast-api/<sentence>')
# def fast_api(sentence):
#     sentiment = predict_sentiment(sentence, classifier)

#     return jsonify({'sentence': sentence, 'sentiment': sentiment})


# setting post method for the api
@app.route('/fastapi', methods=['POST'])
def fastapi():
    text = request.form['text']
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        sentiment = 'Positive'
    elif polarity < 0:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return jsonify({'sentiment': sentiment})


# route for uploading and saving temperary file
@app.route('/upload')
def upload():
    mssg = request.args.get('msg')
    # if the uploaded file is not a text file
    if mssg == "ntxt":
        mssg = "Kindly Upload a text file"

    # if the uploaded textfile is not readable
    elif mssg == "incrt":
        mssg = "Upload file of correct format"

    else:
        mssg = None

    return render_template("upload.html", mssg=mssg)


# route for displaying the curves for the given text file
@app.route('/canvas', methods=['POST', 'GET'])
def canvas():
    if request.method == 'POST':
        pos = 0
        neg = 0
        subject = []
        polar = []
        file = request.files['file']

        # if the file is correct and readable then save it
        if allowed_file(file.filename):
            file.save(file.filename)

            try:
                # open file, read the content perform the analysis and then return the template with the values
                with open(file.filename) as fl:
                    content = fl.read().split('\n')
                    for line in content:
                        # t = fl.readline()
                        a = TextBlob(line).sentiment.polarity*100
                        polar.append(a)
                        subject.append(
                            TextBlob(line).sentiment.subjectivity*100)
                        if a > 0:
                            pos += 1
                        else:
                            neg += 1
                os.remove(file.filename)
                return render_template("canvas.html", value1=subject, value2=polar, pos=pos, neg=neg)

            except:
                os.remove(file.filename)
                return redirect(url_for('upload', msg="incrt"))

        return redirect(url_for('upload', msg="ntxt"))

    # these readings are for mannual or you can say get request when there is no file upload.
    # these readings are not random value, the values are valid for the review.txt file present in static/temp
    subject = [37.351190476190474, 54.50000000000001, 83.75, 50.0, 49.00000000000001, 68.0, 33.05555555555556, 72.08333333333334, 80.3030303030303, 55.00000000000001, 64.40476190476191, 31.785714285714285, 55.625, 0.0, 79.16666666666666, 80.57142857142857, 36.220238095238095, 75.0, 25.833333333333336, 54.99999999999999, 56.904761904761905, 100.0, 56.666666666666664, 20.833333333333336, 72.5, 46.666666666666664, 100.0, 48.00000000000001, 66.75925925925925, 50.71428571428571, 75.0, 54.833333333333336, 51.16666666666667, 57.857142857142854, 65.5952380952381, 75.0, 50.0, 60.0, 76.66666666666666, 10.0, 70.0, 40.0, 100.0, 53.333333333333336, 27.083333333333332, 35.55555555555556, 61.66666666666667, 63.33333333333334, 35.55555555555556, 50.476190476190474, 8.333333333333332, 42.00000000000001, 45.0, 47.5, 20.0, 70.0, 50.0, 50.0, 43.05555555555555, 40.00000000000001, 41.111111111111114, 72.5, 52.38095238095239, 52.5, 38.27777777777778, 53.99999999999999, 70.0, 45.0, 72.4074074074074, 50.0, 83.75, 54.285714285714285, 63.33333333333333, 38.33333333333333, 52.5, 53.333333333333336, 30.138888888888886, 57.14285714285714, 10.0, 75.0, 61.74999999999999, 25.0, 72.38095238095238, 76.66666666666666, 52.5, 71.72619047619048, 50.0, 37.5, 53.0, 49.404761904761905, 34.44444444444444, 60.0, 28.57142857142857, 47.7922077922078, 46.666666666666664, 45.77922077922078, 56.25, 69.16666666666667, 54.166666666666664, 38.874458874458874, 42.5, 28.888888888888893, 60.19999999999999, 80.0, 46.11111111111111, 75.0, 46.666666666666664, 80.47619047619048, 38.57142857142858, 59.791666666666664, 17.5, 71.13636363636364, 57.95918367346938, 52.22222222222223, 54.91071428571428, 64.99999999999999, 0.0, 50.33333333333333, 51.0, 80.0, 6.666666666666667, 83.33333333333334, 71.66666666666667, 22.5, 42.5, 70.0, 41.875, 53.333333333333336, 57.50000000000001, 25.0, 65.0, 63.33333333333334, 34.6875, 75.0, 36.00000000000001, 68.33333333333333, 36.333333333333336, 40.55555555555555, 72.5, 41.42857142857142, 44.375, 35.0, 67.5, 49.16666666666667, 55.99999999999999, 80.0, 25.0, 18.333333333333336, 76.25, 95.83333333333334, 53.333333333333336, 72.5, 28.750000000000004, 38.888888888888886, 68.05555555555554, 40.520833333333336, 31.666666666666664, 80.0, 44.666666666666664, 53.75000000000001, 95.23809523809524, 46.04166666666667, 73.33333333333334, 50.0, 70.0, 65.0, 46.666666666666664, 69.58333333333333, 50.0, 17.22222222222222, 45.892857142857146, 53.333333333333336, 35.55555555555556, 40.833333333333336, 78.91156462585033, 44.166666666666664, 60.0, 100.0, 73.0, 37.375, 75.0, 66.35714285714285, 100.0, 65.0, 72.91666666666666, 76.29629629629629, 50.0, 36.25000000000001, 90.0, 50.0, 16.666666666666664, 41.36363636363637, 55.55555555555555, 43.333333333333336, 45.75, 47.857142857142854, 50.0, 70.83333333333333, 22.499999999999996, 50.0, 23.291666666666664, 40.0, 100.0, 69.5, 30.0, 47.72727272727273, 65.3125, 54.58874458874459, 67.5, 95.83333333333334, 59.72222222222222, 79.16666666666666, 72.01388888888887, 59.0, 42.5, 72.50000000000001, 54.91666666666667, 56.39285714285715, 45.55555555555556, 0.0, 46.666666666666664, 60.0, 39.833333333333336, 65.0, 33.92857142857143, 41.111111111111114, 57.50000000000001, 75.0, 33.33333333333333, 43.16666666666667, 66.66666666666666, 0.0, 80.0, 54.99999999999999, 77.77777777777777, 48.33333333333334, 34.19642857142857, 62.083333333333336, 49.28571428571429, 35.0, 40.0, 57.85714285714286, 59.66666666666668, 82.5, 66.66666666666666, 53.75, 35.0, 60.83333333333333, 36.66666666666667, 22.960858585858585,
               38.33333333333333, 44.44444444444445, 60.17857142857144, 47.72727272727273, 88.33333333333333, 30.666666666666664, 0.0, 56.666666666666664, 50.0, 6.666666666666667, 70.83333333333334, 75.0, 67.5, 28.333333333333332, 52.22222222222223, 60.66666666666667, 32.0, 25.0, 45.45454545454545, 37.5, 61.25000000000001, 40.0, 50.0, 6.666666666666667, 17.5, 86.0, 30.833333333333336, 55.333333333333336, 73.75, 60.0, 63.33333333333333, 100.0, 45.0, 20.0, 57.30983302411874, 37.5, 53.66666666666667, 45.09523809523809, 69.16666666666667, 0.0, 0.0, 28.333333333333332, 36.666666666666664, 54.58333333333334, 46.74242424242425, 76.66666666666666, 25.0, 47.77777777777778, 38.7037037037037, 51.66666666666667, 77.22222222222221, 63.33333333333334, 85.0, 86.0, 38.33333333333333, 95.83333333333334, 60.0, 64.99999999999999, 47.66666666666667, 38.33333333333333, 35.0, 90.0, 80.55555555555554, 72.85714285714285, 10.0, 48.33333333333333, 81.77777777777777, 82.22222222222223, 39.8, 41.66666666666666, 15.000000000000002, 55.99999999999999, 60.55555555555555, 61.39285714285714, 71.11111111111111, 65.5, 71.78571428571429, 70.71428571428571, 57.777777777777786, 80.0, 44.16666666666667, 0.0, 70.0, 60.0, 25.0, 52.75, 63.99999999999999, 68.60000000000001, 57.99999999999999, 40.5, 51.99603174603175, 46.0, 63.33333333333333, 74.16666666666667, 60.0, 75.0, 45.55555555555556, 31.999999999999996, 54.848484848484844, 58.75, 85.77777777777777, 100.0, 33.57575757575758, 41.66666666666667, 39.333333333333336, 65.33333333333333, 53.333333333333336, 100.0, 64.24242424242424, 0.0, 71.12244897959182, 39.791666666666664, 62.875, 20.0, 0.0, 40.0, 50.0, 34.166666666666664, 68.0, 36.666666666666664, 66.5625, 21.25, 39.58333333333333, 50.0, 60.0, 63.39285714285714, 50.0, 31.041666666666668, 33.5, 38.0, 38.33333333333333, 57.50000000000001, 70.66666666666667, 63.25000000000001, 42.6948051948052, 45.555555555555564, 44.72222222222222, 57.49999999999999, 57.00000000000001, 71.66666666666667, 68.0, 56.2962962962963, 33.33333333333333, 63.14814814814815, 42.5, 35.416666666666664, 67.1875, 40.0, 81.25, 70.0, 52.5, 31.666666666666664, 52.0, 57.49999999999999, 79.16666666666666, 31.11111111111111, 61.11111111111111, 58.33333333333333, 46.666666666666664, 41.66666666666667, 36.25, 47.61904761904762, 0.0, 68.88888888888887, 41.666666666666664, 38.33333333333333, 80.0, 54.28571428571429, 35.0, 42.77777777777778, 31.25, 100.0, 46.666666666666664, 58.12500000000001, 31.507936507936506, 51.42857142857142, 57.50000000000001, 69.5, 16.666666666666664, 58.33333333333333, 41.571969696969695, 45.0, 66.66666666666666, 65.41666666666667, 72.77777777777779, 34.166666666666664, 46.875, 50.8, 67.8125, 62.5, 87.5, 73.0, 65.8, 25.83333333333333, 47.083333333333336, 75.0, 24.444444444444446, 53.333333333333336, 75.0, 100.0, 76.0, 77.08333333333333, 54.72222222222223, 51.87500000000001, 33.33333333333333, 40.138888888888886, 54.0, 29.166666666666668, 30.0, 40.714285714285715, 66.66666666666666, 65.0, 45.55555555555556, 37.5, 60.0, 47.49999999999999, 33.75, 63.33333333333333, 38.89682539682539, 36.66666666666667, 54.166666666666664, 39.72222222222222, 65.37414965986395, 42.333333333333336, 79.52380952380952, 37.91666666666667, 40.0, 77.0, 50.0, 0.0, 0.0, 44.99999999999999, 47.99242424242424, 42.5, 67.85714285714285, 67.14285714285715, 87.5, 53.333333333333336, 55.55555555555555, 70.0, 50.83333333333333, 75.0, 49.28571428571429, 34.42307692307692, 56.00000000000001, 41.66666666666667, 62.77777777777778, 56.00000000000001, 53.333333333333336, 73.33333333333334]

    polar = [16.517857142857142, 24.25, 31.25, -9.375, 24.500000000000004, 6.0000000000000036, 8.333333333333334, 34.6875, -61.81818181818181, 41.5, 4.0476190476190474, 14.285714285714285, -0.6249999999999999, 0.0, 48.75, 18.71428571428571, -3.7500000000000018, -25.0, 7.500000000000001, 4.166666666666666, -22.61904761904762, -100.0, 45.83333333333333, 6.25, -34.375, -1.749999999999998, 35.25, -20.0, 2.7777777777777777, 7.857142857142857, 0.0, 35.166666666666664, 3.0000000000000004, 25.0, 3.928571428571428, 50.0, -18.75, -15.0, 20.833333333333336, 0.0, 20.0, 25.0, -100.0, 40.0, -14.583333333333334, 0.0, 31.666666666666664, 40.00000000000001, -6.666666666666667, -4.52380952380952, 8.333333333333332, 25.5, -3.125, 39.375, 0.0, -6.333333333333332, 35.714285714285715, 28.749999999999996, 32.916666666666664, 0.0, 16.11111111111111, -28.749999999999996, 11.30952380952381, 6.071428571428572, 15.055555555555552, 22.66666666666667, -40.0, 17.0, 25.0, -0.8333333333333331, 8.124999999999998, 12.85714285714286, 12.222222222222225, 3.7500000000000004, 45.0, 29.166666666666668, -0.6944444444444443, -10.714285714285714, -10.0, -9.375, 14.125000000000004, -25.0, -43.57142857142857, -10.0, -48.75, -33.29613095238095, -16.666666666666664, 18.75, 6.999999999999999, -12.85714285714286, -0.11111111111111183, 5.0, 24.107142857142858, 15.909090909090908, 11.666666666666666, -1.623376623376625, -15.625, -2.4999999999999964, -55.41666666666666, 10.28138528138528, 14.166666666666666, 26.666666666666668, 27.0, -22.000000000000004, 26.111111111111114, 75.0, 33.33333333333333, -58.285714285714285, -26.339285714285715, 14.045138888888891, 2.5, 33.18181818181818, -9.375, -26.666666666666668, 18.30357142857143, -30.000000000000004, 0.0, -32.99999999999999, -9.0, 56.66666666666668, 6.666666666666667, 43.75, -33.33333333333333, -4.166666666666666, -10.0, 38.33333333333333, 12.5, -8.333333333333332, 48.75, -9.375, 95.0, 19.58333333333333, 4.166666666666666, -43.18181818181818, 15.999999999999998, 48.33333333333334, 0.8958333333333353, 12.083333333333336, 10.416666666666668, 24.285714285714285, 8.958333333333336, -20.0, 4.375000000000001, 14.583333333333334, -26.0, 70.0, -9.375, 8.333333333333332, 10.0, -20.0, 22.5, 35.0, -6.25, 15.0, -18.611111111111104, -1.1458333333333341, 17.5, 0.0, 21.66666666666667, 60.0, 46.42857142857143, 21.458333333333336, -36.66666666666667, 30.0, 34.99999999999999, -1.250000000000001, -4.500000000000002, -38.75, 0.0, -6.38888888888889, 27.45535714285714, -16.666666666666664, 11.111111111111112, 28.125, -45.714285714285715, -17.499999999999993, 14.444444444444446, -100.0, 30.0, -20.791666666666668, 37.77777777777778, 15.42857142857143, 0.0, -40.0, -23.958333333333332, 33.33333333333333, 50.0, 13.333333333333334, 40.0, -16.666666666666664, -16.666666666666664, 25.90909090909091, 4.861111111111111, 45.83333333333333, -1.0000000000000009, 25.0, 50.0, 5.00000000000001, 15.0, -1.3541666666666647, 12.5, 27.500000000000004, 3.7500000000000004, 34.035714285714285, 25.0, 26.81818181818182, 7.812499999999998, 14.329004329004327, 25.0, 8.333333333333332, -23.33333333333333, -29.583333333333332, 30.763888888888886, -22.833333333333336, -26.25, 7.916666666666668, 43.5, -20.44642857142857, 6.111111111111112, 0.0, 35.625, 37.5, 6.0, -33.05555555555556, 13.750000000000002, 44.166666666666664, 22.5, 30.0, 0.0, 1.7222222222222223, -1.5909090909090873, 0.0, 85.0, 21.354166666666664, -11.111111111111112, 24.72222222222222, 8.57142857142857, -2.583333333333333, -20.892857142857142, 5.0, -40.0, 31.9047619047619, -18.333333333333336, 85.00000000000001, 10.416666666666668, 26.875, -16.25, -27.187499999999993, 0.0, -4.85479797979798, -3.095238095238093, 33.33333333333333,
             37.32142857142857, 19.318181818181817, -29.166666666666668, 7.833333333333332, 0.0, -33.33333333333333, 10.000000000000002, 6.666666666666667, -16.666666666666664, 0.0, -30.0, 10.0, -3.333333333333329, 2.000000000000001, -3.9999999999999996, 5.833333333333334, 13.636363636363635, -2.5, 7.500000000000001, 26.666666666666668, 5.000000000000002, 0.0, -17.5, -8.0, 19.58333333333333, -22.166666666666668, -14.6875, 23.75, 36.666666666666664, -61.66666666666667, 6.666666666666667, 10.0, -12.5417439703154, 18.75, -3.0000000000000004, 21.476190476190478, 16.875000000000004, 0.0, 0.0, -18.333333333333336, 21.25, 36.25000000000001, 21.439393939393938, -13.333333333333334, 6.938893903907228e-16, 32.22222222222222, 17.5, 55.833333333333336, -28.33333333333333, 0.0, 32.5, 33.5, 24.166666666666668, 61.66666666666667, 33.33333333333333, 0.0, -9.5, 11.666666666666666, 5.0, -50.0, -17.77777777777777, -15.714285714285708, -2.5, -29.999999999999993, 41.5, 33.70370370370371, 4.2, 12.77777777777778, 15.0, 27.250000000000004, -8.333333333333332, 25.39285714285714, 10.83333333333334, 15.750000000000004, -10.714285714285715, 5.357142857142859, -23.333333333333332, 55.00000000000001, 10.000000000000004, 0.0, 49.16666666666667, 28.749999999999996, -12.5, 3.5833333333333344, -1.000000000000002, 45.199999999999996, 24.0, 15.708333333333336, -15.845238095238093, 11.000000000000002, -16.666666666666668, 56.666666666666664, 24.16666666666666, -50.0, 19.166666666666668, 12.374999999999996, 10.909090909090908, 0.0, 57.00000000000001, -68.75, 21.878787878787882, 26.666666666666668, -17.333333333333336, -46.0, 34.0, 0.0, -15.287878787878784, 0.0, 33.41836734693877, -17.499999999999996, 23.250000000000004, 3.3333333333333335, 0.0, -45.0, 7.500000000000001, -37.5, 32.0, -1.25, -18.4375, 13.750000000000002, 18.229166666666664, 28.333333333333332, 46.875, 14.955357142857142, 31.66666666666667, 15.416666666666668, 38.0, 1.9999999999999998, 4.999999999999999, 36.25, 45.0, -14.000000000000002, -19.63203463203463, 2.4999999999999996, -38.81944444444444, 25.83333333333333, -5.750000000000001, 36.66666666666667, 43.625, 24.814814814814813, 16.666666666666664, 15.74074074074074, -5.0, 12.5, 8.906250000000002, 15.999999999999998, 25.0, 50.0, 12.5, -28.333333333333332, 21.000000000000004, 48.75, -29.166666666666668, 18.333333333333336, 10.347222222222223, 3.3333333333333353, 47.5, 26.666666666666668, 32.5, -2.421536796536798, 0.0, -53.05555555555554, 37.5, 23.75, -25.0, 51.42857142857142, 13.5, 18.935185185185187, 16.25, 13.0, 51.0, 37.1875, 11.289682539682541, 44.767857142857146, 13.583333333333334, 70.25, 16.666666666666664, -2.916666666666663, 18.409090909090907, 15.0, -25.0, -8.75, -2.0833333333333313, 29.166666666666668, 29.375, 7.533333333333333, 15.312500000000002, 18.125000000000004, -31.25, 32.24999999999999, 22.53333333333333, 15.625, 2.500000000000001, -25.0, 7.2222222222222205, 36.66666666666667, -25.0, 100.0, 31.5, -2.0833333333333344, 3.3333333333333326, 19.374999999999996, 25.0, 9.027777777777777, -27.999999999999996, 15.416666666666668, -31.66666666666667, 1.4285714285714282, -6.666666666666667, 28.125, -21.11111111111111, 0.0, 15.0, 41.66666666666667, 3.7500000000000004, 27.22222222222222, -15.373015873015875, 43.333333333333336, -29.999999999999993, 1.666666666666668, 32.31292517006803, -11.999999999999996, 8.095238095238095, 8.888888888888891, -40.0, -45.0, 40.0, 0.0, 0.0, 5.0, -5.227272727272728, 2.4999999999999996, 6.607142857142858, -20.0, -33.12500000000001, 19.375, -14.999999999999995, 24.5, 6.666666666666667, 80.0, 11.428571428571429, 1.8750000000000002, 53.99999999999999, -38.88888888888889, 58.333333333333336, -13.750000000000002, -26.666666666666668, 23.333333333333332]

    pos = 246
    neg = 254

    return render_template('canvas.html', value1=subject, value2=polar, pos=pos, neg=neg)


# route for admin login panel
@app.route('/login')
def login():
    error = request.args.get('er')
    if error == 'incrt':
        error = "Invalid Credentials"

    elif error == 'lnf':
        error = "You need to login first"

    else:
        error = None

    return render_template('login.html', error=error)


# this route is for showing the data of the database with in html template
@app.route('/show', methods=['GET', 'POST'])
def show():
    if request.method == "POST":
        if request.form.get('username') == os.environ.get('sausr', 'gparas') and request.form.get('pwd') == os.environ.get('sapwd', 'gparas'):
            session['sausr'] = request.form.get('username')
            session['sapwd'] = request.form.get('pwd')
            table = New_Data.query.all()[::-1]
            return render_template('show.html', table=table)

        else:
            return redirect(url_for('login', er="incrt"))

    try:
        if 'sausr' in session:
            table = New_Data.query.all()[::-1]
            return render_template('show.html', table=table)

    except:
        pass

    return redirect(url_for('login', er="lnf"))


@app.route('/test')
def test():
    return render_template('index.html', script=True)


@app.errorhandler(404)
def error404(error):
    return render_template("error404.html"), 404


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
