import mutagen.mp3
import nextcord
import yt_dlp
import validators
from file_validator.exceptions import FileValidationException
from file_validator.validators import FileValidator
from mutagen.mp3 import MP3
import os
import bot_parameters
import time
from nextcord.ext import commands
from pydub import AudioSegment
import json
from typing import Optional
from nextcord import SlashOption
