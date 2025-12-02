import json
import os
from config import file_name


# fungsi untuk memuat data dari file JSON
def load_data():

    # cek apakah file ada
    if not os.path.exists(file_name):
        return []  # jika file tidak ada, kembalikan list kosong
    try:
        # buka file dalam mode 'r' (read)
        with open(file_name, 'r') as file:
            content = file.read()
            # jika file ada isinya, ubah dari string JSON ke list python
            # jika file kosong, kembalikan list kosong
            return json.loads(content) if content else []
    except (json.JSONDecoderError, IOError):
        # jika file rusak atau error saat membaca, kembalikan list kosong agar program tetap berjalan
        return []


# fungsi untuk menyimpan data ke file JSON
def save_data(data):
    try:
        # buka file dalam mode 'w' (write)
        with open(file_name, 'w') as file:
            # ubah data dari list python ke string JSON dan tulis ke file
            # indent=4 untuk format yang lebih rapi
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"error saving data: {e}")
