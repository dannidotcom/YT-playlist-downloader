import os
import re
import argparse
from pytube.exceptions import PytubeError
from pytubefix.cli import on_progress
from pytube import Playlist 
from pytube.exceptions import PytubeError
from pytubefix import YouTube

def clean_title(title):
    """Nettoie un titre en remplaçant les caractères non alphabétiques par des tirets '-'."""
    if title:
        title = re.sub(r'[^a-zA-Z0-9\s]', '-', title)
        title = re.sub(r'\s+', '-', title)  # Remplacer les espaces par des tirets
    else:
        title = "Sans_Nom"
    return title

def download_video(video_url, download_path):
    """Télécharge une vidéo YouTube."""
    try:
        video = YouTube(video_url, on_progress_callback=on_progress)
        print(f'Téléchargement en cours : {video.title}')
        video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(download_path)
                    
        #video.streams.get_highest_resolution().download(download_path)
        print(f'Vidéo téléchargée : {video.title}')
    except KeyError as e:
        print(f"Impossible d'accéder aux détails de la vidéo : {video_url}. Erreur : {e}")
    except PytubeError as e:
        print(f"Erreur Pytube lors du téléchargement de {video_url}. Détails : {e}")
    except Exception as e:
        print(f"Erreur inattendue lors du téléchargement de {video_url}. Détails : {e}")

def download_playlist(playlist_url):
    """Télécharge toutes les vidéos d'une playlist YouTube."""
    try:
        # Créer l'objet Playlist
        playlist = Playlist(playlist_url)

        # Nettoyer le titre de la playlist
        playlist_title = clean_title(playlist.title)

        # Créer le chemin de téléchargement
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", playlist_title)

        # Vérifier si le dossier existe, sinon le créer
        os.makedirs(download_path, exist_ok=True)

        print(f'Téléchargement de la playlist : {playlist_title}')

        # Parcourir et télécharger chaque vidéo de la playlist
        for video_url in playlist.video_urls:
            download_video(video_url, download_path)

        print('Téléchargement terminé.')
    except Exception as e:
        print(f"Erreur inattendue lors de la création de la playlist. Détails : {e}")

def main():
    """Point d'entrée principal de l'application CLI."""
    parser = argparse.ArgumentParser(description="Téléchargez des vidéos ou playlists depuis YouTube.")
    parser.add_argument("url", type=str, help="URL de la vidéo ou de la playlist YouTube")
    
    args = parser.parse_args()

    # Vérifier si l'URL correspond à une playlist ou une simple vidéo
    if "list=" in args.url:
        download_playlist(args.url)
    else:
        # Nettoyer le titre pour une vidéo simple
        video = YouTube(args.url)
        video_title = clean_title(video.title)
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", video_title)
        os.makedirs(download_path, exist_ok=True)
        download_video(args.url, download_path)

if __name__ == "__main__":
    main()
