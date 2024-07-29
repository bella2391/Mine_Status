import os
import sys
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import tasks
import mysql.connector
from discord import app_commands
load_dotenv('~/.env')

TOKEN=os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)


@tasks.loop(seconds = 20)
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
        cursor = conn.cursor(dictionary=True)
        onlineservers = []
        maintenance = False

        stmt = "SELECT * FROM mine_status;"
        cursor.execute(stmt)
        status = cursor.fetchall()
        #print(status)

        for row in status:
            name = row["name"]
            online = row["online"]
            if online:
                # MaintenanceのonlineカラムがTrueなら
                if name == "Maintenance":
                    maintenance = True
                    break
                player_list = row["player_list"]
                current_players = row["current_players"]
                onlineservers.append(dict(name=name, player_list=player_list, current_players=current_players))

        if maintenance:
            embed.add_field(name=":red_circle:%s" % ("現在サーバーメンテナンス中"), value="", inline=False)
            status_channel = client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
            status_message = await status_channel.fetch_message(int(os.getenv("DISCORD_MSG_ID")))
            await status_message.edit(embed=embed)
            cursor.close()
            # Maintenance 状態の場合、10秒待機してからループの最初に戻る
            await asyncio.sleep(10)
            return  # ここでループの次の実行まで待機
        
        for server in onlineservers:
            name = server["name"]
            player_list = server["player_list"]
            current_players = server["current_players"]
            if player_list == "" or player_list == "NONE":
                player_list = "No Player"
            embed.add_field(name=":green_circle:%s" % (name), value="%s/%s: %s" % (current_players ,10, player_list), inline=False)

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
