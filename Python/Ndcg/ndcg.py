import os
from pathlib import Path

import numpy as np
import csv

# nDCG(normalized Discounted Cumulative Gain) 알고리즘
# 랭킹기반 추천시스템 평가지표 알고리즘
# 관련성이 높은 결과를 상위권에 노출시켰는지 체크
# 검색엔진, 영상추천, 음악추천 등의 다양한 추천시스템에서 평가지표로 활용


# 랭킹 순서에 따라 점점 비중을 줄여 discounted 관련도를 계산하는 방법
# 랭킹 순서에 대한 로그함수를 분모로 두면, 하위권으로 갈수록 Rel 대비 작은 DCG 값을 가짐
# 하위권 결과에 패널티를 주는 방식
def dcg_score(y_true, y_score, k = 20, gains = "linear"):
    # 내림차순으로 관련 스코어 값 정렬
    order = np.argsort(y_score) [::-1]
    # 정렬된 스코어 값과 매칭 되도록 실제 수치값도 정렬
    y_true = np.take(y_true, order [: k])

    # 랭킹의 순서보다 관련성에 더 비중을 주고싶은 경우 사용
    if gains == "exponential":
        gains = 2 ** y_true-1
    # 랭킹의 순서에 더 비중을 두고 평가하는 경우 사용
    elif gains == "linear":
        gains = y_true # 수식에서 분모가 되는 수열을 gains에 저장
    else:
        raise ValueError("Invalid gains option.") # 예외 상황 처리

    # 수식: SUM (i->p) { Rel i / log2(i+1) } 코드 구현부
    # 분모가 되는 log2(i+1) 수열 생성, 수식에서 i는 1부터 시작하지만, 코드 구현상 i는 0부터 시작하는 경우를 대비해 +2, 결과값은 같음
    discounts = np.log2(np.arange(len (y_true)) + 2)
    # Rel i 수열과 log2(i+1) 수열을 순서대로 나누기 연산을 하여 합산
    return np.sum(gains / discounts)

def ndcg_score(y_true, y_score, k = 20, gains = "linear"):
    # DCG(p) = 랭킹 순서에 따라 점점 비중을 줄여 discounted 관련도 계산
    best = dcg_score(y_true, y_true, k, gains)
    # IDCG(p) = y_score가 큰 순서대로 재배열한 후, 순서에 따라 점점 비중을 줄여 discounted 관련도 계산
    actual = dcg_score(y_true, y_score, k, gains)
    return actual / best # nDCG(p) = DCG(p) / IDCG(p) 연산

# 프로세스 시작
# 파일오픈 > 배열변환 > DCG 연산 > NDCG 연산
with open(Path.joinpath(Path.cwd(), "testing_account.csv"), 'r') as file:
    # 파일 오픈 및 리딩 준비
    csvreader = csv.DictReader(file)
    # 파일 리딩 시작, 라인별로 파일을 읽어서 변수에 저장
    for row in csvreader:
        # 실제 결과 저장
        true_relevanceArr = [row['scope1'], row['scope2'], row['scope3'], row['scope4'], row['scope5'], row['scope6'],
                             row['scope7'], row['scope8'], row['scope9'], row['scope10'], row['scope11'],
                             row['scope12'], row['scope13'], row['scope14'], row['scope15'], row['scope16'],
                             row['scope17'], row['scope18'], row['scope19'], row['scope20']]
        # 관련도 값 저장
        relevance_scoreArr = [row['survey1'], row['survey2'], row['survey3'], row['survey4'], row['survey5'],
                              row['survey6'], row['survey7'], row['survey8'], row['survey9'], row['survey10'],
                              row['survey11'], row['survey12'], row['survey13'], row['survey14'], row['survey15'],
                              row['survey16'], row['survey17'], row['survey18'], row['survey19'], row['survey20']]

        # 배열로 변환
        true_relevance = np.asarray(true_relevanceArr)
        relevance_score = np.asarray(relevance_scoreArr)

        # 배열의 값들을 실제 연산에 사용하기 위해 float(소수점) 형태로 타입 정의
        true_relevance = np.array(true_relevance, dtype=float)
        relevance_score = np.array(relevance_score, dtype=float)

        # NDCG - 실제값과 관련도 값을 통해 추천 평가지표 연산 함수 호출
        ns = ndcg_score(true_relevance, relevance_score)
        # ID값과 ns(ndcg_score) 출력
        print("nDCG score (from function) : ", row['ID'], ns)
