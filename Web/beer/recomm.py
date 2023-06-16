from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Rate
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error




recomm = Blueprint('recomm', __name__)

def get_mse(pred, actual):
  # 평점이 있는 실제 영화만 추출
  pred = pred[actual.nonzero()].flatten()
  actual = actual[actual.nonzero()].flatten()
  return mean_squared_error(pred, actual)


# 특정 맥주와 비슷한 유사도를 가지는 맥주 Top_N에 대해서만 적용 -> 시간오래걸림
def predict_rating_topsim(ratings_arr, item_sim_arr, n=20):
  # 사용자-아이템 평점 행렬 크기만큼 0으로 채운 예측 행렬 초기화
  pred = np.zeros(ratings_arr.shape)

  # 사용자-아이템 평점 행렬의 맥주 개수만큼 루프
  for col in range(ratings_arr.shape[1]):
      # 유사도 행렬에서 유사도가 큰 순으로 n개의 데이터 행렬의 인덱스 반환
      top_n_items = [np.argsort(item_sim_arr[:, col])[:-n - 1:-1]]
      # 개인화된 예측 평점 계산 : 각 col 맥주별(1개), 2496 사용자들의 예측평점
      for row in range(ratings_arr.shape[0]):
          pred[row, col] = item_sim_arr[col, :][top_n_items].dot(
              ratings_arr[row, :][top_n_items].T)
          pred[row, col] /= np.sum(item_sim_arr[col, :][top_n_items])

  return pred

# 사용자가 안 먹어본 맥주를 추천하자.
def get_not_tried_beer(ratings_matrix, userId):
  # userId로 입력받은 사용자의 모든 맥주 정보를 추출해 Series로 반환
  # 반환된 user_rating은 영화명(title)을 인덱스로 가지는 Series 객체
  user_rating = ratings_matrix.loc[userId, :]

  # user_rating이 0보다 크면 기존에 관란함 영화.
  # 대상 인덱스를 추출해 list 객체로 만듦
  tried = user_rating[user_rating > 0].index.tolist()

  # 모든 맥주명을 list 객체로 만듦
  beer_list = ratings_matrix.columns.tolist()

  # list comprehension으로 tried에 해당하는 영화는 beer_list에서 제외
  not_tried = [beer for beer in beer_list if beer not in tried]

  return not_tried

# 예측 평점 DataFrame에서 사용자 id 인덱스와 not_tried로 들어온 맥주명 추출 후
# 가장 예측 평점이 높은 순으로 정렬
def recomm_beer_by_userid(pred_df, userId, not_tried, top_n):
  recomm_beer = pred_df.loc[userId, not_tried].sort_values(ascending=False)[:top_n]
  return recomm_beer

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

@recomm.route('/ver2')
@login_required
def ver2():
  beer_list = pd.read_csv('맥주이름.csv', encoding='utf-8', index_col=0)
  beer_year = pd.read_csv('맥주_연도별평점.csv', encoding='utf-8', index_col=0)
  ratings = pd.read_csv('정제된데이터.csv', encoding='utf-8', index_col=0)
  cluster_3 = pd.read_csv('대표군집클러스터링.csv', encoding='utf-8', index_col=0)
  cluster_all = pd.read_csv('전체맥주클러스터링.csv', encoding='utf-8', index_col=0)
  beer_list = beer_list['맥주']
  cluster_3 = cluster_3.values

  count =  Rate.query.filter(Rate.user_name == current_user.name).count()
  beers = Rate.query.filter_by(user_name=current_user.name).with_entities(Rate.beer).all()
  ratings_1 = Rate.query.filter_by(user_name=current_user.name).with_entities(Rate.rating).all()
  
  return render_template('ver2.html')
