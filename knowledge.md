# Avances 27.07.2024

* Se encontro la forma de conseguir el link de stape, para reproducirlo en VLC
  * Entramos a stape
  * Apretamos F12
  * Buscamos la class=plyr__video-wrapper
  * Buscamos la src del mismo nombre de esa class.
  * Ingresamos a ese link.
  * Volvemos a inspeccionar los elementos
  * Encontraremos el formato del archivo .mp4
* Se empezo a analizar factibilidad para la extraccion de ese contenido con webscrapping (request o selenium)
  * Ingresar a la pagina y extraer el video para mandarlo a VLC
* Se hizo un merge de la primera version del dev al main como copia de seguridad.
* Se creo un test.py para hacer pruebas de diversas cosas.
* Se creo knowledge.md para guardar los avances de la fecha.

# Avances 28.07.2024

* Se implemento selenium para hacer webscrapping al link de stape
* Se cargo con vlc dicho video
* Se espera a Facundo (LostDou) para implementacion de UI en tkinter.

# Avances 03.08.2024

* Se scrappeo todos los sitios web de animeflv
* Se reproducen correctamente en mpv
* Proximamente se investigara como hacer para integrarlo a un bot de discord. :)
