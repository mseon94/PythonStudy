import pandas as pd
import numpy as np
import joblib
import streamlit as st

# 저장된 모델 불러오기
model = joblib.load('../model/diabetes_model.pkl')

# streamlit 앱
st.title('당뇨병 예측 시스템')
st.write('Glucose, BMI, Age 값을 입력하여 당뇨병 예측을 해보세요')

# 사용자 입력받기``
glucose = st.slider(
    'Glucose(혈당수치)',
    min_value=0,
    max_value=200,
    value=100
)

bmi = st.slider(
    'BMI(체질량지수)',
    min_value=0.0,
    max_value=50.0,
    value=25.0,
    step=0.1
)

age = st.slider(
    'Age(나이)',
    min_value=0,
    max_value=100,
    value=30
)

# 예측하기 버튼
if st.button('예측하기'):
    # 입력값을 모델에 전달
    input_data = np.array([
        [glucose, bmi, age]
    ])
    
    prediction = model.predict(input_data)[0]
    
    # 결과 출력
    if prediction == 1:
        st.write("예측 결과: 당뇨병 가능성이 높습니다.")
    else:
        st.write("예측 결과: 당뇨병 가능성이 낮습니다.")