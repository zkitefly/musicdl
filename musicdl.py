import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
import re
import json
import threading
import os

# 全局变量存储歌曲信息
music_info = []

# 搜索歌曲的功能
def search_music(query, result_list, status_label):
    search_url = f"https://cdn.crashmc.com/https://www.gequbao.com/s/{query}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            rows = soup.find_all('div', class_='row')
            music_info.clear()  # 清空之前的搜索结果
            result_list.delete(0, tk.END)  # 清空之前的显示内容

            i = 1
            for row in rows:
                title_span = row.find('span', class_='music-title')
                artist_small = row.find('small', class_='text-jade')
                link = row.find('a', href=True)
                if title_span and artist_small and link:
                    title = title_span.get_text(strip=True)
                    artist = artist_small.get_text(strip=True)
                    href = link['href']
                    music_info.append((i, title, artist, href))
                    result_list.insert(tk.END, f"{i} | {title} - {artist}")
                    i += 1

            status_label.config(text=f"搜索到 {len(music_info)} 首歌曲")
        else:
            status_label.config(text="搜索失败，请重试。")
    except Exception as e:
        status_label.config(text=f"错误: {e}")

# 获取歌曲下载链接
def fetch_download_link(music_index, status_label):
    i, title, artist, href = music_info[music_index]
    song_url = f"https://cdn.crashmc.com/https://www.gequbao.com{href}"
    try:
        response = requests.get(song_url)
        if response.status_code == 200:
            html_content = response.text
            # 使用正则表达式提取 play-id
            match = re.search(r"window\.play_id = '(.*?)'", html_content)
            if match:
                play_id = match.group(1)
                # 调用 API 获取下载链接
                download_url = get_download_link(play_id)
                if download_url:
                    # 下载文件
                    download_song(download_url, f"{title} - {artist}.mp3", status_label)
                else:
                    status_label.config(text="获取下载链接失败")
            else:
                status_label.config(text="未找到 play-id")
        else:
            status_label.config(text="无法访问歌曲详情页")
    except Exception as e:
        status_label.config(text=f"错误: {e}")

# 调用 API 获取下载链接
def get_download_link(play_id):
    api_url = "https://www.gequbao.com/api/play-url"
    data = {'id': play_id}
    headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    try:
        response = requests.post(api_url, data=data, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("code") == 1:
                return json_data["data"]["url"]
    except Exception as e:
        print(f"获取下载链接时出错: {e}")
    return None

# 下载歌曲
def download_song(download_url, file_name, status_label):
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            # 保存歌曲文件
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            status_label.config(text=f"歌曲下载完成: {file_name}")
        else:
            status_label.config(text="下载失败")
    except Exception as e:
        status_label.config(text=f"下载错误: {e}")

# 搜索按钮点击事件
def on_search_click(entry, result_list, status_label):
    query = entry.get().strip()
    if query:
        status_label.config(text="正在搜索...")
        threading.Thread(target=search_music, args=(query, result_list, status_label)).start()

# 列表项点击事件
def on_item_click(event, result_list, status_label):
    selected_index = result_list.curselection()
    if selected_index:
        index = selected_index[0]
        status_label.config(text="正在获取下载链接...")
        threading.Thread(target=fetch_download_link, args=(index, status_label)).start()

# 创建UI
def create_ui():
    window = tk.Tk()
    window.title("音乐下载器 - zkitefly")
    window.geometry("500x350")

    # 搜索框
    search_entry = tk.Entry(window)
    search_entry.pack(pady=10)

    # 搜索按钮
    search_button = tk.Button(window, text="搜索", command=lambda: on_search_click(search_entry, result_list, status_label))
    search_button.pack(pady=5)

    # 搜索结果列表
    result_list_frame = tk.Frame(window)
    result_list = Listbox(result_list_frame, height=10, width=50)
    result_list.bind('<<ListboxSelect>>', lambda event: on_item_click(event, result_list, status_label))
    result_list.pack(side=tk.LEFT, fill=tk.BOTH)
    result_list_frame.pack(pady=10)

    # 状态提示区
    status_label = tk.Label(window, text="请输入关键词进行搜索")
    status_label.pack(pady=10)

    window.mainloop()

# 启动程序
if __name__ == "__main__":
    create_ui()
