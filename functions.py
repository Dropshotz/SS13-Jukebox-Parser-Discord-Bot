from parameters import *


# The JSON converter. format:Give path to audio file, returns a JSON object.
# Siivagunner titles are reversed so that is accounted for
async def makeJSONobject(audio: str, genre="Undefined", issiiva=False, secret=False, artist=""):
    if not debug:
        channel = bot.get_channel(bot_parameters.CHANNEL_ID)
    else:
        channel = bot.get_channel(bot_parameters.DEBUG_CHANNEL_ID)
    title = []
    file = nextcord.File(audio)
    print("Uploading...")
    message = await channel.send(file=file)
    url = message.attachments[0].url
    name = os.path.splitext(os.path.basename(audio))[0]
    if (issiiva):
        title = name.rsplit('-', 1)
        print("Oh hey, Siivagunner")
        aux = title[0]
        title[0] = title[1]
        title[1] = aux
    else:
        if '｜' in name:
            title = name.split('｜', 2)
        else:
            title = name.split('-', 1)
    if len(title) == 1:
        title.append("Not Found")
        title[1] = title[0]
        title[0] = "Not Found"
    title[0] = title[0].strip()
    title[1] = title[1].strip()
    for char in rev_dictionary:
        title[0] = title[0].replace(char, rev_dictionary[char])
        title[1] = title[1].replace(char, rev_dictionary[char])
    duration = int(MP3(audio).info.length) * 10
    if artist == "":
        artist=title[0]
    jsonobj = "{\n" + \
              "\t\"url\" : \"" + url + "\",\n" + \
              "\t\"title\" : \"" + title[1] + "\",\n" + \
              "\t\"duration\" : " + str(duration) + ",\n" + \
              "\t\"artist\": \"" + artist + "\",\n" + \
              "\t\"secret\": " + str(secret).lower() + ",\n" + \
              "\t\"lobby\": false,\n" + \
              "\t\"jukebox\": true,\n" + \
              "\t\"genre\": \"" + genre + "\"\n" + \
              "}"
    return jsonobj


# Clears files and adds to the log file.
def cleanup(user: str, audio: str, error=""):
    fd = os.open("Downloadlog.log", os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    os.write(fd, str.encode(
        time.asctime(time.localtime()) + ":" + user + " has converted the following file:" + audio))
    if (error):
        os.write(fd, str.encode(" ERROR:" + error))
    os.write(fd, str.encode("\n"))
    os.close(fd)
    os.unlink(audio)


# This processes videos individually
async def singlevideo(interaction: nextcord.Interaction, url: str, playlist=False, genre="Undefined", secret=False,
                      soundcloud=False):
    print("Downloading...")
    audio = ""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            artist=""
            audio = ydl.extract_info(url, download=True)
            if (playlist == False):
                replyto = await interaction.followup.send(content=str(audio['title']))
            issiiva = False
            if (not soundcloud):
                if (audio['channel_id'] == "UC9ecwl3FTG66jIKA9JRDtmg"):
                    issiiva = True
            else:
                artist=audio['uploader']
                pass
            if (playlist):
                audio1 = audio
            audio = audio['title']
            print(audio)
            for char in dictionary:
                audio = audio.replace(char, dictionary[char])
            audio = "audio/" + audio + ".mp3"
            if (playlist == False):
                json = "```json\n"
                json += await makeJSONobject(audio, issiiva=issiiva, genre=genre, secret=secret, artist=artist)
                json += "```"
                await replyto.reply(json)
                if (genre == "Undefined"):
                    await replyto.reply("Remember to add genre and make sure it is all fine!")
                else:
                    await replyto.reply("Please double check and make sure it is all fine!")
                print("Done")
            else:
                json = await makeJSONobject(audio, issiiva=issiiva, genre=genre, secret=secret, artist=artist)
            cleanup(interaction.user.name, audio)
            return json
    except nextcord.errors.HTTPException:
        await interaction.followup.send("File Too Large/Other file/Upload related error")
        if (playlist):
            await interaction.followup.send(audio1['title'])
        cleanup(interaction.user.name, audio, "File too large, failed")
    except Exception as error:
        print(error)
        await interaction.followup.send("Undefined Error! Please contact the developer @dr0ppy")
        if (playlist):
            await interaction.followup.send(audio1['title'])
        cleanup(interaction.user.name, audio, "Unknown Error, failed")
    print("test")
    return ""


# This feeds the single video converter playlists one by one
async def playlist(interaction: nextcord.Interaction, url: str, genre="Undefined", secret=False, soundcloud=False):
    print("Playlist Processing Start")
    jsonblock = ""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            replyto = await interaction.followup.send(content=str("Playlist:" + info['title']))
            i = 0
            if (genre == "Undefined"):
                genre = info['title']
            for audio in info['entries']:
                try:
                    i += 1
                    print(i)
                    jsonblock += await singlevideo(interaction, url=audio['webpage_url'], playlist=True,
                                                   genre=info['title'], secret=secret, soundcloud=soundcloud) + ",\n"
                except:
                    pass

            jsonblock = jsonblock[:len(jsonblock) - 2]
            jsonfile = os.open("jsonblock.json", os.O_WRONLY | os.O_APPEND | os.O_CREAT)
            os.write(jsonfile, str.encode(jsonblock))
            file = nextcord.File("jsonblock.json")
            await replyto.reply(file=file)
            if (genre == "Undefined"):
                await replyto.reply("Genre is the playlist name! Make sure to double check!")
            else:
                await replyto.reply("Genre is the one you set! Make sure to double check!")
            os.close(jsonfile)
            os.unlink("jsonblock.json")
        print("Done processing playlist")
        fd = os.open("Downloadlog.log", os.O_WRONLY | os.O_APPEND | os.O_CREAT)
        os.write(fd, str.encode(
            time.asctime(
                time.localtime()) + ":" + interaction.user.name + " converted playlist: " + info['title'] + " URL:" +
            info['webpage_url']))
        os.close(fd)
        return
    except:
        await interaction.followup.send("Undefined error")


async def singlefile(interaction: nextcord.Interaction, audio: str, genre="Undefined", secret=False):
    try:
        file_validator.validate_extension()
    except FileValidationException:
        print("Converting file")
        audio1 = os.path.splitext(audio)[0] + ".mp3"
        AudioSegment.from_file(audio).export(audio1, format="mp3", bitrate="320")
        os.unlink(audio)
        audio = audio1
    replyto = await interaction.followup.send(content=str(os.path.splitext(os.path.basename(audio))[0]))
    json = "```json\n"
    json += await makeJSONobject(audio=audio, genre=genre, secret=secret)
    json += "```"
    await replyto.reply(json)
    await replyto.reply("Remember to add genre and make sure it is all fine!")
    cleanup(interaction.user.name, audio)
