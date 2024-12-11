import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QListWidget, QProgressBar, QHBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QScreen
from pytube import Playlist
from pytube.exceptions import PytubeError
from pytubefix import YouTube
from pytubefix.cli import on_progress

# Classe pour le téléchargement en arrière-plan
class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    
    def __init__(self, playlist_url, download_path):
        super().__init__()
        self.playlist_url = playlist_url
        self.download_path = download_path

    def run(self):
        try:
            playlist = Playlist(self.playlist_url)
            playlist_title = re.sub(r'[^a-zA-Z0-9\s]', '-', playlist.title or "Playlist_Sans_Nom")
            playlist_title = re.sub(r'\s+', '-', playlist_title)
            full_download_path = os.path.join(self.download_path, playlist_title)
            os.makedirs(full_download_path, exist_ok=True)

            self.progress_signal.emit(f'Téléchargement de la playlist : {playlist_title}')
            for video_url in playlist.video_urls:
                try:
                    video = YouTube(video_url, on_progress_callback=on_progress)
                    self.progress_signal.emit(f'Téléchargement en cours : {video.title}')
                    video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(full_download_path)
                    #video.streams.get_highest_resolution().download(full_download_path)

                    self.progress_signal.emit(f'Vidéo téléchargée : {video.title}')
                except KeyError as e:
                    self.progress_signal.emit(f"Erreur d'accès aux détails de la vidéo : {video_url}. Erreur : {e}")
                except PytubeError as e:
                    self.progress_signal.emit(f"Erreur Pytube : {video_url}. Détails : {e}")
                except Exception as e:
                    self.progress_signal.emit(f"Erreur inattendue : {video_url}. Détails : {e}")
            
            self.finished_signal.emit('Téléchargement terminé.')
        except Exception as e:
            self.progress_signal.emit(f"Erreur lors de la création de la playlist. Détails : {e}")
            self.finished_signal.emit('Erreur.')

# Initialisation de l'application
app = QApplication([])
window = QWidget()
window.setWindowTitle('Téléchargeur de Playlists YouTube')
window.setStyleSheet("background-color: #f0f0f0; padding: 15px;")

layout = QVBoxLayout()

# Titre de l'application
title_label = QLabel('Téléchargeur de Playlists YouTube')
title_label.setFont(QFont('Arial', 16, QFont.Bold))
layout.addWidget(title_label)

# Champ de saisie avec étiquette et bouton "Coller"
url_layout = QHBoxLayout()
url_entry = QLineEdit()
url_entry.setPlaceholderText("Collez l'URL ici")
url_entry.setStyleSheet("padding: 5px; font-size: 14px;")
url_layout.addWidget(url_entry)

paste_button = QPushButton('Coller')
paste_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px; border-radius: 5px;")
url_layout.addWidget(paste_button)

# Fonction pour coller le texte du presse-papiers dans l'entrée
def paste_url():
    clipboard = QApplication.clipboard()
    url_entry.setText(clipboard.text())

paste_button.clicked.connect(paste_url)

layout.addLayout(url_layout)

# Bouton de téléchargement
download_button = QPushButton('Télécharger')
download_button.setStyleSheet("background-color: #008CBA; color: white; padding: 10px 20px; border-radius: 5px;")
layout.addWidget(download_button)

# Liste des vidéos
list_widget = QListWidget()
list_widget.setStyleSheet("padding: 5px; font-size: 12px;")
layout.addWidget(list_widget)

# Options de téléchargement (qualité et format)
options_layout = QHBoxLayout()
quality_label = QLabel('Qualité:')
quality_label.setFont(QFont('Arial', 12))
options_layout.addWidget(quality_label)

quality_combo = QComboBox()
quality_combo.addItems(['720p', '1080p', '4K'])
options_layout.addWidget(quality_combo)

format_label = QLabel('Format:')
format_label.setFont(QFont('Arial', 12))
options_layout.addWidget(format_label)

format_combo = QComboBox()
format_combo.addItems(['MP4', 'MP3'])
options_layout.addWidget(format_combo)

layout.addLayout(options_layout)

# Barre de progression
progress_bar = QProgressBar()
progress_bar.setStyleSheet("QProgressBar { border: 1px solid grey; border-radius: 5px; }"
                           "QProgressBar::chunk { background-color: #4CAF50; width: 20px; }")
layout.addWidget(progress_bar)

# Affichage de la progression
status_label = QLabel('Statut : En attente...')
status_label.setFont(QFont('Arial', 10))
layout.addWidget(status_label)

# Variable pour le thread
download_thread = None

# Fonction pour démarrer le téléchargement
def start_download():
    global download_thread
    playlist_url = url_entry.text().strip()
    if not playlist_url:
        QMessageBox.warning(window, "Erreur", "Veuillez entrer une URL valide.")
        return

    download_path = "/media/danni/data/Tutoriel"  # Chemin de téléchargement à personnaliser
    download_thread = DownloadThread(playlist_url, download_path)
    
    def update_status(message):
        status_label.setText(message)
        list_widget.addItem(message)
    
    def download_finished(message):
        progress_bar.setValue(100)
        QMessageBox.information(window, "Terminé", message)
    
    download_thread.progress_signal.connect(update_status)
    download_thread.finished_signal.connect(download_finished)
    download_thread.start()

download_button.clicked.connect(start_download)

# Fonction pour arrêter proprement le thread lors de la fermeture de la fenêtre
def close_event(event):
    global download_thread
    if download_thread and download_thread.isRunning():
        download_thread.wait()  # Attendre que le thread se termine
    event.accept()

# Connecter la fermeture de la fenêtre à la fonction de fermeture
window.closeEvent = close_event

# Appliquer le layout
window.setLayout(layout)
window.resize(600, 400)

# Centrer la fenêtre sur l'écran
screen = QScreen.availableGeometry(app.primaryScreen())
x = (screen.width() - window.width()) // 2
y = (screen.height() - window.height()) // 2
window.move(x, y)

window.show()
app.exec_()
