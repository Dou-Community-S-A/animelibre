import requests
from bs4 import BeautifulSoup

# URL de la página web
url = "https://streamtape.com/v/z1XYM0q0KwCYa6Y/"

# Hacer una solicitud GET a la página
response = requests.get(url)

# Verificar que la solicitud fue exitosa
if response.status_code == 200:
    # Analizar el contenido HTML de la página
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Buscar el elemento con id "mainvide"
    main_video_block = soup.find(id="mainvideo")
    
    if main_video_block:
        # Buscar la etiqueta de video dentro del bloque
        video_tag = main_video_block.find("video")
        
        if video_tag:
            # Obtener el atributo 'src' del video
            video_src = video_tag.get("src")
            
            if video_src:
                print("URL del video:", video_src)
            else:
                print("No se encontró la URL del video.")
        else:
            print("No se encontró la etiqueta de video dentro del bloque con id 'mainvideo'.")
    else:
        print("No se encontró el bloque con id 'mainvide'.")
else:
    print("Error al hacer la solicitud a la página:", response.status_code)
