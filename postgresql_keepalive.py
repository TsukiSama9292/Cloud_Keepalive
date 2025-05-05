import psycopg2
from psycopg2 import sql
from datetime import datetime
import argparse
import sys

def main():
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="PostgreSQL Keepalive Script")
    parser.add_argument("--db", required=True, help="Database name")
    parser.add_argument("--host", required=True, help="Database host")
    parser.add_argument("--port", type=int, required=True, help="Database port")
    parser.add_argument("--user", required=True, help="Database user")
    parser.add_argument("--password", required=True, help="Database password")
    args = parser.parse_args()

    conn = None  # 初始化 conn 為 None
    try:
        # 建立連線
        conn = psycopg2.connect(
            dbname=args.db,
            user=args.user,
            password=args.password,
            host=args.host,
            port=args.port,
            connect_timeout=10
        )
        conn.autocommit = True

        with conn:
            with conn.cursor() as cur:
                # 建立 keepalive 資料表（若尚未存在）
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS keepalive (
                        source TEXT PRIMARY KEY,
                        create_time TIMESTAMP NOT NULL
                    )
                """)

                # 插入或更新 github 的時間
                cur.execute("""
                    INSERT INTO keepalive (source, create_time)
                    VALUES (%s, %s)
                    ON CONFLICT (source)
                    DO UPDATE SET create_time = EXCLUDED.create_time
                """, ("github", datetime.now()))

                print("✅ PostgreSQL Keepalive Table Updated.")

    except psycopg2.OperationalError as e:
        print(f"⚠️ PostgreSQL 連線或操作錯誤 (Operational): {e}")
        print("⚠️ 請檢查資料庫伺服器是否運行中，網路連線是否正常，以及提供的 host 和 port 是否正確。")
        sys.exit(1)
    except psycopg2.ProgrammingError as e:
        print(f"⚠️ PostgreSQL SQL 語法錯誤 (Programming): {e}")
        print("⚠️ 請檢查 SQL 語法是否正確，以及資料庫和表格是否存在。")
        sys.exit(1)
    except psycopg2.IntegrityError as e:
        print(f"⚠️ PostgreSQL 資料完整性錯誤 (Integrity): {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    except psycopg2.InternalError as e:
        print(f"⚠️ PostgreSQL 內部錯誤 (Internal): {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    except psycopg2.DataError as e:
        print(f"⚠️ PostgreSQL 資料錯誤 (Data): {e}")
        print(f"⚠️ 請檢查輸入的資料格式是否正確。")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"⚠️ 發生未預期的 PostgreSQL 錯誤: {e}")
        print(f"⚠️ 錯誤詳細資訊: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()