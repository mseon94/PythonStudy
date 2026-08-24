import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# streamlit 기본 환경 설정
st.set_page_config(
    page_title="퇴사율 예측 및 대시보드",
    layout="wide"
)

# Matplotlib 한글 폰트 및 마이너스 기호 설졍
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 모델 및 전처리 객체 불러오기
@st.cache_resource
def load_ml_objects():
    try:
        encoder = joblib.load("model/left_encoder.joblib")
        scaler = joblib.load("model/left_scaler.joblib")
        model = joblib.load("model/left_model.joblib")
        meta = joblib.load("model/features_meta.joblib")
        
        return encoder, scaler, model, meta
    
    except FileNotFoundError as error:
        st.error(
            f"모델 또는 전처리 객체 파일을 찾을 수 없습니다.\n\n"
            f"오류 내용: {error}"
        )
        st.stop()
        
# 시각화용 원본 데이터 불러오기
@st.cache_data
def load_raw_data():
    try:
        df = pd.read_csv("dataset/HR_comma_sep.csv", encoding="cp949")
    
        # 컬럼명의 오타와 불필요한 공백 수정
        df = df.rename(
            columns={
                "Departments ": "Departments",
                "average_montly_hours": "average_monthly_hours",
                "time_spend_company": "time_spent_company",
                "Work_accident": "work_accident"
            }
        )
        
        return df

    except FileNotFoundError as error:
        st.error(
            f"원본 데이터 파일을 찾을 수 없습니다.\n\n"
            f"오류 내용: {error}"
        )
        st.stop()
        
        
# 모델 및 데이터 로드
encoder, scaler, model, meta = load_ml_objects()
df = load_raw_data()

# 모델 학습 당시 사용한 컬럼 정보
numeric_features = meta["numeric_cols"]
categorical_features = meta["categorical_cols"]

# 인코딩 후 전체 특성명
encoded_feature_names = list(
    encoder.get_feature_names_out(categorical_features)
)

all_feature_names = (
    list(numeric_features) + encoded_feature_names
)

def preprocess_input(input_df):
    # 범주형 변수 원핫인코딩
    encoded_values = encoder.transform(
        input_df[categorical_features]
    )
    
    # 인코딩된 컬럼명 가져오기
    encoded_columns = encoder.get_feature_names_out(
        categorical_features
    )
    
    encoded_df = pd.DataFrame(
        encoded_values,
        columns=encoded_columns,
        index=input_df.index
    )
    
    # 수치형 변수와 원핫인코딩 결과 결합
    processed_df = pd.concat(
        [
            input_df[numeric_features].reset_index(drop=True),
            encoded_df.reset_index(drop=True)
        ], axis=1
    )
    
    # 저장된 스케일러로 변환
    scaled_input = scaler.transform(processed_df)
    
    return scaled_input



# 메인 화면
st.title("퇴사율 예측 및 대시보드")
st.write(
    """
    직원의 세부 정보를 입력하여 퇴사 가능성을 과학적으로 예측하고 HR 인사이트를 분석합니다.
    """
)

# 메인 탭 구성
simulator_tab, dashboard_tab = st.tabs(
    [
        "퇴사 위험도 시뮬레이터",
        "데이터 인사이트 대시보드"
    ]
)

with simulator_tab:
    st.subheader("퇴사 위험도 시뮬레이터")
    
    # 화면 분할
    input_col, result_col = st.columns([2, 1.1])
    
    # 왼쪽 : 사용자 입력
    with input_col:
        st.markdown("#### 직원 정보 입력")

        satisfaction_level = st.slider(
            "만족도", 
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01
        )
        
        last_evaluation = st.slider(
            "평가 점수", 
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01
        )
        
        number_project = st.number_input(
            "프로젝트 수",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )
        
        average_monthly_hours = st.number_input(
            "월 평균 근무 시간",
            min_value=50,
            max_value=400,
            value=200,
            step=1
        )
        
        time_spent_company = st.number_input(
            "근속 연수",
            min_value=1,
            max_value=20,
            value=3,
            step=1
        )
        
        work_accident = st.selectbox(
            "사고 유무",
            options=[0, 1],
            format_func=lambda value: "사고 없음" if value == 0 else "사고 있음"
        )
        
        promotion_last_5years = st.selectbox(
            "최근 5년 내 승진 여부",
            options=[0, 1],
            format_func=lambda value: "승진 없음" if value == 0 else "승진 있음"
        )
        
        department = st.selectbox(
            "부서",
            options=(df["Departments"].dropna().unique())
        )
        
        salary = st.selectbox(
            "급여 수준",
            options=df["salary"].dropna().unique()
        )
    
    # 오른쪽 : 예측 결과
    with result_col:
        st.markdown("#### 예측 결과")
        predict_button = st.button(
            "퇴사 예측",
            type="primary",
            use_container_width=True
        )
        
        if predict_button:
            # 사용자 입력 값을 1행짜리 DataFrame으로 생성
            input_df = pd.DataFrame(
                {
                    "satisfaction_level": [satisfaction_level],
                    "last_evaluation": [last_evaluation],
                    "number_project": [number_project],
                    "average_monthly_hours": [
                        average_monthly_hours
                    ],
                    "time_spent_company": [
                        time_spent_company
                    ],
                    "work_accident": [work_accident],
                    "promotion_last_5years": [
                        promotion_last_5years
                    ],
                    "Departments": [department],
                    "salary": [salary]
                }
            )
            
            # 인코딩 및 스케일링
            scaled_input = preprocess_input(input_df)
            
            # 퇴사 여부와 확률 예측
            prediction = model.predict(scaled_input)[0]
            probabilities = model.predict_proba(scaled_input)[0]

            if prediction == 1:
                st.metric(
                    label="예측 상태",
                    value="퇴사 위험"
                )

                st.error(
                    f"퇴사 가능성이 높은 직원으로 예측되었습니다.\n\n"
                    f"퇴사 위험도: {probabilities[1]:.1%}"
                )

            else:
                st.metric(
                    label="예측 상태",
                    value="재직 유지"
                )

                st.success(
                    f"재직을 유지할 가능성이 높은 직원으로 예측되었습니다.\n\n"
                    f"재직 유지 확률: {probabilities[0]:.1%}"
                )

        else:
            st.info(
                "직원 정보를 입력한 후 '퇴사 예측' 버튼을 눌러주세요."
            )
            
    
with dashboard_tab:
    st.subheader("데이터 인사이트 대시보드")

    importance_tab, analysis_tab, tenure_tab = st.tabs(
        [
            "AI 특성 중요도 분석",
            "만족도 및 프로젝트 분석",
            "근속 연수 분포"
        ]
    )

    # AI 특성 중요도 분석
    with importance_tab:
        st.markdown("#### 퇴사 예측 특성 중요도 상위 10개")

        importance_df = pd.DataFrame(
            {
                "feature": all_feature_names,
                "importance": model.feature_importances_
            }
        )

        top_features = (
            importance_df
            .sort_values(
                by="importance",
                ascending=False
            )
            .head(10)
        )

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=top_features,
            x="importance",
            y="feature",
            color="steelblue",
            ax=ax
        )

        ax.set_title("퇴사 예측 특성 중요도 상위 10개")
        ax.set_xlabel("특성 중요도")
        ax.set_ylabel("특성명")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # 그래프 표시용 데이터
    chart_df = df.copy()

    chart_df["left_label"] = chart_df["left"].map(
        {
            0: "재직",
            1: "퇴사"
        }
    )

    # 만족도 및 프로젝트 분석
    with analysis_tab:
        satisfaction_col, project_col = st.columns(2)

        with satisfaction_col:
            st.markdown("#### 만족도별 퇴사 여부")

            fig, ax = plt.subplots(figsize=(6, 5))

            sns.boxplot(
                data=chart_df,
                x="left_label",
                y="satisfaction_level",
                ax=ax
            )

            ax.set_title("퇴사 여부에 따른 만족도 분포")
            ax.set_xlabel("퇴사 여부")
            ax.set_ylabel("만족도")

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with project_col:
            st.markdown("#### 프로젝트 수별 퇴사 현황")

            fig, ax = plt.subplots(figsize=(6, 5))

            sns.countplot(
                data=chart_df,
                x="number_project",
                hue="left_label",
                ax=ax
            )

            ax.set_title("프로젝트 수별 퇴사 현황")
            ax.set_xlabel("프로젝트 수")
            ax.set_ylabel("직원 수")
            ax.legend(title="퇴사 여부")

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    # 근속 연수 분포
    with tenure_tab:
        st.markdown("#### 근속 연수별 퇴사자 적층 분포")

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.histplot(
            data=chart_df,
            x="time_spent_company",
            hue="left_label",
            multiple="stack",
            discrete=True,
            ax=ax
        )

        ax.set_title("근속 연수별 재직 및 퇴사 직원 분포")
        ax.set_xlabel("근속 연수")
        ax.set_ylabel("직원 수")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)