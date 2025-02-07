import os
from itertools import islice


def batched(lst, batch_size):
    it = iter(lst)
    return iter(lambda: list(islice(it, batch_size)), [])


def save_uploaded_file(uploaded_file):
    data_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, uploaded_file.name)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    return file_path