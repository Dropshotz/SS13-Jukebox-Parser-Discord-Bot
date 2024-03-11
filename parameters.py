from imports import *

debug = False

bot = commands.Bot(intents=nextcord.Intents.all(), command_prefix="!")

dictionary = {":": "：", "/": "⧸", "?": "？", "|": "｜", "\"": "＂"}
rev_dictionary = {"：": ":", "⧸": "/", "？": "?", "｜": "|", "＂": "\""}


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# Parameters for the YouTube downloader
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


titleformat = '(?P<artist>.*) - (?P<track>.*) \(Karaoke\)'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [
        {'key': 'MetadataFromTitle',
         'titleformat': titleformat},
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    'outtmpl': 'audio/%(title)s.%(ext)s',
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    '_titleformat': titleformat,
    'noplaylist': True,
    'ignoreerrors': True,
}

# parameters for file validator
file_validator = FileValidator(
    acceptable_types=["audio"],
    acceptable_extensions=[".mp3"]
)
