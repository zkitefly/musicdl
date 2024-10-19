import time
import requests
from bs4 import BeautifulSoup
import re
import os

# 全局变量存储歌曲信息
music_info = []

# 创建 music 文件夹
if not os.path.exists("music"):
    os.makedirs("music")

# 搜索歌曲并匹配输入的歌名和歌手
def search_and_download(query, song_info):
    query = query.replace(" / ", "&")
    search_url = f"https://cdn.crashmc.com/https://www.gequbao.com/s/{query}"
    retries = 5
    for attempt in range(retries):
        try:
            time.sleep(1)  # 添加延迟以避免请求过于频繁
            response = requests.get(search_url)
            log_search_url = search_url.replace(" ", "%20")
            print(f"搜索 URL: {log_search_url}")
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                rows = soup.find_all('div', class_='row')

                matched_song = None
                song_title, artist_name = song_info.split(" - ")

                for row in rows:
                    title_span = row.find('span', class_='music-title')
                    artist_small = row.find('small', class_='text-jade')
                    link = row.find('a', href=True)
                    if title_span and artist_small and link:
                        title = title_span.get_text(strip=True)
                        artist = artist_small.get_text(strip=True)
                        href = link['href']
                        # 检查是否有完全匹配的歌曲名和歌手
                        if title == song_title and artist == artist_name:
                            matched_song = (title, artist, href)

                        artist_name.replace(" ", "")
                        if title == song_title and artist == artist_name:
                            matched_song = (title, artist, href)
                            break
                            

                if matched_song:
                    title, artist, href = matched_song
                    print(f"正在下载: {title} - {artist}")
                    download_song(title, artist, href)
                    return  # 下载成功后结束函数
                else:
                    print(f"未找到匹配的: {song_info}")
                    with open('musicdl.txt', 'a') as log_file:
                        log_file.write(f"未找到匹配的: {song_info}\n")
                    return
            else:
                print(f"搜索失败，状态码：{response.status_code}")
        except Exception as e:
            print(f"搜索错误：{e}")
        time.sleep(1)  # 每次重试前的延迟

# 修改下载歌曲的函数，当文件下载失败时重新尝试
def download_song(title, artist, href):
    song_url = f"https://cdn.crashmc.com/https://www.gequbao.com{href}"
    retries = 5
    for attempt in range(retries):
        try:
            time.sleep(1)  # 添加延迟以避免请求过于频繁
            print(f"歌曲详情页 URL: {song_url}")
            response = requests.get(song_url)
            if response.status_code == 200:
                html_content = response.text
                match = re.search(r"window\.play_id = '(.*?)'", html_content)
                if match:
                    play_id = match.group(1)
                    download_url = get_download_link(play_id)
                    if download_url:
                        # 下载歌曲，检查文件大小
                        success = download_to_folder(download_url, f"music/{title} - {artist}.mp3")
                        if success:
                            print(f"下载完成: {title} - {artist}")
                            with open('musicdl.txt', 'a') as log_file:
                                log_file.write(f"下载成功: {title} - {artist}\n")
                            return  # 下载成功后结束函数
                        else:
                            print(f"重新下载: {title} - {artist}")
                            continue  # 重新尝试下载
                    else:
                        print(f"无法获取下载链接: {title} - {artist}")
                        with open('musicdl.txt', 'a') as log_file:
                            log_file.write(f"无法获取下载链接: {title} - {artist}\n")
                        return
                else:
                    print("未找到 play-id")
            else:
                print(f"未找到歌曲信息，状态码：{response.status_code}" )
        except Exception as e:
            print(f"下载错误：{e}")
        time.sleep(1)  # 每次重试前的延迟

# 调用 API 获取下载链接
def get_download_link(play_id):
    api_url = "https://www.gequbao.com/api/play-url"
    data = {'id': play_id}
    headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    retries = 5
    for attempt in range(retries):
        try:
            time.sleep(1)  # 添加延迟以避免请求过于频繁
            response = requests.post(api_url, data=data, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("code") == 1:
                    return json_data["data"]["url"]
            print(f"获取下载链接失败，响应状态: {response.status_code}")
        except Exception as e:
            print(f"获取下载链接时出错: {e}")
        time.sleep(1)  # 每次重试前的延迟
    return None

# 下载歌曲文件，并检查文件大小是否符合要求
def download_to_folder(download_url, file_path):
    download_url = "https://cdn.crashmc.com/" + download_url
    retries = 5
    for attempt in range(retries):
        try:
            time.sleep(1)  # 添加延迟以避免请求过于频繁
            print(f"下载 URL: {download_url}")
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                # 检查文件大小
                if os.path.getsize(file_path) < 10240:  # 小于 10 KB
                    print(f"文件 {file_path} 大小小于 10 KB，重新下载...")
                    os.remove(file_path)  # 删除下载的无效文件
                    # 重新获取下载链接并再次下载
                    return False
                else:
                    print(f"歌曲下载成功: {file_path}")
                    return True  # 下载成功
            else:
                print(f"下载失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载文件时出错: {e}")
        time.sleep(1)  # 每次重试前的延迟
    return False  # 下载失败，返回 False

# 读取 music.txt 并开始批量下载
def start_batch_download():
    try:
        with open('music.txt', 'r') as file:
            songs = file.readlines()

        if not songs:
            print("music.txt 为空，请输入歌曲")
            return

        for song in songs:
            time.sleep(1)  # 添加延迟
            song = song.strip()
            if song:
                query = song
                print(f"- 搜索 {song}")
                search_and_download(query, song)

        print("下载完成")

    except FileNotFoundError:
        print("找不到 music.txt 文件")
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    start_batch_download()
