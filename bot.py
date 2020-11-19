import os
import discord
import random
from dotenv import load_dotenv
import configparser

from discord.ext import commands
import mysql.connector


def connect_to_DB():
    print("Inside connect_to_DB()")
    config = configparser.ConfigParser()
    config.read('env.ini')

    if 'mysql' in config:
        creds = config['mysql']
        print("Make that connection < connect_to_DB()")
        mydb = mysql.connector.connect(
            host = creds['host'],
            database = creds['db'],
            user = creds['user'],
            passwd = creds['passwd'],
            auth_plugin = "mysql_native_password")

        try:
            if (mydb):
                status = "connection successful"
            else:
                status = "connection failed"

            if status == "connection successful":
                return mydb
        
        except Exception as e:
            print("Fucked up trying to connect to teh database.")
            status = "Fucked up trying to connect.  Error:  %s" % str(e)

    else:
        print("Failure getting credentials.")

    

def query_db_no_param(query):
    print("In query_db_no_param()")
    mydb = connect_to_DB()
    row = None
    row_list = []

    try:
        if mydb is None:
            connect_to_DB()
        else:
            mydb.ping(True)
            print("ping mysql connection")
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
        print("Finally statement of query_db_no_param()")
        cursor.close()
        mydb.close()
        
        if len(row_list) > 0:
            return row_list
        else:
            row_list = ['empty']
            return row_list


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
    await ctx.send('Always begin a command with an exclamanation(!).\nList of commands available:\n\n**!species** - Returns a list of all available species. \n**!char_list vampires** - Lists active characters of a species (must input a species name)\n**!chars "mysteryuser"** - Lists active characters for a player (use player\'s name in double quotes if multiple words)\n**!app "marty mcfly"** - Shows the application url (and other goodies) for a character (use character\'s name in quotes)\n\nFor more information, visit www.rpconsole.com/bot.html')

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
    proper_character_name = char_name.lower()
    char_query = """SELECT name, species, player_name, url FROM characters WHERE name = %(name)s""", {'name': proper_character_name}

    try:
        data = query_db(char_query)
        await ctx.send("character name: " + data[0] + "\n" + "species: " + data[1] + "\n" + "player: " + data[2] + "\n" + "application: " + data[3])
    except:
        print("An error happened in get_character_url using: " + char_name)

# -----------------
# Get characters in species
# -----------------
@bot.command(name='char_list', help = 'Input: species name    Output: list of characters in species')
async def get_characters_in_species(ctx, species:str):
    proper_species_name = species.lower()
    char_query = """SELECT name FROM characters WHERE species = %(species)s AND active = 'Y'""", {'species': proper_species_name}

    data_list = query_db(char_query)

    await ctx.send("-------------------\n" + "**" + species + " characters**\n" + "-------------------\n" + "\n".join(map(str, data_list)))

# -----------------
# Get characters by player
# -----------------
@bot.command(name='chars', help = 'Input: player name    Output: list of characters by player')
async def get_characters_from_player(ctx, player:str):
    proper_player_name = player.lower()
    char_query = """SELECT name FROM characters WHERE player_name = %(player)s AND active = 'Y'""", {'player': proper_player_name}

    data_list = query_db(char_query)

    await ctx.send("-------------------\n" + "**" + player + "'s characters**\n" + "-------------------\n" + "\n".join(map(str, data_list)))


# -----------------
# Get species
# -----------------
@bot.command(name='species', help = 'Input: None     Output: list of species')
async def get_species(ctx):
    print("Generate char_query.")
    char_query = """SELECT distinct species FROM characters"""

    print("Calling query_db_no_param()")
    data_list = query_db_no_param(char_query)

    await ctx.send('**Available Species**\n' + '\n'.join(map(str, data_list)))

bot.run(TOKEN)