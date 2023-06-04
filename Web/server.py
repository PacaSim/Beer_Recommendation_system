from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import joblib

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
   beer_list = pd.read_csv('beer_list.csv', encoding='utf-8', index_col=0)
   beer_list = beer_list['맥주']
   data = request.form
   print(data)
   return render_template('register.html',beer_list=beer_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
   data1 = request.form
   print(data1)
   return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)