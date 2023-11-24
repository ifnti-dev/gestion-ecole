import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

basic_path = os.getcwd()
source_path = f'{basic_path}/media/pdf/maquette'
destination_path = f'{basic_path}/projet_ifnti/static/assets/pdf/maquette'

def create_symbolique_link(source, destination):
    # Verifier si le répertoire de destination existe
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Créer des liens symboliques pour chaque fichier dans le répertoire source
    for filename in os.listdir(source):
        source_path = os.path.join(source, filename)
        destination_path = os.path.join(destination, filename)
        
        if not os.path.exists(destination_path):
            os.symlink(source_path, destination_path)
            print(f"Le lien symbolique pour {filename} a été créé.")
        else:
            print(f"Le lien symbolique pour {filename} existe déjà.")

# print(source_path)
# print(destination_path)
create_symbolique_link(source_path, destination_path)

# class SymbolicLinkUpdater(FileSystemEventHandler):
#     def on_modified(self, event):
#         if event.src_path == target_path:
#             os.remove(link_path)
#             os.symlink(target_path, link_path)
#             print("Symbolic link updated")

# if __name__ == "__main__":
#     event_handler = SymbolicLinkUpdater()
#     observer = Observer()
#     observer.schedule(event_handler, path=target_path, recursive=False)
#     observer.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()

#     observer.join()


