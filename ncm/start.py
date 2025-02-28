import os
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.parse import urlparse, parse_qs

from ncm import config
from ncm.api import CloudApi
from ncm.constants import add_cookies
from ncm.constants import headers
from ncm.downloader import download_song_by_id
from ncm.downloader import download_song_by_song
from ncm.downloader import format_string
from ncm.downloader import get_song_info_by_id

# load the config first
config.load_config()
api = CloudApi()

def download_hot_songs(artist_id):
    songs = api.get_hot_songs(artist_id)
    folder_name = format_string(songs[0]['artists'][0]['name']) + ' - hot50'
    folder_path = os.path.join(config.DOWNLOAD_DIR, folder_name)
    download_count = config.DOWNLOAD_HOT_MAX if (0 < config.DOWNLOAD_HOT_MAX < 50) else config.DOWNLOAD_HOT_MAX_DEFAULT
    for i, song in zip(range(download_count), songs):
        print('{}: {}'.format(i + 1, song['name']))
        download_song_by_song(song, folder_path, False)

def download_album_songs(album_id):
    songs = api.get_album_songs(album_id)
    folder_name = format_string(songs[0]['album']['name']) + ' - album'
    folder_path = os.path.join(config.DOWNLOAD_DIR, folder_name)
    for i, song in enumerate(songs):
        print('{}: {}'.format(i + 1, song['name']))
        download_song_by_song(song, folder_path, False)

def download_program(program_id):
    program = api.get_program(program_id)
    folder_name = format_string(program['dj']['brand']) + ' - program'
    folder_path = os.path.join(config.DOWNLOAD_DIR, folder_name)
    download_song_by_song(program, folder_path, False, True)

def download_playlist_songs(playlist_id):
    songs, playlist_name = api.get_playlist_songs(playlist_id)
    folder_name = format_string(playlist_name) + ' - playlist'
    folder_path = os.path.join(config.DOWNLOAD_DIR, folder_name)
    for i, song in enumerate(songs):
        song_detail = get_song_info_by_id(song['id'])
        print('{}: {}'.format(i + 1, song_detail['name']))
        download_song_by_song(song_detail, folder_path, False)

def get_parse_id(song_id):
    if song_id.startswith('http'):
        return parse_qs(urlparse(song_id, allow_fragments=False).query)['id'][0]
    return song_id

def handle_download(option_var):
    option = option_var.get()
    print("Option:", option)
    if option == "song_id":
        song_id = song_id_entry.get()
        if song_id:
            download_song_by_id(get_parse_id(song_id), config.DOWNLOAD_DIR)
    elif option == "song_ids":
        song_ids = song_ids_entry.get().split()
        for sid in song_ids:
            download_song_by_id(get_parse_id(sid), config.DOWNLOAD_DIR)
    elif option == "artist_id":
        artist_id = artist_id_entry.get()
        if artist_id:
            download_hot_songs(get_parse_id(artist_id))
    elif option == "album_id":
        album_id = album_id_entry.get()
        if album_id:
            download_album_songs(get_parse_id(album_id))
    elif option == "program_id":
        program_id = program_id_entry.get()
        if program_id:
            download_program(get_parse_id(program_id))
    elif option == "playlist_id":
        playlist_id = playlist_id_entry.get()
        if playlist_id:
            download_playlist_songs(get_parse_id(playlist_id))

    messagebox.showinfo("完成", "已完成")

def set_cookies(cookies_entry):
    cookies = cookies_entry.get().split()
    for cookie in cookies:
        key, value = cookie.replace("\n", "").replace(" ", "").replace("\t", "").split('=')
        add_cookies(key, value)

def open_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("设置")

    # 设置窗口大小
    settings_width = 340
    settings_height = 110
    center_window(settings_window, settings_width, settings_height)

    tk.Label(settings_window, text="User-Agent:").grid(row=0, column=0, padx=5, pady=5)
    user_agent_entry = tk.Entry(settings_window)
    user_agent_entry.grid(row=0, column=1, padx=5, pady=5)

    save_button = tk.Button(settings_window, text="设置UA", command=lambda: {'User-Agent': user_agent_entry})
    save_button.grid(row=0, column=2, padx=5, pady=10)

    tk.Label(settings_window, text="Cookies (k=v):").grid(row=1, column=0, padx=5, pady=5)
    cookies_entry = tk.Entry(settings_window)
    cookies_entry.grid(row=1, column=1, padx=5, pady=5)

    save_button = tk.Button(settings_window, text="设置Cookie", command=lambda: set_cookies(cookies_entry))
    save_button.grid(row=1, column=2, padx=5, pady=10)

    # 设置焦点到设置窗口
    settings_window.focus_force()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    global root, song_id_entry, song_ids_entry, artist_id_entry, album_id_entry, program_id_entry, playlist_id_entry

    root = tk.Tk()
    root.title("网易云音乐下载器")

    # 设置窗口大小
    window_width = 260
    window_height = 250
    center_window(root, window_width, window_height)

    # 下载选项
    option_var = tk.StringVar(value="song_id")
    options = ["Song ID", "Song IDs", "Artist ID", "Album ID", "Program ID", "Playlist ID"]
    for idx, option in enumerate(options):
        rb = ttk.Radiobutton(root, text=option, variable=option_var, value=option.lower().replace(" ", "_"))
        rb.grid(row=idx+1, column=0, sticky="w", padx=5, pady=5)

    # 输入框
    song_id_entry = tk.Entry(root)
    song_id_entry.grid(row=1, column=1, padx=5, pady=5)

    song_ids_entry = tk.Entry(root)
    song_ids_entry.grid(row=2, column=1, padx=5, pady=5)

    artist_id_entry = tk.Entry(root)
    artist_id_entry.grid(row=3, column=1, padx=5, pady=5)

    album_id_entry = tk.Entry(root)
    album_id_entry.grid(row=4, column=1, padx=5, pady=5)

    program_id_entry = tk.Entry(root)
    program_id_entry.grid(row=5, column=1, padx=5, pady=5)

    playlist_id_entry = tk.Entry(root)
    playlist_id_entry.grid(row=6, column=1, padx=5, pady=5)

    # 设置页面按钮
    settings_button = tk.Button(root, text="设置", command=open_settings_window)
    settings_button.grid(row=7, column=0, columnspan=1, pady=10)

    # 下载按钮
    download_button = tk.Button(root, text="下载", command=lambda: handle_download(option_var))
    download_button.grid(row=7, column=1, columnspan=2, pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()
