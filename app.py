import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from ttkbootstrap import Style
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from scripts.anime_scrapper import AnimeFLV
import scripts.selected_rp as srp  
import threading
from zipfile import ZipFile
from requests import get
from io import BytesIO
import webbrowser
import locale
import subprocess
import sys


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

import mpv

def callback(url):  # Función para abrir enlaces
    webbrowser.open_new_tab(url)

locale.setlocale(locale.LC_NUMERIC, 'C')

class AnimeApp:
    def __init__(self, root):  # Crear ventana principal
        self.root = root
        self.root.title("Anime Libre v1.1")
        self.root.resizable(0, 0)
        self.root.geometry('1024x800')
        self.root.iconbitmap(r'assets\mainicon.ico')
        self.api = AnimeFLV()
        self.player_option = srp.get_selected_player()  # Cargar opción de reproductor seleccionada
        self.widgets = []  # Lista para almacenar widgets
        
        self.search_query = "" # Almacenar la búsqueda y los resultados
        self.search_results = []
        self.selected_anime_info = None

        self.clear_temp_folder()
        self.set_background()
        self.mainmenu()
    
    def clear_temp_folder(self): # Limpia la carpeta .temp
        temp_folder = os.path.join(os.path.dirname(__file__), '.temp')
        if os.path.exists(temp_folder):
            for file_name in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error al eliminar el archivo {file_path}: {e}")

    def set_background(self):  # Aplicar fondos de pantalla
        bg_image = Image.open(r"assets/background/background.jpg")
        bg_image = bg_image.resize((1024, 800), Image.Resampling.LANCZOS)
        bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=4))
        enhancer = ImageEnhance.Brightness(bg_image)
        bg_image_darker = enhancer.enhance(0.5)
        self.bg_photo = ImageTk.PhotoImage(bg_image_darker)

        canvas = tk.Canvas(self.root, width=1024, height=800)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        style = Style(theme="darkly")  # Aplicar un tema oscuro

    def clear_widgets(self):  # Limpiar los widgets
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def global_widgets(self):  # Widgets utilizados en todos los menús
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

        mainmenu_button = ttk.Button(self.root, text="Menu Principal", cursor="hand2", command=self.mainmenu)
        mainmenu_button.place(x=800, y=20)
        self.widgets.append(mainmenu_button)

        optionsmenu_button = ttk.Button(self.root, text="Opciones", cursor="hand2", command=self.optionsmenu)
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

        ## ========= recuperar busqueda (si hay)===========
        if self.search_query:
            self.search_entry.insert(0, self.search_query)
            self.results_listbox.delete(0, tk.END)
            for result in self.search_results:
                self.results_listbox.insert(tk.END, result)

            if self.selected_anime_info:
                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"Título: {self.selected_anime_info['title']}\n")
                self.info_text.insert(tk.END, f"Estado: {self.selected_anime_info['status']}\n")
                self.info_text.insert(tk.END, f"Sinopsis: {self.selected_anime_info['summary']}\n")
                self.load_anime_cover(self.selected_anime_info['cover'])
                self.episodes_listbox.delete(0, tk.END)
                for i, episode in enumerate(self.selected_anime_info['episodes'], 1):
                    self.episodes_listbox.insert(tk.END, f"Episodio {i}")
                self.info_text.config(state=tk.DISABLED)


        ## ============== play_button_frame ======================
        play_button_frame = ttk.Frame(self.root)
        play_button_frame.place(x=10, y=760, width=1004, height=30)
        self.widgets.append(play_button_frame)

        self.play_button = ttk.Button(play_button_frame, text="Play", cursor="hand2", command=self.on_play_button_clicked)
        self.play_button.pack(side=tk.RIGHT)
        self.widgets.append(self.play_button)
        self.selected_link = None

    def optionsmenu(self):  # Menú de configuraciones (Selector de reproductor)
        self.clear_widgets()
        self.global_widgets()

        options_label = ttk.Label(self.root, text="Opciones", font=("Helvetica", 16))
        options_label.place(x=200, y=80)
        self.widgets.append(options_label)

        # Selector de reproductor
        rp_frame = ttk.Frame(self.root)
        rp_frame.place(x=200, y=150)
        self.widgets.append(rp_frame)

        rp_label = ttk.Label(rp_frame, text="Seleccionar Reproductor:")
        rp_label.pack(side=tk.LEFT)
        self.widgets.append(rp_label)

        self.player_var = tk.StringVar(value=self.player_option)

        mpv_radio = ttk.Radiobutton(rp_frame, text="MPV", variable=self.player_var, value="mpv")
        mpv_radio.pack(side=tk.LEFT, padx=10)
        self.widgets.append(mpv_radio)

        default_radio = ttk.Radiobutton(rp_frame, text="Reproductor Predeterminado", variable=self.player_var, value="default")
        default_radio.pack(side=tk.LEFT)
        self.widgets.append(default_radio)

        save_button = ttk.Button(rp_frame, text="Guardar", command=self.save_player_option)
        save_button.pack(side=tk.LEFT, padx=10)
        self.widgets.append(save_button)

    def save_player_option(self): # Guarda el reproductor elegido por el usuario
        self.player_option = self.player_var.get()
        srp.save_selected_player(self.player_option)
        messagebox.showinfo("Información", "Opción de reproductor guardada con éxito.")

    def search_anime(self): # Buscar el Anime elegido por el usuario
        query = self.search_entry.get().strip()
        if query:
            self.search_query = query  # Guardar la búsqueda actual
            self.results_listbox.delete(0, tk.END)
            self.search_results = self.api.search(query)  # Guardar los resultados de búsqueda
            for result in self.search_results:
                self.results_listbox.insert(tk.END, result)
        else:
            messagebox.showwarning("Advertencia", "Ingrese un título de anime para buscar.")

    def load_anime_info(self, event): # Cargar la info del anime elegido
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            anime_id = self.results_listbox.get(index)
            self.api.anime_info(anime_id)
            self.selected_anime_info = {
                "title": self.api.anime_title(),
                "status": self.api.anime_status(),
                "summary": self.api.anime_summary(),
                "cover": self.api.anime_cover(),
                "episodes": self.api.anime_episodes(),
            }
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Título: {self.selected_anime_info['title']}\n")
            self.info_text.insert(tk.END, f"Estado: {self.selected_anime_info['status']}\n")
            self.info_text.insert(tk.END, f"Sinopsis: {self.selected_anime_info['summary']}\n")
            self.load_anime_cover(self.selected_anime_info['cover'])
            self.episodes_listbox.delete(0, tk.END)
            for i, episode in enumerate(self.selected_anime_info['episodes'], 1): # Carga lista de Episodios
                self.episodes_listbox.insert(tk.END, f"Episodio {i}")
            self.info_text.config(state=tk.DISABLED)

    def load_anime_cover(self, cover_url): # Cargar la portada del anime elegido
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

    def load_episode_links(self, event): # Cargar links del episodio elegido
        selection = self.episodes_listbox.curselection()
        if selection:
            episode_index = selection[0]
            links = self.api.get_links(episode_index + 1)
            self.links_listbox.delete(0, tk.END)
            for link in links: # Inserta los links en el recuadro de la interfaz
                self.links_listbox.insert(tk.END, link)

    def on_play_button_clicked(self): # Deteccion del boton play para reproducir el episodio
        if self.selected_link:
            if self.player_option == "mpv": # Eleccion entre mpv o default
                self.play_with_mpv(self.selected_link)
            else:
                self.play_with_default(self.selected_link)
        else:
            messagebox.showwarning("Advertencia", "No se ha seleccionado ningún enlace.")

    def select_link(self, event): # Seleccion de link
        selection = self.links_listbox.curselection()
        if selection:
            link_index = selection[0]
            self.selected_link = self.links_listbox.get(link_index)

    def play_with_mpv(self, link): # Reproducir con MPV
        player = mpv.MPV(ytdl=True, input_default_bindings=True, osc=True)
        player.play(link)
    
    '''
    # Posible fix a futuro (Error al cerrar MPV de forma forzada)
    def cerrar_aplicacion(): # Consulta para confirmar cierre aplicacion
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?"):
            # Cerrar la ventana principal
            root.destroy()

            # Si se estaba reproduciendo un video, intentar cerrar el reproductor
            if reproductor_seleccionado == "mpv":
                subprocess.call(["taskkill", "/IM", "mpv.exe", "/F"])

            # Termina completamente la aplicación
            sys.exit()
    '''

    def play_with_default(self, link): # Reproducir con el reproductor predeterminado del sistema (VLC, WMP, etc.)
        temp_folder = os.path.join(os.path.dirname(__file__), '.temp')
        os.makedirs(temp_folder)

        # Contar el número de archivos existentes en la carpeta para determinar el siguiente índice
        existing_files = [f for f in os.listdir(temp_folder) if f.startswith('temp_video') and f.endswith('.mp4')]
        if existing_files:
            # Extraer el índice más alto y sumarle 1
            indices = [int(f.split('_')[2].split('.')[0]) for f in existing_files]
            next_index = max(indices) + 1
        else:
            next_index = 0

        # Generar el nombre del archivo
        video_filename = f"temp_video{next_index}.mp4"
        video_file = os.path.join(temp_folder, video_filename)
        subprocess.run(['yt-dlp', '-o', video_file, link]) # Descargar el video utilizando yt-dlp
        subprocess.run(['start', '', video_file], shell=True) # Reproducir el video con el reproductor predeterminado
    

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeApp(root)
    root.mainloop()