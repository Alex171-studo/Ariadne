import os 
from pathlib import Path
from config import TARGET_PROJECT_DIR
import re
class FileSystemMCP:
    
    def __init__(self, target_dir:str=TARGET_PROJECT_DIR):
        self.target_dir = os.path.abspath(target_dir)
        self.forbidden_files = {".git", ".env", ".pem", ".id_rsa", ".key"}

    def _is_safe(self, relative_path:str) -> tuple[bool, str]:

        if not relative_path:
            return False, "Aucun chemin fourni"

        target_path = os.path.abspath(os.path.join(self.target_dir, relative_path))

        if not target_path.startswith(self.target_dir):
            return False, "⚠️ REFUS DE SÉCURITÉ : Tentative d'accès hors du répertoire autorisé (Path Traversal détecté)."

        filename = os.path.basename(target_path)
        if filename in self.forbidden_files or filename.startswith(".env"):
            return False, f"⚠️ REFUS DE SÉCURITÉ : Le fichier '{filename}' est protégé et ne peut pas être lu."
        
        if not os.path.exists(target_path):
            return False, f"Fichier introuvable : '{relative_path}'."

        return True, target_path

    def _sanitize_content(self, text: str) -> str:
        suspicious_patterns = [
            r"(?i)ignore\s+previous\s+instructions",
            r"(?i)system\s*:",
            r"(?i)you\s+are\s+now\s+a",
        ]
        sanitized = text
        for pattern in suspicious_patterns:
            sanitized = re.sub(pattern, "[CONTENU_NEUTRALISE_PAR_SECURITE]", sanitized)
        return sanitized
    
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

        is_safe,result = self._is_safe(file_path)
        if not is_safe:
            return result
        
        try:
            with open(result,"r", encoding="utf-8") as f:
                content = f.read()
                return self._sanitize_content(content)
        except UnicodeDecodeError:
            return "[Erreur : Impossible de lire ce fichier (format binaire ou non-textuel)]"

