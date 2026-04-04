from app import app
import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Ouvre le navigateur dans un thread séparé
    threading.Timer(1.0, open_browser).start()
    app.run()
