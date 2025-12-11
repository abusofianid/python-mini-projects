import qrcode
import os

# Data yang ingin dimasukkan (bisa berupa Link URL atau Teks)
data = input("Input link or text: ")

# Membuat QR Code
img = qrcode.make(data)

# Mengecek nama file yang sudah ada untuk menghindari overwrite
counter = 1
while os.path.exists(os.path.join(os.path.dirname(__file__), f"qrcode_{counter}.png")):
    counter += 1

# Menyimpan gambar
nama_file = os.path.join(os.path.dirname(__file__), f"qrcode_{counter}.png")
img.save(nama_file)
print(f"QR Code success created and saved as {nama_file}")
