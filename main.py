import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from animeflv import AnimeFLV, EpisodeInfo, AnimeInfo

# Función para abrir enlace en VLC
def open_in_vlc(video_src):
    vlc_path = "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"  # Cambia esta ruta si VLC está instalado en otro lugar
    subprocess.run([vlc_path, video_src])

# Función para configurar y obtener el WebDriver
def get_webdriver(driver_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless
    chrome_options.add_argument("--disable-gpu")  # Deshabilitar GPU
    chrome_options.add_argument("--window-size=1920x1080")  # Establecer tamaño de ventana para headless
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Configura el WebDriver
driver_path = 'D:\\GitClones\\web-scraping-selenium\\chromedriver.exe'  # Cambia esta ruta al lugar donde tengas tu chromedriver

try:
    with AnimeFLV() as api:
        try:
            anime_name = input("Anime: ")
            anime_list = api.search(anime_name)
            for i, anime in enumerate(anime_list):
                print(f"{i} - {anime.title}")

            while True:
                try:
                    select = int(input("Opción: "))
                    if 0 <= select < len(anime_list):
                        break
                    else:
                        print("Por favor, ingresa un número dentro del rango.")
                except ValueError:
                    print("Por favor, ingresa un número válido.")

            selected_anime = anime_list[select]
            info = api.get_anime_info(selected_anime.id)
            info.episodes.reverse()

            for j, episode in enumerate(info.episodes):
                print(f"{j} - {episode.id}")

            while True:
                try:
                    ep = int(input("Opción de episodio: "))
                    if 0 <= ep < len(info.episodes):
                        break
                    else:
                        print("Por favor, ingresa un número dentro del rango.")
                except ValueError:
                    print("Por favor, ingresa un número válido.")

            serie = selected_anime.id
            capitulo = info.episodes[ep].id
            links = api.get_links(serie, capitulo)

            # Filtra el enlace de 'stape'
            stape_link = None
            for link in links:
                if 'stape' in link.server.lower():
                    stape_link = link.url
                    print(f"Stape link: {stape_link}")
                    break

            if stape_link:
                # Configura el WebDriver en modo headless
                driver = get_webdriver(driver_path)

                # Abre la página del enlace de 'stape' con Selenium
                driver.get(stape_link)

                # Espera explícita para el elemento de video en la nueva página
                wait = WebDriverWait(driver, 10)
                video_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'plyr__video-wrapper')))
                video_element = video_div.find_element(By.TAG_NAME, 'video')

                # Obtén el atributo 'src' del elemento de video
                video_src = video_element.get_attribute('src')
                print('El enlace del video es:', video_src)

                # Abre el enlace del video con VLC
                open_in_vlc(video_src)
            else:
                print('No se encontró un enlace de Stape.')

        except Exception as e:
            print(f"Error al obtener los enlaces del anime: {e}")

except Exception as e:
    print(f"Error al obtener el enlace del video: {e}")

finally:
    try:
        driver.quit()
    except:
        pass
