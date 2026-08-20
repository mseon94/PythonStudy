from flask import Flask

# Flask 애플리케이션 객체 생성
app = Flask(__name__)

# 라우팅(Routing) 설정
@app.route("/")
def hello_world():
    return "Hello, World!"

# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)     # debug = True는 개발 오류 발생 시 자세한 정보 제공