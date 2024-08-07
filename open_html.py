import webbrowser
import os

html_file_path = os.path.abspath("frontend/index.html")
webbrowser.open(f"file://{html_file_path}")
