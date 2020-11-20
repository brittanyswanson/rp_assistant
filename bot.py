import os
import discord
import random
from dotenv import load_dotenv
import configparser

from discord.ext import commands
import mysql.connector
import logging

# Logging Setup
logging.basicConfig(filename="bot.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Connecting using Discord Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

# Database Work
def connect_to_DB():
    config = configparser.ConfigParser()
    config.read('env.ini')

    if 'mysql' in config:
        creds = config['mysql']
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
                logger.debug("Connected to DB")
                return mydb
        
        except Exception as e:
            logger.error("Fucked up trying to connect. " + str(e))
            status = "Fucked up trying to connect.  Error:  %s" % str(e)

    else:
        logger.error("Failure reading mysql credentials.")

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
            cursor.execute(query)
            
            for row in cursor:
                for field in row:
                    row_list.append(field)

    except Exception as e:
        logger.error("Couldn't execute query: " + str(query))
        logger.error(str(e))

    finally:
        cursor.close()
        mydb.close()
        
        if len(row_list) > 0:
            return row_list
        else:
            row_list = ['empty']
            logger.debug("No results from query: " + str(query))
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
            
            for row in cursor:
                for field in row:
                    row_list.append(field)

    except Exception as e:
        logger.error("Couldn't execute query: " + str(query))
        logger.error(str(e))

    finally:
        cursor.close()
        mydb.close()
        
        if len(row_list) > 0:
            return row_list
        else:
            row_list = ['empty']
            logger.debug("No results from query: " + str(query))
            return row_list

        # TODO: Is this still necessary
        if row is not None:
            logger.debug("*****This is still being used, clearly! Line 120**********")
            return row



@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} has connected to Discord!')



# -----------------
# Help
# -----------------
@bot.command(name='helpme', help = 'Input: None     Output: help')
async def show_help(ctx):
    logger.info('!helpme was called.')
    await ctx.send('Always begin a command with an exclamanation(!).\nList of commands available:\n\n**!species** - Returns a list of all available species. \n**!char_list vampires** - Lists active characters of a species (must input a species name)\n**!chars "mysteryuser"** - Lists active characters for a player (use player\'s name in double quotes if multiple words)\n**!app "marty mcfly"** - Shows the application url (and other goodies) for a character (use character\'s name in quotes)\n\nFor more information, visit www.rpconsole.com/bot.html')

# -----------------
# Roll Dice
# -----------------
@bot.command(name='roll_dice', help='Call it with the number of dice and number of sides separated by spaces')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    logger.info('!roll_dice was called.  Who even knew about this?')
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
    logger.info('!app was called with parameter: ' + char_name)
    proper_character_name = char_name.lower()
    char_query = """SELECT name, species, player_name, url FROM characters WHERE name = %(name)s""", {'name': proper_character_name}
    logger.debug(char_query)

    try:
        data = query_db(char_query)
        await ctx.send("character name: " + data[0] + "\n" + "species: " + data[1] + "\n" + "player: " + data[2] + "\n" + "application: " + data[3])
    except:
        logger.error("An error happened in get_character_url using: " + char_name)

# -----------------
# Get characters in species
# -----------------
@bot.command(name='char_list', help = 'Input: species name    Output: list of characters in species')
async def get_characters_in_species(ctx, species:str):
    logger.info('!char_list was called with parameter: ' + species)
    proper_species_name = species.lower()
    char_query = """SELECT name FROM characters WHERE species = %(species)s AND active = 'Y'""", {'species': proper_species_name}

    data_list = query_db(char_query)

    await ctx.send("-------------------\n" + "**" + species + " characters**\n" + "-------------------\n" + "\n".join(map(str, data_list)))

# -----------------
# Get characters by player
# -----------------
@bot.command(name='chars', help = 'Input: player name    Output: list of characters by player')
async def get_characters_from_player(ctx, player:str):
    logger.info('!char_list was called with parameter: ' + player)
    proper_player_name = player.lower()
    char_query = """SELECT name FROM characters WHERE player_name = %(player)s AND active = 'Y'""", {'player': proper_player_name}

    data_list = query_db(char_query)

    await ctx.send("-------------------\n" + "**" + player + "'s characters**\n" + "-------------------\n" + "\n".join(map(str, data_list)))


# -----------------
# Get species
# -----------------
@bot.command(name='species', help = 'Input: None     Output: list of species')
async def get_species(ctx):
    logger.info('!species was called.')
    char_query = """SELECT distinct species FROM characters"""

    logger.info("Calling query_db_no_param()")
    data_list = query_db_no_param(char_query)

    await ctx.send('**Available Species**\n' + '\n'.join(map(str, data_list)))

bot.run(TOKEN)