import requests
from bs4 import BeautifulSoup
import re
import json
import os

# 全局变量存储歌曲信息
music_info = []

# 搜索歌曲的功能
def search_music(query):
    search_url = f"https://cdn.crashmc.com/https://www.gequbao.com/s/{query}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            rows = soup.find_all('div', class_='row')
            music_info.clear()  # 清空之前的搜索结果

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
                    print(f"{i} | {title} - {artist}")
                    i += 1

            print(f"搜索到 {len(music_info)} 首歌曲")
        else:
            print("搜索失败，请重试。")
    except Exception as e:
        print(f"错误: {e}")

# 获取歌曲下载链接
def fetch_download_link(music_index):
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
                    download_song(download_url, f"{title} - {artist}.mp3")
                else:
                    print("获取下载链接失败")
            else:
                print("未找到 play-id")
        else:
            print("无法访问歌曲详情页")
    except Exception as e:
        print(f"错误: {e}")

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
def download_song(download_url, file_name):
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            # 保存歌曲文件
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"歌曲下载完成: {file_name}")
        else:
            print("下载失败")
    except Exception as e:
        print(f"下载错误: {e}")

if __name__ == "__main__":
    while True:
        query = input("请输入要搜索的歌曲名 (输入 'exit' 退出): ").strip()
        if query.lower() == 'exit':
            break
        search_music(query)
        
        if not music_info:
            continue
        
        try:
            music_index = int(input("请输入要下载的歌曲编号: ")) - 1
            if 0 <= music_index < len(music_info):
                fetch_download_link(music_index)
            else:
                print("无效的编号")
        except ValueError:
            print("请输入有效的数字")
