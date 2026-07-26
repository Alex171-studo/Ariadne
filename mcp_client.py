import os 
from pathlib import Path
from config import TARGET_PROJECT_DIR

class FileSystemMCP:
    
    def __init__(self, target_dir:str=TARGET_PROJECT_DIR):
        self.target_dir = target_dir

        if not os.path.exists(self.target_dir):
            raise FileNotFoundError(f"Le dossier {self.target_dir} n'existe pas")

    
    def get_tree(self) -> str:
        results = []
        ignored = {".git", "__pycache__", ".venv", ".env", "node_modules"}

        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in ignored]

            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, self.target_dir)
                results.append(relative_path)

        return "\n".join(results)

    def get_file_content(self, file_path:str) -> str:

        target_base = Path(self.target_dir).resolve()
        requested_path = (target_base / file_path).resolve()

        if not str(requested_path).startswith(str(target_base)):
            raise PermissionError("Accès refusé : Tentative d'accès hors du dossier cible.")

        if not requested_path.is_file():
            raise FileNotFoundError(f"Fichier non trouvé : {file_path}")

        try:
            return requested_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "[Erreur : Impossible de lire ce fichier (format binaire ou non-textuel)]"

