import ffmpeg
from config import Config

def get_compress_name(filename: str):
    k = filename.replace(Config().FILE_EXTENSION, "")# replace .mp4 extension if it exists
    return f"{k}_comp{Config().FILE_EXTENSION}"

def compress(filename: str):
    compress_video = get_compress_name(filename)
    (ffmpeg
        .input(filename)
        .output(
            compress_video,
            crf=35,
            vcodec="libx264",
            preset='superfast',
            loglevel='quiet',
        )
        .run(
        overwrite_output=True
    )
)
    return compress_video