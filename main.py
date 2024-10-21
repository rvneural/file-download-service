import os.path
import random
import string
import time
import yt_dlp
import base64
from fastapi import FastAPI, Response
import uvicorn

app = FastAPI(
    title="File Downloader",
    version="1.0.0"
)

cache = dict()
in_process = False


def remove(file: str, flag: bool = False):
    if not os.path.exists(file):
        return
    while in_process:
        time.sleep(10)
    try:
        os.remove(file)
    except Exception as e:
        print(e)
        if not flag:
            remove(file, True)
        else:
            return


def clear_cache(exclude: str):
    cache.clear()
    exclude = exclude.replace('downloads/', '').strip()
    for file in os.listdir('downloads'):
        if file.strip() == exclude:
            continue
        try:
            remove('downloads/' + file)
        except:
            pass


def get_cache(url: str, quality: str = '') -> str | None:
    if quality.lower().strip() == 'best':
        quality = 'best'
    else:
        quality = 'low'

    if cache.get(url) and cache.get(url).get(quality):
        return cache.get(url).get(quality)
    else:
        return None


def set_cache(url: str, path: str, quality: str = ''):
    if len(cache) > 100:
        clear_cache(path)
    if quality.lower().strip() == 'best':
        quality = 'best'
    else:
        quality = 'low'

    if cache.get(url):
        cache[url][quality] = path
    else:
        cache[url] = {quality: path}


def generate_randon_name(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def download(url: str, quality: str = '') -> str:
    output = 'downloads/' + generate_randon_name(50) + '.mp4'

    cache_res = get_cache(url, quality)
    if (cache_res is not None) and (os.path.exists(cache_res)):
        return cache_res

    if quality.lower().strip() == 'best':
        v_format = 'bestvideo+bestaudio/best'
    else:
        v_format = 'worstvideo+bestaudio/best'

    ydl_opts = {
        'outtmpl': output,
        'geo_bypass': True,
        'format': v_format,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'overwrites': True,
        'extractor_args': {
            'youtube': {
                'raise_incomplete_data': ['Incomplete Data Received']
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if os.path.exists(output):
        set_cache(url=url,
                  path=output,
                  quality=quality)
        return output
    if os.path.exists(output + '.webm'):
        set_cache(url=url,
                  path=output + '.webm',
                  quality=quality)
        return output + '.webm'

    raise yt_dlp.utils.DownloadError(msg="Error while downloading")


@app.get('/file')
def download_file(url: str, quality: str = 'low'):
    global in_process
    try:
        in_process = True
        file_name = download(url, quality=quality)
        name = file_name.replace('downloads/', '')
        file = open(file_name, 'rb')
        bytes = file.read()
        file.close()
    except yt_dlp.utils.DownloadError:
        return Response(status_code=400,
                        content={'error': 'Bad Request', 'details': 'Вы ввели неверный URL или сервер недоступен'})
    except Exception as e:
        return Response(status_code=500, content={'error': 'Internal Server Error', 'details': str(e)})
    else:
        return {
            'name': name,
            'data': base64.b64encode(bytes)
        }
    finally:
        in_process = False


if __name__ == '__main__':
    uvicorn.run(app="main:app", host='', port=8084, log_level='info', workers=4)
