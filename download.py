import os
import re
from pytube import Playlist 
from pytube.exceptions import PytubeError
from pytubefix import YouTube
from pytubefix.cli import on_progress

# URL de la playlist YouTube
playlist_url = 'https://www.youtube.com/watch?v=82KLS2C_gNQ&list=PLO_fdPEVlfKqMDNmCFzQISI2H_nJcEDJq'

# Créer l'objet Playlist
playlist = Playlist(playlist_url)

# Nettoyer le titre de la playlist en remplaçant les caractères non alphabétiques par des tirets '-'
if playlist.title:
    playlist_title = re.sub(r'[^a-zA-Z0-9\s]', '-', playlist.title)
    playlist_title = re.sub(r'\s+', '-', playlist_title)  # Remplacer les espaces par des tirets
else:
    playlist_title = "Playlist_Sans_Nom"

# Créer le chemin de téléchargement
download_path = os.path.join(os.path.expanduser("~"), "Downloads", playlist_title)


# Vérifier si le dossier existe, sinon le créer
os.makedirs(download_path, exist_ok=True)

print(f'Téléchargement de la playlist : {playlist_title}')

# Parcourir et télécharger chaque vidéo de la playlist
for video_url in playlist.video_urls:
    try:
        video = YouTube(video_url, on_progress_callback = on_progress)
        print(f'Téléchargement en cours : {video.title}')
        video.streams.get_highest_resolution().download(download_path)
        print(f'Vidéo téléchargée : {video.title}')
    except KeyError as e:
        print(f"Impossible d'accéder aux détails de la vidéo : {video_url}. Erreur : {e}")
    except PytubeError as e:
        print(f"Erreur Pytube lors du téléchargement de {video_url}. Détails : {e}")
    except Exception as e:
        print(f"Erreur inattendue lors du téléchargement de {video_url}. Détails : {e}")

print('Téléchargement terminé.')
