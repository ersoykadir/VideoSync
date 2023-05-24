import ffmpeg
from config import Config
def compress(filename: str):
    filename.replace(Config().FILE_EXTENSION, "") # replace .mp4 extension if it exists
    compressed_filename = f"{filename}_comp{Config().FILE_EXTENSION}"
    (ffmpeg
        .input(filename)
        .output(
            compressed_filename,
            crf=30,
            vcodec="libx264",
            preset='superfast',
            loglevel='quiet',
        )
        .run()
    )
    return compressed_filename