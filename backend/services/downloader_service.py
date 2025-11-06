import yt_dlp
import os

def download_audio(url: str, save_path: str) -> str:
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

    try:
        print(f"Starting download from URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            base_filename = ydl.prepare_filename(info_dict).rsplit('.', 1)[0]
            final_filepath = base_filename + '.mp3'
            
            if os.path.exists(final_filepath):
                print(f"Download complete. File saved to: {final_filepath}")
                return final_filepath
            else:
                raise Exception("Downloaded file not found after conversion.")
    except Exception as e:
        print(f"Error downloading from URL {url}: {e}")
        raise e