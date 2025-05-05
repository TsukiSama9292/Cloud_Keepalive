import valkey
from valkey import exceptions
import argparse
from datetime import datetime
import sys

def main():
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="Valkey Keepalive Script")
    parser.add_argument("--user", required=True, help="Valkey username")
    parser.add_argument("--password", required=True, help="Valkey password")
    parser.add_argument("--host", required=True, help="Valkey host")
    parser.add_argument("--port", type=int, required=True, help="Valkey port")
    args = parser.parse_args()

    valkey_client = None
    try:
        # 建立 valkey URI 並連線
        valkey_uri = f'valkeys://{args.user}:{args.password}@{args.host}:{args.port}'
        valkey_client = valkey.from_url(valkey_uri, socket_timeout=10)

        # 設定或更新 keepalive key
        key_name = 'github_keepalive'
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        valkey_client.set(key_name, current_time)
        key_value = valkey_client.get(key_name).decode('utf-8')
        print(f"✅ Valkey Keepalive Key-Value Updated.")

    except exceptions.ConnectionError as e:
        print(f"⚠️ Valkey 連線錯誤: {e}")   # ConnectionError 來自 valkey.exceptions.ConnectionError :contentReference[oaicite:0]{index=0}
        sys.exit(1)
    except exceptions.AuthenticationError as e:
        print(f"⚠️ Valkey 驗證錯誤: {e}")   # AuthenticationError 來自 valkey.exceptions.AuthenticationError :contentReference[oaicite:1]{index=1}
        sys.exit(1)
    except exceptions.ValkeyError as e:
        print(f"⚠️ 發生 Valkey 通用錯誤: {e}")  # ValkeyError 為所有 Valkey 例外的基底 :contentReference[oaicite:2]{index=2}
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ 發生未預期的錯誤: {e}")
        sys.exit(1)
    finally:
        if valkey_client:
            valkey_client.close()

if __name__ == '__main__':
    main()
