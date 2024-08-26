import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from ttkbootstrap import Style
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from scripts.anime_scrapper import AnimeFLV
import scripts.app_config as cfg  
import threading
from zipfile import ZipFile
from requests import get
from io import BytesIO
import webbrowser
import locale
import subprocess
import sys
import ctypes
import textwrap


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
    # =========== Setear ventana principal =================
    def __init__(self, root):  # Crear ventana principal
        self.root = root
        self.root.title("Anime Libre v1.1")
        self.root.resizable(0, 0)
        self.root.geometry('1024x800')
        self.root.iconbitmap(r'assets\mainicon.ico')
        self.api = AnimeFLV()
        self.player_option = cfg.get_selected_player()  # Cargar opción de reproductor seleccionada
        self.widgets = []  # Lista para almacenar widgets
        
        # Almacenar la búsqueda y los resultados
        self.search_query = ""
        self.search_results = []
        self.selected_anime_info = None
        # Almacenar el link, anime y episodio seleccionado para despues guardarlo
        self.selected_link = None
        self.current_anime_id = None
        self.current_episode_number = None

        self.clear_temp_folder()
        self.set_background()
        self.mainmenu()

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

        title_label = ttk.Label(header_frame, text="Anime Libre", font=("Osaka-Sans Serif", 20), cursor="hand2")
        title_label.pack(anchor="nw")
        title_label.bind("<Button>", lambda event: self.mainmenu())
        self.widgets.append(title_label)

        subtitle_label = ttk.Label(header_frame, text="By Dou Community", foreground="#00a3ff", font=("Helvetica", 10), cursor="hand2")
        subtitle_label.pack(anchor="nw")
        subtitle_label.bind("<Button>", lambda event: callback("https://github.com/Dou-Community-S-A"))
        self.widgets.append(subtitle_label)

        searchmenu_button = ttk.Button(self.root, text="Buscador", cursor="hand2", command=self.searchmenu)
        searchmenu_button.place(x=725, y=20)
        self.widgets.append(searchmenu_button)

        recentmenu_button = ttk.Button(self.root, text="Animes vistos", cursor="hand2", command=self.recentmenu)
        recentmenu_button.place(x=810, y=20)
        self.widgets.append(recentmenu_button)

        optionsmenu_button = ttk.Button(self.root, text="Opciones", cursor="hand2", command=self.optionsmenu)
        optionsmenu_button.place(x=920, y=20)
        self.widgets.append(optionsmenu_button)
    

    # =================== Menús ===========================

    def mainmenu(self): # Menú principal (Changelog)
        self.clear_widgets()
        self.global_widgets()

        title_label = ttk.Label(self.root, text="Anime Libre v1.1 (Pre-Release)", font=("Helvetica", 25))
        title_label.place(x=10, y=80)
        self.widgets.append(title_label)

        date_label = ttk.Label(self.root, text="26/08/24", font=("Helvetica", 15))
        date_label.place(x=480, y=88)
        self.widgets.append(date_label)

        changelog_text = tk.Text(self.root, height=10, width=150, wrap=tk.WORD)
        changelog_text.place(x=10, y=150)
        changelog_text.tag_configure("changelog", font=("Arial", 13))
        changelog = ("CHANGE LOG:\n"
        "* Fondo e interfaz mejoradas (dentro de lo posible)\n"
        "* 3 nuevos menús: Menú principal (este mismo), Animes vistos y Opciones\n"
        "* Ahora se guardan los animes que viste, a futuro desde ahi podras acceder a ellos directamente\n"
        "* Ahora puedes elegir si usar el reproductor integrado con la app o el reproductor predeterminado de tu PC. Esto en el menu de opciones.\n"
        "* Ahora los resultados se muestran sin guiones :3\n"        
        )
        changelog_text.insert(tk.END, changelog, "changelog")
        changelog_text.config(state=tk.DISABLED)
        self.widgets.append(changelog_text)
        
    def searchmenu(self): # Menú del buscador (Busqueda de anime)
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

        '''
        comentado para evitar errores al volver al buscador
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
                self.info_text.insert(tk.END, "\n")
                self.info_text.insert(tk.END, f"Estado: {self.selected_anime_info['status']}\n")
                self.info_text.insert(tk.END, "\n")
                self.info_text.insert(tk.END, f"Sinopsis: {self.selected_anime_info['summary']}\n")
                self.load_anime_cover(self.selected_anime_info['cover'])
                self.episodes_listbox.delete(0, tk.END)
                for i, episode in enumerate(self.selected_anime_info['episodes'], 1):
                    self.episodes_listbox.insert(tk.END, f"Episodio {i}")
                self.info_text.config(state=tk.DISABLED)
        '''

        ## ============== play_button_frame ======================
        play_button_frame = ttk.Frame(self.root)
        play_button_frame.place(x=10, y=760, width=1004, height=30)
        self.widgets.append(play_button_frame)

        self.play_button = ttk.Button(play_button_frame, text="Play", cursor="hand2", command=self.on_play_button_clicked)
        self.play_button.pack(side=tk.RIGHT)
        self.widgets.append(self.play_button)
        self.selected_link = None

    def recentmenu(self): # Menú de animes recientes (muestra una lista de cuantos usaste)
        self.clear_widgets()  # Limpia los widgets existentes
        self.global_widgets()  # Vuelve a cargar los widgets globales

        # Crear un frame para contener el canvas y la scrollbar
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        # Etiqueta para el menú de animes vistos
        watched_label = ttk.Label(self.root, text="Animes vistos:", font=("Helvetica", 16))
        watched_label.place(x=10, y=80)
        self.widgets.append(watched_label)

        x_position = 10  # Posición inicial para colocar los widgets en la fila
        y_position = 130  # Posición vertical inicial en el frame
        max_columns = 6   # Número máximo de columnas
        column_width = 150  # Ancho de cada imagen
        row_height = 250  # Altura de cada fila (imagen + espacio para el título)

        # Obtener la lista de animes vistos
        data = cfg.load_config()
        watched_animes = data.get('visto', {})

        # Añadir animes al frame
        for index, (anime_id, episodes) in enumerate(watched_animes.items()):
            # Obtener la información del anim
            self.api.anime_info(anime_id)
            self.anime_info = {
                "title": self.api.anime_title(),
                "cover": self.api.anime_cover()
            }

            if self.anime_info['cover']:
                # Obtener y procesar la imagen de portada
                response = get(self.anime_info['cover'])
                image_data = response.content
                image = Image.open(BytesIO(image_data))
                image = image.resize((150, 200), Image.Resampling.LANCZOS)  # Ajusta el tamaño según sea necesario
                photo = ImageTk.PhotoImage(image)
            else:
                photo = None

            # Etiqueta para la portada
            cover_label = ttk.Label(self.root, image=photo)
            cover_label.place(x=x_position, y=y_position)
            self.widgets.append(cover_label)

            # Etiqueta para el nombre del anime
            wrapped_title = '\n'.join(textwrap.wrap(self.anime_info['title'], width=17)) # Hace un salto de linea en caso de llegar a mas de 17 caracteres
            title_label = ttk.Label(self.root, text=wrapped_title, font=("Helvetica", 10))
            title_label.place(x=x_position, y=y_position + 210)  # Ajusta la posición según sea necesario
            self.widgets.append(title_label)

            # Actualizar la posición para la próxima imagen
            x_position += column_width + 10  # Añadir un margen de 10 píxeles entre columnas

            # Cambiar de fila después de tres columnas
            if (index + 1) % max_columns == 0:
                x_position = 10  # Reiniciar posición horizontal
                y_position += row_height  # Mover hacia abajo para la siguiente fila

            # Mantener una referencia a la imagen para evitar la recolección de basura
            if photo:
                cover_label.image = photo


        # Configurar el frame en el contenedor principal para expandirse
        container.pack_propagate(False)
        container.update_idletasks()

        # Asegurarse de que el contenedor se expanda para llenar la ventana
        self.root.update_idletasks()

    def optionsmenu(self):  # Menú de configuraciones (Selector de reproductor)
        self.clear_widgets()
        self.global_widgets()

        options_label = ttk.Label(self.root, text="Opciones:", font=("Helvetica", 16))
        options_label.place(x=10, y=80)
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

    # =================== Funciones =======================

    def save_player_option(self): # Guarda el reproductor elegido por el usuario
        self.player_option = self.player_var.get()
        cfg.save_selected_player(self.player_option)
        messagebox.showinfo("Información", "Opción de reproductor guardada con éxito.")

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

    def search_anime(self): # Buscar el Anime elegido por el usuario
        query = self.search_entry.get().strip()
        if query:
            self.search_query = query  # Guardar la búsqueda actual
            self.results_listbox.delete(0, tk.END)
            self.search_results = self.api.search(query)  # Guardar los resultados de búsqueda
            self.anime_dict = {} # Creamos un diccionario para despues mostrar los resultados sin guion
            self.mod_results = [result.replace("-", " ") for result in self.search_results] 
            for original, modified in zip(self.search_results, self.mod_results):
                self.anime_dict[modified] = original
                self.results_listbox.insert(tk.END, modified)
        else:
            messagebox.showwarning("Advertencia", "Ingrese un título de anime para buscar.")

    def load_anime_info(self, event): # Carga la informacion del anime elegido
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            modified_name = self.results_listbox.get(index) # Conseguimos el nombre con guiones del diccionario creado anteriormente
            original_name = self.anime_dict.get(modified_name)
            if original_name:
                anime_id = original_name
                self.current_anime_id = anime_id
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
        self.info_text.insert(tk.END, "\n")
        self.info_text.insert(tk.END, f"Estado: {self.selected_anime_info['status']}\n")
        self.info_text.insert(tk.END, "\n")
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
            self.current_episode_number = episode_index + 1
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
        print(self.current_anime_id)
        cfg.mark_as_seen(self.current_anime_id, self.current_episode_number)
    
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
    
    # Crear la carpeta .temp si no existe y establecer el atributo de oculto
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
            # Establecer el atributo de oculto
            if os.name == 'nt': 
                ctypes.windll.kernel32.SetFileAttributesW(temp_folder, 2)

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
        cfg.mark_as_seen(self.current_anime_id, self.current_episode_number)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeApp(root)
    root.mainloop()