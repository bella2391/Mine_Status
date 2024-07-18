import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks
import mysql.connector
from discord import app_commands
load_dotenv('C://Users/maeka/PHP/.env')

TOKEN=os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)


@tasks.loop(seconds = 10)
async def myLoop():
   conn = None
   try:
      conn = mysql.connector.connect(
         host=os.getenv("DB_HOST"),
         user=os.getenv("DB_USER"),
         password=os.getenv("DB_PASS"),
         database=os.getenv("DB_NAME")
      )

      if conn.is_connected:
         pass
      if not conn.is_connected():
         raise Exception("データベースサーバへの接続に失敗しました")
      embed = discord.Embed(title=f"Server Status", description="", color=discord.Color.green())
      cursor = conn.cursor()

      servers_str = ""
      players_str = ""
      playernums_str = ""
      columns_list = []
      servers = []
      servers.append(dict(name="Bungeecord",port=os.getenv("Bungeecord_SERVER_PORT")))
      #servers.append(dict(name="Velocity",port=os.getenv("Velocity_SERVER_PORT")))
      servers.append(dict(name="Home",port=os.getenv("Home_SERVER_PORT")))
      servers.append(dict(name="Latest",port=os.getenv("Latest_SERVER_PORT")))
      servers.append(dict(name="La_Test",port=os.getenv("La_Test_SERVER_PORT")))
      servers.append(dict(name="RLCraft",port=os.getenv("RLCraft_SERVER_PORT")))
      servers.append(dict(name="Gun",port=os.getenv("Gun_SERVER_PORT")))
      servers.append(dict(name="Multi_Isekai",port=os.getenv("Multi_Isekai_SERVER_PORT")))
      servers.append(dict(name="DungeonF",port=os.getenv("DungeonF_SERVER_PORT")))
      servers.append(dict(name="Vanilla",port=os.getenv("Vanilla_SERVER_PORT")))
      servers.append(dict(name="La_Test2",port=os.getenv("La_Test2_SERVER_PORT")))
      servers.append(dict(name="HardCore",port=os.getenv("HardCore_SERVER_PORT")))
      
      i=0
      while i<len(servers):
        servers_str += f"{servers[i]["name"]},"
        players_str += f"{servers[i]["name"]}_player_list,"
        playernums_str += f"{servers[i]["name"]}_current_players,"
        columns_list.append(servers[i]["name"])
        i=i+1
      servers_str = servers_str[:-1]
      players_str = players_str[:-1]
      playernums_str = playernums_str[:-1]
      stmt=f"SELECT {servers_str} FROM mine_status WHERE id={1};"
      cursor.execute(stmt)
      onoffs = cursor.fetchall()
      conn.commit()
      stmt=f"SELECT {players_str} FROM mine_status WHERE id={1};"
      cursor.execute(stmt)
      players = cursor.fetchall()
      conn.commit()
      stmt=f"SELECT {playernums_str} FROM mine_status WHERE id={1};"
      cursor.execute(stmt)
      playernums = cursor.fetchall()
      conn.commit()
      for name, onoff, player,playernum in zip(columns_list,onoffs[0],players[0],playernums[0]):
        if int(onoff) == 1:
          if player == "":
            player = "No Player"
          embed.add_field(name=":green_circle:%s" % (name),value="%s/%s: %s" % (playernum,10,player),inline=False)
      status_channel = client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
      status_message = await status_channel.fetch_message(int(os.getenv("DISCORD_MSG_ID")))
      await status_message.edit(embed=embed)
      cursor.close()
   except Exception as e:
      print(f"Error Occurred: {e}")

   finally:
      if conn is not None and conn.is_connected():
         conn.close()

@client.event
async def on_ready():
 await client.change_presence(activity=discord.Game(name="Status Updating..."))
 await tree.sync()
 print("login complete")
 myLoop.start()

client.run(TOKEN)
