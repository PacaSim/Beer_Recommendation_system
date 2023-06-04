from flask import Flask, render_template, request, flash, session
import numpy as np
import pandas as pd
import joblib

app = Flask(__name__)

app.secret_key = "beer recommendation"

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    beer_list = pd.read_csv('beer_list.csv', encoding='utf-8', index_col=0)
    beer_list = beer_list['맥주']

    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        beer = request.form.get('beer')

        # 유효성 검사
        if password != password2:
            flash('비밀번호가 서로 다릅니다.', category='error')
        elif len(password) < 7:
            flash('패스워드가 너무 짧습니다.', category='error')
        else:
            flash('회원가입이 완료되었습니다.', category='success')

    return render_template('register.html', beer_list=beer_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
   data1 = request.form
   print(data1)
   return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)