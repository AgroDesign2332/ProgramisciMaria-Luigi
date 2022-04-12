import discord, datetime, sqlite3; from discord.ext import commands
from discord.commands.options import Option
from discord.commands import permissions
from config import *

# ---+== MAIN VAR'S ==+--- #

intents = discord.Intents.all()
client = commands.Bot(intents=intents)
conn = sqlite3.connect('data.db')
c = conn.cursor()

# ---+== MAIN FUNC'S ==+--- #

def filmChoice(ctx: discord.AutocompleteContext):
    c.execute("SELECT word FROM films")
    films = c.fetchall()
    list = []
    for film in films:
        list.append(film[0])
    return list

def filmList():
    c.execute("SELECT word FROM films")
    films = c.fetchall()
    list = []
    for film in films:
        list.append(film[0])
    return list
    
# -----+=== READY ===+----- #

@client.event
async def on_ready():
    print('Zalogowano jako {}'.format(client.user.name))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{botstatus}"))
    print('Ustawiono status.')
    c.execute("CREATE TABLE IF NOT EXISTS films(word STR, link STR)")
    conn.commit()

# ----+== DELETE LOG ==+---- #

@client.event
async def on_message_delete(message):
    #if message.author.bot:
    #    return
    channel = message.guild.get_channel(963146152562262037)
    embed = discord.Embed(
        title=f'`👀` Usunięta wiadomość',
        description=f'Wiadomość {message.author.mention} z <#{message.channel.id}>: \n> {message.content}',
        timestamp=datetime.datetime.now(),
        color=0xd62929
    ).set_footer(text=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar.url)
    await channel.send(embed=embed)

# ----+=== COMMANDS ===+---- #

@client.slash_command(guild_ids=[941633571393781770], description='💭 Dodaje sugestie na kanale #💡sugestie')
async def sugestia(ctx: discord.Interaction, sugestia: Option(str, '🤔 Tu wpisz sugestie')):
    channel = ctx.guild.get_channel(963146152562262037)
    msg = await channel.send(embed=(discord.Embed(
        title=f'`💡` Sugestia od {ctx.author.name}',
        description='> ' + sugestia,
        timestamp=datetime.datetime.now(),
        color=0x00ff80
    ).set_footer(text=f'{ctx.guild.name}', icon_url=f'{ctx.guild.icon.url}')))
    await msg.add_reaction('👍')
    await msg.add_reaction('➖')
    await msg.add_reaction('👎')
    threadname = f'Sugestia {ctx.author.name}'
    await msg.create_thread(name=threadname)
    await ctx.respond(f'\✅ Sugestia została wysłana! \n{msg.jump_url}', ephemeral=True)

@client.slash_command(guild_ids=[941633571393781770], description='🎥 Wysyła link do wybrań filmu')
async def films(ctx, film: Option(str, '🤔 Jaki chcesz film?', autocomplete=filmChoice)):
    c.execute('SELECT * FROM films WHERE word = ?', (film,))
    link = c.fetchone()
    embed = discord.Embed(
        title=f'`🎥` Film {film}',
        description=f'> Link: {link[1]}',
        timestamp=datetime.datetime.now(),
        color=0x00ff80
    ).set_footer(text=f'{ctx.author.name}', icon_url=f'{ctx.author.avatar.url}')
    xd, code = str(link[1]).split('watch?v=')
    embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{code}/hqdefault.jpg')
    await ctx.respond(embed=embed)

@client.slash_command(guild_ids=[941633571393781770], description='🎥 Dodaje film do bazy')
@permissions.has_any_role(adminroles)
async def dodaj_film(ctx, film: Option(str, 'Fraza która pojawi się do wyboru'), link: Option(str, 'Link do filmu')):
    c.execute('INSERT INTO films VALUES (?, ?)', (film, link))
    conn.commit()
    await ctx.respond(f'Dodano film {film}', ephemeral=True)

@client.slash_command(guild_ids=[941633571393781770], description='🎥 Usuwa film z bazy')
@permissions.has_any_role(adminroles)
async def usun_film(ctx, film: Option(str, 'Nazwa filmu (fraza)', autocomplete=filmChoice)):
    c.execute('DELETE FROM films WHERE word = ?', (film,))
    conn.commit()
    await ctx.respond(f'Usunięto film {film}', ephemeral=True)

# ---+=== MSG COMMAND ===+--- #

@client.message_command(guild_ids=[941633571393781770], description='🎥 Wysyła link do wybrań filmu')
async def film(ctx, message):
    for film in filmList():
        if film in message.content:
            c.execute('SELECT * FROM films WHERE word = ?', (film,))
            link = c.fetchone()
            embed = discord.Embed(
                title=f'`🎥` Film {film}',
                description=f'> Link: {link[1]}',
                timestamp=datetime.datetime.now(),
                color=0x00ff80
            ).set_footer(text=f'{ctx.author.name}', icon_url=f'{ctx.author.avatar.url}')
            xd, code = str(link[1]).split('watch?v=')
            embed.set_thumbnail(url=f'https://i.ytimg.com/vi/{code}/hqdefault.jpg')
            return await ctx.respond(embed=embed)
        else:
            continue
    await ctx.respond(f'Nie znalazłem takiego filmu.', ephemeral=True)

# -----+=== LOGIN ===+----- #

client.run(token)
    