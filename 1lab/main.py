import subprocess
import sys
import os


def main():
    # Устанавливаем рабочую директорию как 1lab
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Запускаем сервер в отдельном процессе
    server_process = subprocess.Popen([sys.executable, "server.py"])

    # Запускаем графический клиент (или консольный, если нужно)
    client_process = subprocess.Popen([sys.executable, "client_gui.py"])

    # Ждем завершения процессов (можно убрать, если не нужно ждать)
    server_process.wait()
    client_process.wait()


if __name__ == "__main__":
    main()
