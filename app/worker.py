import pickle

def print_title(title_path):
    with open(title_path, 'rb') as f:
        title = pickle.load(f)
    print(f'title in print_title: {title}')