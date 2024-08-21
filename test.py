import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from ttkbootstrap import Style
import os
from scripts.anime_scrapper import AnimeFLV
import threading
from zipfile import ZipFile
from requests import get
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
from io import BytesIO
import webbrowser
import locale
import subprocess 

os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')

if os.name == "nt":
    if not os.path.exists(os.path.dirname(__file__) + "\\yt-dlp.exe"):
        print("Descargando depencia yt-dlp: ...")
        open(f'{os.path.dirname(__file__)}\\yt-dlp.exe', 'wb').write(get('https://raw.githubusercontent.com/matiasdante/files-4-animelibre/main/yt-dlp.exe').content)
    
    if not os.path.exists(os.path.dirname(__file__) + "\\libvlc.dll"):
        print("Downloading libvlc dependency: ...")
        open(f'{os.path.dirname(__file__)}\\libvlc.zip', 'wb').write(get('https://raw.githubusercontent.com/matiasdante/files-4-animelibre/main/libvlc.zip').content)
        print("Extracting libvlc.dll dependency: ...")
        ZipFile(f"{os.path.dirname(__file__)}\\libvlc.zip", "r").extractall(os.path.dirname(__file__))
        os.remove(f"{os.path.dirname(__file__)}\\libvlc.zip")

    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]

def callback(url):  # Funcion para abrir enlaces
    webbrowser.open_new_tab(url)

import vlc

locale.setlocale(locale.LC_NUMERIC, 'C')

class AnimeApp:
    def __init__(self, root): # Crear ventana principal
        self.root = root
        self.root.title("Anime Libre v1.1")
        self.root.resizable(0, 0)
        self.root.geometry('1024x800')
        self.root.iconbitmap(r'assets\mainicon.ico')
        self.api = AnimeFLV()
        self.setup_hidden_folder()
        self.widgets = []  # Lista para almacenar widgets
        self.set_background() # aplica el fondo
        self.mainmenu() # llama al menu principal

    def setup_hidden_folder(self):
        """Crea una carpeta oculta para almacenar temporalmente el video."""
        self.hidden_dir = os.path.join(os.path.dirname(__file__), ".anime_temp")
        if not os.path.exists(self.hidden_dir):
            os.makedirs(self.hidden_dir)
            os.system(f'attrib +h "{self.hidden_dir}"')
        else:
            # Elimina el archivo de video temporal si existe
            temp_file = os.path.join(self.hidden_dir, "temp_video.mp4")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def set_background(self): # Aplicar fondos de pantalla
        bg_image = Image.open(r"assets/background/background.jpg")
        bg_image = bg_image.resize((1024,800), Image.Resampling.LANCZOS)
        bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=4))
        enhancer = ImageEnhance.Brightness(bg_image)
        bg_image_darker = enhancer.enhance(0.5)
        self.bg_photo = ImageTk.PhotoImage(bg_image_darker)

        canvas = tk.Canvas(self.root, width=1024, height=800)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        style = Style(theme="darkly")  # Aplicar un tema oscuro

    def clear_widgets(self): # Limpiar los widgets
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def global_widgets(self): # Widgets utilizados en todos los menús
        header_frame = ttk.Frame(self.root)
        header_frame.place(x=10, y=10)
        self.widgets.append(header_frame)

        title_label = ttk.Label(header_frame, text="Anime Libre", font=("Osaka-Sans Serif", 20))
        title_label.pack(anchor="nw")
        self.widgets.append(title_label)

        subtitle_label = ttk.Label(header_frame, text="By Dou Community", foreground="#00a3ff", font=("Helvetica", 10), cursor="hand2")
        subtitle_label.pack(anchor="nw")
        subtitle_label.bind("<Button>", lambda event: callback("https://github.com/Dou-Community-S-A"))
        self.widgets.append(subtitle_label)

        mainmenu_button=ttk.Button(self.root, text="Menu Principal", cursor="hand2", command=self.mainmenu)
        mainmenu_button.place(x=800, y=20)
        self.widgets.append(mainmenu_button)

        optionsmenu_button=ttk.Button(self.root, text="Opciones", cursor="hand2", command=self.optionsmenu)
        optionsmenu_button.place(x=910, y=20)
        self.widgets.append(optionsmenu_button)
    
    def mainmenu(self): # Menu principal (Busqueda de anime)
        self.clear_widgets()
        self.global_widgets()

        ## ============== search_frame ======================
        search_frame = ttk.Frame(self.root)
        search_frame.place(x=200, y=20)
        self.widgets.append(search_frame)

        search_label = ttk.Label(search_frame, text="Buscar Anime:")
        search_label.pack(side=tk.LEFT)
        self.widgets.append(search_label)

        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.widgets.append(self.search_entry)

        search_button = ttk.Button(search_frame, text="Buscar", cursor="hand2", command=self.search_anime)
        search_button.pack(side=tk.LEFT)
        self.widgets.append(search_button)

        ## ============== main_frame ======================
        main_frame = ttk.Frame(self.root)
        main_frame.place(x=10, y=80, width=1004, height=320)
        self.widgets.append(main_frame)

        # Lista de resultados de búsqueda y imagen de portada
        results_frame = ttk.Frame(main_frame)
        results_frame.place(x=0, y=0, width=700, height=350)
        self.widgets.append(results_frame)

        self.results_listbox = tk.Listbox(results_frame, height=10, bg='black', fg='white')
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', self.load_anime_info)
        self.widgets.append(self.results_listbox)

        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.config(yscrollcommand=results_scrollbar.set)
        self.widgets.append(results_scrollbar)

        # Frame para la imagen de portada
        cover_frame = ttk.Frame(main_frame)
        cover_frame.place(x=710, y=0, width=284, height=350)
        self.widgets.append(cover_frame)

        self.cover_label = ttk.Label(cover_frame)
        self.cover_label.pack(side=tk.TOP, pady=(10, 10))
        self.widgets.append(self.cover_label)

        ## ============== info_frame ======================
        info_frame = ttk.Frame(self.root)
        info_frame.place(x=10, y=410, width=1004, height=200)
        self.widgets.append(info_frame)

        self.info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_text.config(state=tk.DISABLED)
        self.widgets.append(self.info_text)

        self.episodes_listbox = tk.Listbox(info_frame, height=10)
        self.episodes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.episodes_listbox.bind('<<ListboxSelect>>', self.load_episode_links)
        self.widgets.append(self.episodes_listbox)

        episodes_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.episodes_listbox.yview)
        episodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.episodes_listbox.config(yscrollcommand=episodes_scrollbar.set)
        self.widgets.append(episodes_scrollbar)

        ## ============== links_frame ======================
        links_frame = ttk.Frame(self.root)
        links_frame.place(x=10, y=620, width=1004, height=130)
        self.widgets.append(links_frame)

        self.links_listbox = tk.Listbox(links_frame, height=10)
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.links_listbox.bind('<<ListboxSelect>>', self.select_link)
        self.widgets.append(self.links_listbox)

        links_scrollbar = ttk.Scrollbar(links_frame, orient=tk.VERTICAL, command=self.links_listbox.yview)
        links_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.links_listbox.config(yscrollcommand=links_scrollbar.set)
        self.widgets.append(links_scrollbar)

        ## ============== play_button_frame ======================
        play_button_frame = ttk.Frame(self.root)
        play_button_frame.place(x=10, y=760, width=1004, height=30)
        self.widgets.append(play_button_frame)

        self.progress_bar = ttk.Progressbar(play_button_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.widgets.append(self.progress_bar)

        self.play_button = ttk.Button(play_button_frame, text="Play", cursor="hand2", command=self.play_selected_link)
        self.play_button.pack(side=tk.RIGHT)
        self.widgets.append(self.play_button)
        self.selected_link = None

    def optionsmenu(self): # Menu de configuraciones (Selector de reproductor)
        self.clear_widgets()
        self.global_widgets()

        options_label = ttk.Label(self.root, text="Opciones", font=("Helvetica", 16))
        options_label.place(x=200, y=80)
        self.widgets.append(options_label)
    
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
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Título: {self.api.anime_title()}\n")
            self.info_text.insert(tk.END, f"Estado: {self.api.anime_status()}\n")
            self.info_text.insert(tk.END, f"Sinopsis: {self.api.anime_summary()}\n")

            self.load_anime_cover(self.api.anime_cover())

            self.episodes_listbox.delete(0, tk.END)
            for i, episode in enumerate(self.api.anime_episodes(), 1):
                self.episodes_listbox.insert(tk.END, f"Episodio {i}")
            self.info_text.config(state=tk.DISABLED)

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
            temp_file = os.path.join(self.hidden_dir, "temp_video.mp4")

            print(f"Descargando video a {temp_file}...")
            result = subprocess.run(["yt-dlp", "-o", temp_file, video_src], check=True)

            if result.returncode == 0 and os.path.exists(temp_file):
                print(f"Reproduciendo video desde {temp_file}...")
                os.open(temp_file.mp4)
                while temp_file.is_playing():
                    pass
                print("Reproducción completada.")
            else:
                raise Exception("Error en la descarga o archivo no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir el video: {e}")
        finally:
            self.progress_bar.stop()


    def create_player(self):
        pass 

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeApp(root)
    root.mainloop()