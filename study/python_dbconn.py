import pymysql

def connect_to_mysql(host, port, user, password, database):
    """
    PyMySQL을 사용하여 MariaDB 데이터베이스에 연결하는 함수
    
    Args:
        host (str): MariaDB 서버 호스트 주소.
        port (int): MariaDB 서버 포트 번호.
        user (str): MariaDB 사용자 이름.
        password (str): MariaDB 사용자 비밀번호.
        database (str): 연결할 데이터베이스 이름.

    Returns:
        pymysql.Connection: MySQL 연결 객체 (성공 시).
        None: 연결 실패 시.
    """
    
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"MySQL 데이터베이스 '{database}에 성공적으로 연결되었습니다.")
        return conn
    except pymysql.MySQLError as e:
        print(f"MySQL 연결 오류: {e}")
        return None
    
if __name__ == '__main__':
    # 데이터베이스 연결 정보
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "1111"
    DB_DATABASE = "test"
    
    # 데이터베이스 연결 시도
    conn = connect_to_mysql(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE)
    
    if conn:
        try:
            with conn.cursor() as cs:
                sql = "SELECT VERSION()"
                cs.execute(sql)
                result = cs.fetchone()
                print(f"MariaDB 버전: {result}")
        
        except pymysql.MySQLError as e:
            print(f"데이터베이스 작업 오류: {e}")
        finally:
            # [중요!!] 연결 종료 - with 문을 사용해서 커서를 닫으면 conn.close()만 필요
            if conn:
                conn.close()
                print("MariaDB 연결이 종료되었습니다.")