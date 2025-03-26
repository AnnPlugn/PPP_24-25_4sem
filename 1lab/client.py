import socket
import json


def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5555))
    return client


def display_structure(data, indent=0):
    for key, value in data.items():
        if key not in ['files', 'dirs']:
            print('  ' * indent + f"📁 {key}")
            display_structure(value, indent + 1)
        elif key == 'files':
            for file in value:
                print('  ' * indent + f"📄 {file}")


def main():
    client = connect_to_server()
    print("Подключено к серверу. Доступные команды:")
    print("1. SET_DIR <путь> — установить новую корневую директорию")
    print("2. GET — получить структуру директории")
    print("3. EXIT — выйти")

    while True:
        command = input("> ").strip()

        if command.startswith("SET_DIR "):
            client.send(f"SET_DIR:{command[8:]}".encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(response)

        elif command == "GET":
            print("Отправляем запрос GET_STRUCTURE")  # Отладка
            client.send("GET_STRUCTURE".encode('utf-8'))
            print("Ожидаем размер файла")  # Отладка
            file_size_data = client.recv(1024).decode('utf-8')
            if not file_size_data:
                print("Ошибка: сервер не отправил размер файла")
                continue
            file_size = int(file_size_data)
            print(f"Получен размер файла: {file_size}")  # Отладка
            client.send("OK".encode('utf-8'))

            with open('received_structure.json', 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    data = client.recv(min(1024, file_size - bytes_received))
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)

            with open('received_structure.json', 'r', encoding='utf-8') as f:
                structure = json.load(f)
            print("Структура директории:")
            display_structure(structure)

        elif command == "EXIT":
            client.close()
            print("Отключено от сервера")
            break

        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()
