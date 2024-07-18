import os
from dotenv import load_dotenv
import datetime
import minestat
import mysql.connector

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

      if conn.is_connected:
         pass
      if not conn.is_connected():
         raise Exception("データベースサーバへの接続に失敗しました")
      cursor = conn.cursor()
      status = ""
      param = []
      servers = []
      dbcolumns_list = []
      tables = ""
      tables2 = ""
      ttt = ""
      online = ""
      online += "オンラインサーバー:\n"
      offline = "オフラインサーバー:\n"
      servers.append(dict(name="Server1",port=os.getenv("Server1_SERVER_PORT")))
      servers.append(dict(name="Server2",port=os.getenv("Server2_SERVER_PORT")))
      
      stmt=f"SHOW COLUMNS FROM mine_status;"
      cursor.execute(stmt)
      columns = cursor.fetchall()
      conn.commit()
      i=0
      while i<len(columns):
         dbcolumns_list.append(columns[i][0])
         i=i+1
      columns_list = []
      i=0
      while i<len(servers):
         columns_list.append(servers[i]["name"])
         i=i+1
      i=0
      while i<len(servers):
         code = f"ms_{servers[i]["name"]} = minestat.MineStat('{os.getenv("HOST")}',{servers[i]['port']})"
         exec(code)
         i=i+1
      i=0
      while i<(len(servers)):
         if not servers[i]["name"] in dbcolumns_list:
            print(f"{servers[i]["name"]}をカラムに追加しました。")
            tables += "%s %s default 0," % (servers[i]["name"],"BOOLEAN")
            tables += "%s %s default 0," % (f"{servers[i]["name"]}_current_players","text")
            tables += "%s %s default 0," % (f"{servers[i]["name"]}_player_list","text")

         if eval(f"ms_{servers[i]["name"]}") and eval(f"ms_{servers[i]["name"]}.current_players")!=None:
            bb = str(eval(f"ms_{servers[i]["name"]}.player_list"))[2:-2]
            bb = bb.replace("'","")
            online += f"   {servers[i]["name"]}:\n"
            online += f"      {str(eval(f"ms_{servers[i]["name"]}.current_players"))}/10: {bb}\n"

            param.append(1)

            status += "%s=%s," % (servers[i]["name"], True)
            status += "%s='%s'," % (f"{servers[i]["name"]}_player_list",bb)
            status += "%s='%s'," % (f"{servers[i]["name"]}_current_players",str(eval(f"ms_{servers[i]["name"]}.current_players")))

         else:
            offline += f"  {servers[i]["name"]}\n"
            param.append(0)
            status += "%s=%s," % (servers[i]["name"], False)
            status += "%s='%s'," % (f"{servers[i]["name"]}_player_list",str(eval(f"ms_{servers[i]["name"]}.player_list")))
            status += "%s='%s'," % (f"{servers[i]["name"]}_current_players",str(eval(f"ms_{servers[i]["name"]}.current_players")))

         if i==len(servers)-1:
            status = status[:-1]
            if tables!="":
               tables = tables[:-1]
               stmt = (f'''ALTER table mine_status add column ({tables});''')
               print(stmt)
               cursor.execute(stmt)
               conn.commit()
         i=i+1
      print(online)
      print(offline)
      dt_now = datetime.datetime.now()
      print(dt_now.strftime('%Y年%m月%d日 %H:%M:%S'))
      stmt = (f'''UPDATE mine_status SET {status} WHERE id={1};''')
      cursor.execute(stmt)
      conn.commit()
      cursor.close()
   except Exception as e:
      print(e)

   finally:
      if conn is not None and conn.is_connected():
         conn.close()
