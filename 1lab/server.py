import socket
import os
import json
import threading


def get_directory_structure(root_dir):
    structure = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current = structure
        path_parts = os.path.relpath(dirpath, root_dir).split(os.sep)
        if path_parts[0] == '.':
            path_parts = []

        for part in path_parts:
            if part not in current:
                current[part] = {}
            current = current[part]

        current['files'] = filenames
        current['dirs'] = dirnames

    return {os.path.basename(root_dir) or root_dir: structure}


def save_to_json(data, filename='directory_structure.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filename


def handle_client(client_socket, address):
    print(f"Подключен клиент: {address}")
    current_dir = os.getcwd()

    while True:
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                break

            print(f"Получен запрос: {request}")  # Отладка

            if request.startswith("SET_DIR:"):
                new_dir = request.split("SET_DIR:")[1].strip()
                if os.path.isdir(new_dir):
                    current_dir = new_dir
                    client_socket.send("Директория успешно изменена".encode('utf-8'))
                else:
                    client_socket.send("Ошибка: директория не существует".encode('utf-8'))

            elif request == "GET_STRUCTURE":
                structure = get_directory_structure(current_dir)
                json_file = save_to_json(structure)
                file_size = os.path.getsize(json_file)
                print(f"Отправляем размер файла: {file_size}")  # Отладка
                client_socket.send(str(file_size).encode('utf-8'))
                print(f"Ожидаем подтверждение от клиента")  # Отладка
                client_socket.recv(1024)  # Ждем "OK" от клиента

                with open(json_file, 'rb') as f:
                    client_socket.sendfile(f)
                print(f"Отправлена структура директории клиенту {address}")

        except Exception as e:
            print(f"Ошибка при обработке клиента {address}: {e}")
            break

    client_socket.close()
    print(f"Клиент {address} отключен")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    print("Сервер запущен на localhost:5555")

    while True:
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()


if __name__ == "__main__":
    start_server()