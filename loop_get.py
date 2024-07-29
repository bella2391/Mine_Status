import os
import datetime
import minestat
import mysql.connector
from dotenv import load_dotenv

load_dotenv('~/.env')

while True:
    conn = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )

        if not conn.is_connected():
            raise Exception("データベースサーバへの接続に失敗しました")

        cursor = conn.cursor()
        servers = []
        online = "オンラインサーバー:\n"
        offline = "オフラインサーバー:\n"

        stmt = "SELECT name, port FROM mine_status WHERE exception2!=%s;" % True
        cursor.execute(stmt)
        status = cursor.fetchall()

        for row in status:
            name = row[0]
            port = row[1]
            servers.append(dict(name=name, port=port))

        minestats = []
        host = os.getenv("HOST")  # ホストの取得
        for server in servers:
            ms = minestat.MineStat(host, server["port"])  # サーバーのポートを使用してインスタンスを作成
            minestats.append(ms)

        for i, ms in enumerate(minestats):
            server = servers[i]
            name = server["name"]
            if ms and ms.current_players is not None:
                player_list = ms.player_list
                if isinstance(player_list, list):  # player_list がリストであることを確認
                    bb = ', '.join(player_list)
                else:
                    bb = str(player_list)  # player_list がリストでない場合は、そのまま文字列化
                online += f"   {name}:\n"
                online += f"      {ms.current_players}/10: {bb}\n"

                stmt = "UPDATE mine_status SET online=%s, player_list=%s, current_players=%s WHERE name=%s;"
                param = (True, bb, ms.current_players, name)
                cursor.execute(stmt, param)
                conn.commit()
            else:
                offline += f"  {name}\n"
                stmt = "UPDATE mine_status SET online=%s, player_list=NULL, current_players=NULL WHERE name=%s;"
                param = (False, name)
                cursor.execute(stmt, param)
                conn.commit()

        print(online)
        print(offline)
        dt_now = datetime.datetime.now()
        print(dt_now.strftime('%Y年%m月%d日 %H:%M:%S'))

        cursor.close()
    except Exception as e:
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()
