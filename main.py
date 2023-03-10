import os
import eyed3
from dotenv import load_dotenv
from eyed3.core import Date
from eyed3.id3 import Tag
import pprint
from datetime import datetime

from logger import Logging

logging = Logging(__name__)

load_dotenv()

dir_path = os.getenv('DIRECTORY_PATH', None)
logging.log.info(f'Loading directory: {dir_path}')


def clean_filename(filename):
    filename = clean(filename)
    return filename.replace("Mp3", "mp3")


def clean(content: str):
    content = content.lower()
    content = content[0].upper() + content[1:]
    content = content.title()
    content = ''.join(i for i in content if i not in '"')
    content = content.replace('“', '').replace('”', '')
    content = content.replace('_', '').replace('~', '')
    content = content.replace('/', '-').replace('...', '')
    content = content.replace('|', '-').replace('@', '-')\
        .replace('[', '- ').replace(']', '')\
        .replace('(', '- ').replace(')', '')
    return ' '.join(content.split())


class MP3:
    def __init__(self, tag: Tag):
        self.artist = tag.artist
        self.album = tag.album
        self.genre = tag.genre.name
        self.recording_date = tag.recording_date.year
        self.track_num = tag.track_num.count
        self.title = tag.title
        self.comments = tag.comments

    def dump(self) -> dict:
        comments = []
        for comment in self.comments:
            comments.append(
                {
                    'text': comment.text,
                    'description': comment.description
                }
            )
        return {
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'recording_date': self.recording_date,
            'track_num': self.track_num,
            'title': self.title,
            'comments': comments,
        }


def get_mp3_files():
    mp3_files = []
    for path in os.listdir(dir_path):
        if '.mp3' not in path:
            continue
        mp3_files.append(os.path.join(dir_path, path))
    return mp3_files


def process():
    start_time = datetime.now()
    index = 1
    for mp3_file_path in get_mp3_files():
        if not os.path.isfile(mp3_file_path):
            continue
        logging.log.info(f'Processing: {mp3_file_path}')
        audiofile = eyed3.load(mp3_file_path)
        if not audiofile.tag:
            audiofile.initTag()
        try:
            audiofile.tag.genre = clean(audiofile.tag.genre.name) \
                if audiofile.tag.genre.name is not None and audiofile.tag.genre.name != '' else 'Electronic'
        except AttributeError as ignore:
            audiofile.tag.genre = 'Electronic'
        audiofile.tag.artist = clean(audiofile.tag.artist) \
            if audiofile.tag.artist is not None and audiofile.tag.artist != '' else 'Various Artists Music Mixer'
        audiofile.tag.album = clean(audiofile.tag.album) \
            if audiofile.tag.album is not None and audiofile.tag.album != '' else 'Electro Music 2023'
        audiofile.tag.recording_date = Date(int(2023))
        audiofile.tag.track_num = index
        audiofile.tag.title = clean(f'{str(index).zfill(5)}-{audiofile.tag.title}')
        for comment in audiofile.tag.comments:
            comment.text = 'lgzarturo'
            audiofile.tag.comments.remove(comment.description)
        # Definir una cover
        # with open(cover_path, "rb") as cover_art:
        #   song.tag.images.set(1, cover_art.read(), "image/jpeg")
        audiofile.tag.save()
        head, tail = os.path.split(mp3_file_path)
        new_mp3_file_path = f'{head}/{clean_filename(tail)}'
        os.rename(mp3_file_path, new_mp3_file_path)
        logging.log.info(f'Filename: {new_mp3_file_path}\n')
        index = index + 1
    logging.elapsed_time(start_time, 'process-files')


def read():
    start_time = datetime.now()
    res = []
    for mp3_file_path in get_mp3_files():
        if os.path.isfile(mp3_file_path):
            audiofile = eyed3.load(mp3_file_path)
            if not audiofile.tag:
                audiofile.initTag()
            res.append(MP3(audiofile.tag).dump())
    pprint.pprint(res)
    logging.elapsed_time(start_time, 'reading-files')


if __name__ == '__main__':
    if dir_path is None:
        logging.log.error('No se ha definido el directorio que se va a procesar.')
        exit(0)
    process()
    read()
