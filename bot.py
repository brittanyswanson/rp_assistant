import os
import discord
import random
from dotenv import load_dotenv
import json

from discord.ext import commands
import mysql.connector


def connect_to_DB():
    mydb = mysql.connector.connect(
        
    )

    try:
        if (mydb):
            status = "connection successful"
        else:
            status = "connection failed"

        if status == "connection successful":
            return mydb
    except Exception as e:
        status = "Failure %s" % str(e)

def query_db_no_param(query):
    mydb = connect_to_DB()
    row = None
    row_list = []

    try:
        if mydb is None:
            connect_to_DB()
        else:
            mydb.ping(True)
            cursor = mydb.cursor()
            # Changed to put * before query in order to unpack.  Was getting a system error.
            cursor.execute(query)
            # row = cursor.fetchone()
            
            for row in cursor:
                for field in row:
                    row_list.append(field)

            
                # row = cursor.fetchone()
    except Exception as e:
        print(e)

    finally:
        cursor.close()
        mydb.close()
        
        if len(row_list) > 0:
            for it in row_list:
                print(it)
            return row_list

        if row is not None:
            return row

def query_db(query):
    mydb = connect_to_DB()
    row = None
    row_list = []

    try:
        if mydb is None:
            connect_to_DB()
        else:
            mydb.ping(True)
            cursor = mydb.cursor()
            # Changed to put * before query in order to unpack.  Was getting a system error.
            cursor.execute(*query)
            # row = cursor.fetchone()
            
            for row in cursor:
                for field in row:
                    row_list.append(field)

            
                # row = cursor.fetchone()
    except Exception as e:
        print(e)

    finally:
        cursor.close()
        mydb.close()
        
        if len(row_list) > 0:
            for it in row_list:
                print(it)
            return row_list

        if row is not None:
            return row

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# client = discord.Client()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')



# -----------------
# Help
# -----------------
@bot.command(name='helpme', help = 'Input: None     Output: help')
async def show_help(ctx):
    await ctx.send('Always begin a command with an exclamanation(!).\nList of commands available:\n\n**!species** - Returns a list of all available species. \n**!char_list VAMPIRES** - Shows the active characters of a species (must input a species name)\n**!app "MARTY MCFLY"** - Shows the application url for a desired character (use character\'s name in quotes)\n\nFor more information, visit www.rpconsole.com/bot.html')


# -----------------
# Roll Dice
# -----------------
@bot.command(name='roll_dice', help='Call it with the number of dice and number of sides separated by spaces')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


# -----------------
# Get character url
# -----------------
@bot.command(name='app', help = 'Input: full character name    Output: character bio url')
async def get_character_url(ctx, char_name:str):
    char_query = """SELECT name, species, url FROM characters WHERE name = %(name)s""", {'name': char_name}

    data = query_db(char_query)
    await ctx.send("character name: " + data[0] + "\n" + "species: " + data[1] + "\n" + "application: " + data[2])

# -----------------
# Get characters in species
# -----------------
@bot.command(name='char_list', help = 'Input: species name    Output: list of characters in species')
async def get_characters_in_species(ctx, species:str):
    char_query = """SELECT name FROM characters WHERE species = %(species)s""", {'species': species}

    data_list = query_db(char_query)

    await ctx.send('**' + species + '**\n' + '\n'.join(map(str, data_list)))


# -----------------
# Get species
# -----------------
@bot.command(name='species', help = 'Input: None     Output: list of species')
async def get_species(ctx):
    char_query = """SELECT distinct species FROM characters"""

    data_list = query_db_no_param(char_query)

    await ctx.send('**Available Species**\n' + '\n'.join(map(str, data_list)))

bot.run(TOKEN)