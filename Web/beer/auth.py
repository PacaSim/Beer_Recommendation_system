import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
  beer_list = pd.read_csv('beer\\beer_list.csv', encoding='utf-8', index_col=0)
  beer_list = beer_list['맥주']

  if request.method == 'POST':
      name = request.form.get('name')
      password = request.form.get('password')
      password2 = request.form.get('password2')
      beer = request.form.get('beer')

      # 유효성 검사
      user = User.query.filter_by(name=name).first()
      if password != password2:
          flash('비밀번호가 서로 다릅니다.', category='error')
      elif len(password) < 7:
          flash('패스워드가 너무 짧습니다.', category='error')
      else:
          new_user = User(name=name, password=generate_password_hash(password, method='sha256'), beer=beer)
          db.session.add(new_user)
          db.session.commit()
          # 회원가입 시 자동 로그인
          login_user(new_user, remember=True)

          return redirect(url_for('views.index'))

  return render_template('register.html', beer_list=beer_list)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(name=name).first()
    if user:
      if check_password_hash(user.password, password):
        login_user(user, remember=True)
        return redirect(url_for('views.index'))
      else:
        flash('비밀번호가 다릅니다.', category='error')
    else:
       flash('해당 이름이 없습니다.', category='error')
    
  return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))