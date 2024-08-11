import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from ttkbootstrap import Style
import os
from scripts.anime_scrapper import AnimeFLV
import os
import threading
from zipfile import ZipFile
from requests import get
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import locale

if os.name == "nt":
    if not os.path.exists(os.path.dirname(__file__) + "\\yt-dlp.exe"):
        print("Descargando depencia yt-dlp: ...")
        open(f'{os.path.dirname(__file__)}\\yt-dlp.exe', 'wb').write(get('https://raw.githubusercontent.com/agus-balles/files/main/yt-dlp.exe').content)
    
    if not os.path.exists(os.path.dirname(__file__) + "\\libmpv-2.dll"):
        from zipfile import ZipFile
        print("Descargando Dependencia libmpv: ...")
        open(f'{os.path.dirname(__file__)}\\libmpv-2.zip', 'wb').write(get('https://raw.githubusercontent.com/agus-balles/files/main/libmpv-2.zip').content)
        print("Extrayendo depencia libmpv-2.dll: ...")
        ZipFile(f"{os.path.dirname(__file__)}\\libmpv-2.zip", "r").extractall(os.path.dirname(__file__))
        os.remove(f"{os.path.dirname(__file__)}\\libmpv-2.zip")
    
    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
    
def callback(url):  # Funcion para abrir enlaces
        webbrowser.open_new_tab(url)

import mpv

locale.setlocale(locale.LC_NUMERIC, 'C')

class AnimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Libre v1.0")
        self.root.resizable(0, 0)
        self.root.tk.call('tk', 'scaling', 1.25)
        self.root.geometry('1024x768')
        self.root.iconbitmap(r'assets\mainicon.ico')
        self.api = AnimeFLV()



        # Nombre de la app
        header_frame = ttk.Frame(self.root)
        header_frame.place(x=10, y=2) 
        
        title_label = ttk.Label(header_frame, text="Anime Libre", font=("Osaka-Sans Serif", 20))
        title_label.pack(anchor="nw")
        
        subtitle_label = ttk.Label(header_frame, text="By Dou Community", foreground="#00a3ff" ,font=("Helvetica", 10))
        subtitle_label.pack(anchor="nw")
        subtitle_label.bind("<Button>", lambda event: callback("https://github.com/Dou-Community-S-A"))

        style = Style(theme="darkly")  # Aplicar un tema oscuro

        # Frame de búsqueda
        search_frame = ttk.Frame(self.root)
        search_frame.pack(padx=10, pady=10)

        search_label = ttk.Label(search_frame, text="Buscar Anime:")
        search_label.pack(side=tk.LEFT)

        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10)

        search_button = ttk.Button(search_frame, text="Buscar", command=self.search_anime)
        search_button.pack(side=tk.LEFT)

        # Frame principal para resultados y portada
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Lista de resultados de búsqueda y imagen de portada
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.results_listbox = tk.Listbox(results_frame, height=10, bg='black', fg='white')
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self.load_anime_info)

        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=results_scrollbar.set)

        # Frame para la imagen de portada
        cover_frame = ttk.Frame(main_frame)
        cover_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y, expand=False)

        self.cover_label = ttk.Label(cover_frame)
        self.cover_label.pack(side=tk.TOP, pady=10)

        # Información del anime y lista de episodios
        info_frame = ttk.Frame(self.root)
        info_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.episodes_listbox = tk.Listbox(info_frame, height=10)
        self.episodes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.episodes_listbox.bind('<<ListboxSelect>>', self.load_episode_links)

        episodes_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.episodes_listbox.yview)
        episodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.episodes_listbox.config(yscrollcommand=episodes_scrollbar.set)

        # Lista de enlaces del episodio
        links_frame = ttk.Frame(self.root)
        links_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.links_listbox = tk.Listbox(links_frame, height=10)
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.links_listbox.bind('<<ListboxSelect>>', self.select_link)

        links_scrollbar = ttk.Scrollbar(links_frame, orient=tk.VERTICAL, command=self.links_listbox.yview)
        links_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.links_listbox.config(yscrollcommand=links_scrollbar.set)

        # Estilo personalizado para la barra de progreso
        style = ttk.Style()
        style.configure("custom.Horizontal.TProgressbar",
                        troughcolor='lightgray',
                        background='green',
                        thickness=300)  # Cambia el grosor aquí

        # Frame para la barra de progreso y el botón de reproducción
        play_button_frame = ttk.Frame(self.root)
        play_button_frame.pack(padx=10, pady=10, fill=tk.X, side=tk.BOTTOM)

        self.progress_bar = ttk.Progressbar(play_button_frame, style="custom.Horizontal.TProgressbar", mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.play_button = ttk.Button(play_button_frame, text="Play", command=self.play_selected_link)
        self.play_button.pack(side=tk.RIGHT)
        self.selected_link = None

    
    def search_anime(self):
        query = self.search_entry.get().strip()
        if query:
            self.results_listbox.delete(0, tk.END)
            results = self.api.search(query)
            for result in results:
                self.results_listbox.insert(tk.END, result)
        else:
            messagebox.showwarning("Advertencia", "Ingrese un título de anime para buscar.")

    def load_anime_info(self, event):
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            anime_id = self.results_listbox.get(index)
            self.api.anime_info(anime_id)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Título: {self.api.anime_title()}\n")
            self.info_text.insert(tk.END, f"Estado: {self.api.anime_status()}\n")
            self.info_text.insert(tk.END, f"Sinopsis: {self.api.anime_summary()}\n")

            self.load_anime_cover(self.api.anime_cover())

            self.episodes_listbox.delete(0, tk.END)
            for i, episode in enumerate(self.api.anime_episodes(), 1):
                self.episodes_listbox.insert(tk.END, f"Episodio {i}")

    def load_anime_cover(self, cover_url):
        if cover_url:
            response = get(cover_url)
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            image = image.resize((200, 300), Image.Resampling.LANCZOS)  # Ajusta el tamaño según sea necesario
            photo = ImageTk.PhotoImage(image)
            self.cover_label.config(image=photo)
            self.cover_label.image = photo
        else:
            self.cover_label.config(image='')

    def load_episode_links(self, event):
        selection = self.episodes_listbox.curselection()
        if selection:
            episode_index = selection[0]
            links = self.api.get_links(episode_index + 1)
            self.links_listbox.delete(0, tk.END)
            for link in links:
                self.links_listbox.insert(tk.END, link)

    def select_link(self, event):
        selection = self.links_listbox.curselection()
        if selection:
            link_index = selection[0]
            self.selected_link = self.links_listbox.get(link_index)

    def play_selected_link(self):
        if self.selected_link:
            self.progress_bar.start()  # Iniciar la barra de progreso
            threading.Thread(target=self.watch_video, args=(self.selected_link,)).start()
        else:
            messagebox.showwarning("Advertencia", "Seleccione un enlace para reproducir.")

    def watch_video(self, video_src):
        try:
            player = self.create_player()
            player.play("ytdl://" + video_src)
            player.wait_for_playback()
            player.terminate()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir el video: {e}")
        finally:
            self.progress_bar.stop()  # Detener la barra de progreso cuando el video comience o si hay un error

    def create_player(self):
        return mpv.MPV(ytdl=True, osc=True, input_default_bindings=True, input_vo_keyboard=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeApp(root)
    root.mainloop()
