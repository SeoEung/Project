from django.shortcuts import render
import pandas as pd
from django.db.models import Count
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

# DB에 저장되어 있는 데이터 불러오는 코드

def conn() :
    conn = sqlite3.connect("../db.sqlite3", isolation_level=None)
    c = conn.cursor()
    return c

def sel_df() :
    con = conn()
    sql = "select * from main_movies"
    con.execute(sql)
    res = con.fetchall()
    # print(type(pd.DataFrame(res)))
    M= pd.DataFrame(res)
    return pd.DataFrame(res)
# sel_df()

# movies 데이터를 위 'sel_df()' 함수를 사용해서 데이터 프레임으로 불러오기
movies= pd.DataFrame(sel_df())
# print(data)

# 불러 온 데이터의 컬럼명을 재설정해준 후 원본 적용
movies.rename(columns= {0: 'movieId', 1: 'title', 2: 'genres'},
              inplace= True)
# print(movies)

# 불러 온 movies 데이터를 movies1 데이터로 copy
movies1= movies.copy()

# print(movies1)
# movies1.to_csv('moviedata.csv')

# copy 한 movies1 데이터의 인덱스를 movieId 로 set_index 후 원본 적용
movies1.set_index('movieId', inplace= True)
# print(movies1)



# 파이썬 객체 변환을 위한 함수 선언 후 적용
# 파이썬에서 사용 data 의 genre 를 사용할 수 있도록

def transform(a):
    return a.split('|')

movies['genres']= movies['genres'].apply(transform)

# 앞서 객체 변환시킨 data를 genres_literal로 넣어줌
movies['genres_literal']= movies['genres'].apply(lambda x : (' ').join(x))

# 데이터 피쳐의 벡터화

count_vect= CountVectorizer(min_df= 0)
genre_mat= count_vect.fit_transform(movies['genres_literal'])

# 코사인 유사도 계산
# 장르 간 유사도를 계산하기 위해 사용

genre_sim= cosine_similarity(genre_mat, genre_mat)
# print(genre_sim)

# 앞서 계산 된 장르 유사도를 Genre_sim 에 데이터프레임 형태로 저장 / 컬럼과 인덱스는 영화의 제목으로 설정
Genre_sim= pd.DataFrame(data= genre_sim, columns= movies.title, index= movies.title)
Genre_sim = Genre_sim.reset_index()
# print(Genre_sim)

# movieId_sim= Genre_sim.copy()
# print(movieId_sim)


# 장르가 유사한 영화 movieId 반환 함수 구현

def REC(movieId, Genre_sim=Genre_sim):
    choice = []

    # 위 전처리에서 copy 한 movies1 데이터에서 movieId 와 title 을 추출
    movies1.loc[movieId, 'title']
    # title 은 위에서 추출한 movieId 와 title 저장
    title= movies1.loc[movieId, 'title']

    # 모든 영화에 대한 해당 영화의 유사도 계산
    sim_scores = list(enumerate(Genre_sim[title]))
    # print(Genre_sim[title])
    # print(sim_scores)

    # 유사도에 따라 영화 정렬
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 가장 유사한 10개의 영화 받아옴
    sim_scores = sim_scores[0:10]

    # 가장 유사한 10개 영화의 인덱스를 추출
    movie_indices = [i[0] for i in sim_scores]

    # return sim_scores

    # for 문을 이용해 유사도 테이블의 제목을 이용해 유사한 10개 영화의 인덱스 추출 후 b에 저장
    # 반환받을 a에 앞서 추출 한 10개 영화의 인덱스를 append 해준다
    a= []
    b= Genre_sim['title'].iloc[movie_indices]
    for i in b:
        a.append(i)
    # print(a)

    # 최종적으로 반환되는 a 는 영화의 movieId
    return a

# print(REC(99165))

# 위 함수를 통해 반환받은 movieId 값을 통해 영화를 추천해주는 함수 구현

def rec1(movieId):

    # result 값은 딕셔너리로 형태로 반환받음
    result= {}

    # 입력 받은 movieId 를 바탕으로 위에서 구현한 함수에 id 값으로 반환받은 값을 s 에 저장
    for id in movieId:
        s= REC(id)
        # 딕셔너리 result 값의 리스트 id 값은 s 와 같다는 것을 선언
        result[id]= s

    # print(s)

    # 반환 받을 b 값은 딕셔너리 형태로 받아준다 / key 와 value 값의 용이한 분리 위해
    b = {}

    # 앞서 반환 받은 result 값의 벨류값을 value 로 뽑아준다
    for value in result.values():
        # value 값 중 i 를 뽑아내어
        for i in value:
            # T 값에 movies 데이터의 title 리스트를 i 와 같다고 선언
            T = movies[movies['title'] == i]
            # 앞서 저장한 T 에 movieId를 리스트 값으로 b에 반환
            b[i] = ((T.movieId.tolist()[0]))
    return b

# print(rec1([99165]))
# print(rec1([99165, 104114, 158371]))

# rec1 함수에 movieId 가 입력되면 그에 맞는 영화가 각각 10개씩 추천되어짐
print(list(rec1([99165, 104114, 158371]).values()))

# print(dic)

# b= {}
# for value in dic.values():
#     for i in value:
#         T = movies[movies['title'] == i]
#         b[i]= ((T.movieId.tolist()[0]))

# i= 'Kid The (1921)'
# T = movies1[movies1['title'] == i]
# print(T)
# print(movies)

# print(b)