# tree.py
import os

def print_tree(start_path, prefix=''):
    files = os.listdir(start_path)
    files.sort()
    for index, name in enumerate(files):
        path = os.path.join(start_path, name)
        connector = '└── ' if index == len(files) - 1 else '├── '
        print(prefix + connector + name)
        if os.path.isdir(path):
            extension = '    ' if index == len(files) - 1 else '│   '
            print_tree(path, prefix + extension)

if __name__ == '__main__':
    print_tree('.')  # hoặc './your_app' nếu muốn xem 1 app cụ thể

