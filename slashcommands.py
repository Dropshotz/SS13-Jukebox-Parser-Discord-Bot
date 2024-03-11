from functions import *


# parser slash command. usage in discord: "/ytparser (url)"
@bot.slash_command(
    description="Turn a YouTube link into a SS13 Jukebox compatible JSON object.",
    guild_ids=bot_parameters.GUILD_ID)
async def onlineparser(interaction: nextcord.Interaction,
                   url: str,
                   genre: Optional[str] = SlashOption(required=False, default="Undefined"),
                   secret: Optional[bool] = SlashOption(required=False, default=False)):
    try:
        await interaction.response.send_message(f"Converting...")
    except:
        print("Interaction expired.")
        return
    if validators.url(url):
        if url.startswith((
                'https://www.youtube.com/c/',
                'https://www.youtube.com/channel/',
                'https://www.youtube.com/user/')):
            fd = os.open("Downloadlog.log", os.O_WRONLY | os.O_APPEND | os.O_CREAT)
            os.write(fd, str.encode(
                time.asctime(
                    time.localtime()) + ":" + interaction.user.name + " has tried to download something wrong!\n"))
            await interaction.followup.send("Please don't try to download entire channels with the bot.")
            return
        elif url.startswith('https://www.youtube.com/playlist'):
            await playlist(interaction, url=url, genre=genre, secret=secret)
            return
        elif url.startswith(('https://www.youtube.com/watch',
                             'https://www.twitch.tv/',
                             'https://clips.twitch.tv/',
                             'https://soundcloud.com/',
                             'https://youtu.be/')):
            soundcloud=False
            if url.startswith('https://soundcloud.com/'):
                soundcloud=True
                if url.startswith('https://soundcloud.com/pluffaduff/sets/'):
                    await playlist(interaction, url=url,genre=genre,secret=secret,soundcloud=soundcloud)
                    return
            await singlevideo(interaction, url=url, genre=genre, secret=secret,soundcloud=soundcloud)
            return
        else:
            return
        return
    await interaction.followup.send("Bad URL")


# file parser slash command. usage in discord: "/fileparser (url)"
@bot.slash_command(
    guild_ids=bot_parameters.GUILD_ID,
    description="Turn a audio file into a SS13 Jukebox compatible JSON object")
async def fileparser(interaction: nextcord.Interaction,
                     attachment: nextcord.Attachment,
                     genre: Optional[str] = SlashOption(required=False, default="Undefined"),
                     secret: Optional[bool] = SlashOption(required=False, default=False)):
    await interaction.response.send_message(f"Converting...")
    audio = "audio/" + attachment.filename
    await attachment.save(audio)
    file_validator.file_path = audio
    try:
        await singlefile(interaction, audio=audio, genre=genre,secret=secret)
    except FileValidationException:
        await interaction.followup.send("Not an audio file!")
        cleanup(interaction.user.name, audio, "Not a audio file, failed")
        return


@bot.slash_command(
    guild_ids=bot_parameters.GUILD_ID,
    description="Sorts the local JSON file.")
async def sorter(interaction: nextcord.Interaction, ):
    if (interaction.user.id != bot_parameters.BOT_OWNER):
        await interaction.response.send("You're unauthorized to use this command!")
        return
    await interaction.response.send_message(f"Sorting...")
    tosort = json.loads(json.dumps(json.load(open("tosort.json", "r"))))
    a = lambda x: (x['genre'], x['title'])
    sort = sorted(tosort, key=a)
    json.dump(sort, open('jukebox.json', 'w'), indent=2)
    print("Sorted")
