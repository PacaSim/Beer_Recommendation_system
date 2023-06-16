from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Rate
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error




views = Blueprint('views', __name__)

def recomm_feature(df, col):
    feature = col
    ratings = df[['아이디','맥주', feature]]

    # 피벗 테이블을 이용해 유저-아이디 매트릭스 구성
    ratings_matrix = ratings.pivot_table(feature, index='아이디', columns='맥주')
    ratings_matrix.head(3)
    # fillna함수를 이용해 Nan처리
    ratings_matrix = ratings_matrix.fillna(0)

    # 유사도 계산을 위해 트랜스포즈
    ratings_matrix_T = ratings_matrix.transpose()

    # 아이템-유저 매트릭스로부터 코사인 유사도 구하기
    item_sim = cosine_similarity(ratings_matrix_T, ratings_matrix_T)

    # cosine_similarity()로 반환된 넘파이 행렬에 영화명을 매핑해 DataFrame으로 변환
    item_sim_df = pd.DataFrame(data=item_sim, index=ratings_matrix.columns,
                              columns=ratings_matrix.columns)

    return item_sim_df

def recomm_beer(item_sim_df, beer_name):
    # 해당 맥주와 유사도가 높은 맥주 5개만 추천
    return item_sim_df[beer_name].sort_values(ascending=False)[1:7]

@views.route('/', methods = ['GET', 'POST'])
@login_required
def index():
  beer_list = pd.read_csv('beer\\beer_list.csv', encoding='utf-8', index_col=0)
  beer_year = pd.read_csv('beer\맥주_연도별평점.csv', encoding='utf-8', index_col=0)
  ratings = pd.read_csv('beer\정제된데이터.csv', encoding='utf-8', index_col=0)
  cluster_3 = pd.read_csv('beer\대표군집클러스터링.csv', encoding='utf-8', index_col=0)
  cluster_all = pd.read_csv('beer\전체맥주클러스터링.csv', encoding='utf-8', index_col=0)
  beer_list = beer_list['맥주']
  cluster_3 = cluster_3.values

  beer_name = current_user.beer
  df_aroma = recomm_feature(ratings, 'Aroma')
  df_flavor = recomm_feature(ratings, 'Flavor')
  df_mouthfeel = recomm_feature(ratings, 'Mouthfeel')
  df = df_aroma * 0.1 + df_flavor*0.1 + df_mouthfeel*0.1

  result = recomm_beer(df, beer_name)
  result = result.index.tolist()

  tmp_cluster=[]

  for i in range(3):
    target = cluster_all[cluster_all['맥주']==result[i]]
    target = target[['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']]
    target = target.values[0]
    tmp_cluster.append(target)

  tmp_year = []
  tmp_ratings = []
  for i in range(3):
      target = beer_year[beer_year['맥주']==result[i]]
      target_year = target['년'].tolist()
      target_rating = target['평점'].tolist()
      tmp_year.append(target_year)
      tmp_ratings.append(target_rating)

  targetdict = {
  'beer_name' : result,
  'beer_cluster1' : tmp_cluster[0].tolist(),
  'beer_cluster2' : tmp_cluster[1].tolist(),
  'beer_cluster3' : tmp_cluster[2].tolist(),
  'cluster1' : cluster_3[0].tolist(),
  'cluster2' : cluster_3[1].tolist(),
  'cluster3' : cluster_3[2].tolist(),
  'tmp_year' : tmp_year,
  'tmp_ratings' : tmp_ratings
  }
  targetJson = json.dumps(targetdict)

  # POST 한줄평 추가
  if request.method == "POST":
    beer = request.form.get('beer')
    rating = request.form.get('rating')
    comment = request.form.get('comment')

    if len(comment) >300:
      flash("내용이 너무 깁니다.", category="error")
    else:
      new_rate = Rate(user_id=current_user.id, beer=beer, rating=rating, oneline=comment)
      db.session.add(new_rate)
      db.session.commit()

      return redirect(url_for('views.index'))

  all_rates_1 = Rate.query.filter_by(beer=result[0]).all()
  all_rates_2 = Rate.query.filter_by(beer=result[1]).all()
  all_rates_3 = Rate.query.filter_by(beer=result[2]).all()
  all_rates_4 = Rate.query.filter_by(beer=result[3]).all()
  all_rates_5 = Rate.query.filter_by(beer=result[4]).all()
  all_rates_6 = Rate.query.filter_by(beer=result[5]).all()
  return render_template('index.html', all_rates1=all_rates_1,all_rates2=all_rates_2,all_rates3=all_rates_3,all_rates4=all_rates_4,all_rates5=all_rates_5,all_rates6=all_rates_6, result=result, beer_list=beer_list,targetJson=targetJson)