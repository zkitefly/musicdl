import time
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import re
import os
import threading

# 全局变量存储歌曲信息
music_info = []

# 创建 music 文件夹
if not os.path.exists("music"):
    os.makedirs("music")

# 搜索歌曲并匹配输入的歌名和歌手
def search_and_download(query, song_info, status_label, result_list):
    search_url = f"https://cdn.crashmc.com/https://www.gequbao.com/s/{query}"
    retries = 3
    for attempt in range(retries):
        try:
            time.sleep(2)  # 添加延迟以避免请求过于频繁
            response = requests.get(search_url)
            print(f"搜索 URL: {search_url}")
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
                            break

                if matched_song:
                    title, artist, href = matched_song
                    status_label.config(text=f"正在下载: {title} - {artist}")
                    download_song(title, artist, href, result_list, status_label)
                    return  # 下载成功后结束函数
                else:
                    status_label.config(text=f"未找到匹配的: {song_info}")
                    with open('musicdl.txt', 'a') as log_file:
                        log_file.write(f"未找到匹配的: {song_info}\n")
                    return
            else:
                status_label.config(text="搜索失败")
        except Exception as e:
            status_label.config(text=f"搜索出错: {e}")
            print(f"搜索错误：{e}")
        time.sleep(2)  # 每次重试前的延迟

# 获取歌曲下载链接并下载歌曲
def download_song(title, artist, href, result_list, status_label):
    song_url = f"https://cdn.crashmc.com/https://www.gequbao.com{href}"
    retries = 3
    for attempt in range(retries):
        try:
            time.sleep(2)  # 添加延迟以避免请求过于频繁
            print(f"歌曲详情页 URL: {song_url}")
            response = requests.get(song_url)
            if response.status_code == 200:
                html_content = response.text
                match = re.search(r"window\.play_id = '(.*?)'", html_content)
                if match:
                    play_id = match.group(1)
                    download_url = get_download_link(play_id)
                    if download_url:
                        # 下载歌曲
                        download_to_folder(download_url, f"music/{title} - {artist}.mp3")
                        status_label.config(text=f"下载完成: {title} - {artist}")
                        with open('musicdl.txt', 'a') as log_file:
                            log_file.write(f"下载成功: {title} - {artist}\n")
                        return  # 下载成功后结束函数
                    else:
                        status_label.config(text=f"无法获取下载链接: {title} - {artist}")
                        with open('musicdl.txt', 'a') as log_file:
                            log_file.write(f"无法获取下载链接: {title} - {artist}\n")
                        return
                else:
                    status_label.config(text="未找到 play-id")
        except Exception as e:
            status_label.config(text=f"下载错误: {e}")
            print(f"下载错误：{e}")
        time.sleep(2)  # 每次重试前的延迟

# 调用 API 获取下载链接
def get_download_link(play_id):
    api_url = "https://www.gequbao.com/api/play-url"
    data = {'id': play_id}
    headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    retries = 3
    for attempt in range(retries):
        try:
            time.sleep(2)  # 添加延迟以避免请求过于频繁
            response = requests.post(api_url, data=data, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("code") == 1:
                    return json_data["data"]["url"]
            print(f"获取下载链接失败，响应状态: {response.status_code}")
        except Exception as e:
            print(f"获取下载链接时出错: {e}")
        time.sleep(2)  # 每次重试前的延迟
    return None

# 下载歌曲文件
def download_to_folder(download_url, file_path):
    retries = 3
    for attempt in range(retries):
        try:
            time.sleep(2)  # 添加延迟以避免请求过于频繁
            print(f"下载 URL: {download_url}")
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f"歌曲下载成功: {file_path}")
                return  # 下载成功后结束函数
            else:
                print(f"下载失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载文件时出错: {e}")
        time.sleep(2)  # 每次重试前的延迟

# 读取 music.txt 并开始批量下载
def start_batch_download(status_label, result_list):
    try:
        with open('music.txt', 'r') as file:
            songs = file.readlines()

        if not songs:
            status_label.config(text="music.txt 为空，请输入歌曲")
            return

        for song in songs:
            time.sleep(2)  # 添加延迟
            song = song.strip()
            if song:
                query = song.replace(" ", "%20")  # URL 编码
                status_label.config(text=f"搜索 {song}")
                threading.Thread(target=search_and_download, args=(query, song, status_label, result_list)).start()

        status_label.config(text="下载完成")

    except FileNotFoundError:
        status_label.config(text="找不到 music.txt 文件")
    except Exception as e:
        status_label.config(text=f"读取文件时出错: {e}")

# 创建UI
def create_ui():
    window = tk.Tk()
    window.title("批量音乐下载器")
    window.geometry("600x200")

    # 显示说明
    instruction_label = tk.Label(window, text="请在 music.txt 中输入歌曲，格式为 '歌名 - 歌手'，每行一首")
    instruction_label.pack(pady=10)

    # 开始下载按钮
    start_button = tk.Button(window, text="开始下载", command=lambda: start_batch_download(status_label, result_list))
    start_button.pack(pady=10)

    # 下载结果列表
    result_list_frame = tk.Frame(window)
    scrollbar = Scrollbar(result_list_frame)
    result_list = Listbox(result_list_frame, height=10, width=50)
    result_list_frame.pack(pady=10)

    # 状态提示区
    status_label = tk.Label(window, text="准备下载")
    status_label.pack(pady=10)

    window.mainloop()

# 启动程序
if __name__ == "__main__":
    create_ui()
