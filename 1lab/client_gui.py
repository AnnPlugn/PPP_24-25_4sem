import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox


class ClientGUI:
    def __init__(self, root):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 5555))

        self.root = root
        self.root.title("Клиент директорий")

        # Поле ввода пути
        self.path_label = tk.Label(root, text="Введите путь:")
        self.path_label.pack()
        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.pack()

        # Кнопки
        self.set_dir_button = tk.Button(root, text="Установить директорию", command=self.set_directory)
        self.set_dir_button.pack()
        self.get_dir_button = tk.Button(root, text="Получить структуру", command=self.get_structure)
        self.get_dir_button.pack()

        # Дерево
        self.tree = ttk.Treeview(root, height=20)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_directory(self):
        path = self.path_entry.get()
        self.client.send(f"SET_DIR:{path}".encode('utf-8'))
        response = self.client.recv(1024).decode('utf-8')
        messagebox.showinfo("Ответ сервера", response)

    def get_structure(self):
        try:
            # Отправляем запрос
            self.client.send("GET_STRUCTURE".encode('utf-8'))

            # Получаем размер файла
            file_size_data = self.client.recv(1024).decode('utf-8')
            if not file_size_data:
                messagebox.showerror("Ошибка", "Сервер не отправил размер файла")
                return
            file_size = int(file_size_data)
            self.client.send("OK".encode('utf-8'))  # Подтверждение серверу

            # Получаем файл
            with open('received_structure.json', 'wb') as f:
                bytes_received = 0
                while bytes_received < file_size:
                    data = self.client.recv(min(1024, file_size - bytes_received))
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)

            # Читаем и отображаем структуру
            with open('received_structure.json', 'r', encoding='utf-8') as f:
                structure = json.load(f)

            self.tree.delete(*self.tree.get_children())
            self.populate_tree('', structure)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить структуру: {str(e)}")

    def populate_tree(self, parent, data):
        for key, value in data.items():
            if key not in ['files', 'dirs']:
                node = self.tree.insert(parent, 'end', text=f"📁 {key}", open=False)
                self.populate_tree(node, value)
            elif key == 'files':
                for file in value:
                    self.tree.insert(parent, 'end', text=f"📄 {file}")

    def on_closing(self):
        self.client.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
