import pymysql
from datetime import datetime
import argparse
import sys  # 導入 sys 模組以便在錯誤發生時退出程式

def main():
    # 設定 argparse
    parser = argparse.ArgumentParser(description="MySQL Keepalive Script")
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--host", required=True, help="MySQL host")
    parser.add_argument("--password", required=True, help="MySQL password")
    parser.add_argument("--port", type=int, required=True, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL user")
    args = parser.parse_args()

    connection = None  # 初始化 connection 為 None
    timeout = 10
    try:
        # 建立連線
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            db=args.db,
            host=args.host,
            password=args.password,
            port=args.port,
            user=args.user,
            read_timeout=timeout,
            write_timeout=timeout,
        )

        with connection.cursor() as cursor:
            # 建立 keepalive 表格（如尚未存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keepalive (
                    source VARCHAR(255) PRIMARY KEY,
                    create_time DATETIME NOT NULL
                )
            """)

            # 插入或更新 github 的時間
            cursor.execute("""
                INSERT INTO keepalive (source, create_time)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE create_time = VALUES(create_time)
            """, ("github", datetime.now()))

            connection.commit()
            print("✅ MySQL Keepalive Table Updated.")

    except pymysql.err.OperationalError as e:
        print(f"⚠️ MySQL 連線或操作錯誤: {e}")
        print("⚠️ 請檢查資料庫伺服器是否運行中，網路連線是否正常，以及提供的 host 和 port 是否正確。")
        sys.exit(1)
    except pymysql.err.ProgrammingError as e:
        print(f"⚠️ MySQL SQL 語法錯誤: {e}")
        print("⚠️ 請檢查 SQL 語法是否正確，以及資料庫和表格是否存在。")
        sys.exit(1)
    except pymysql.err.IntegrityError as e:
        print(f"⚠️ MySQL 資料完整性錯誤: {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    except pymysql.err.InternalError as e:
        print(f"⚠️ MySQL 內部錯誤: {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ 發生未預期的錯誤: {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    main()