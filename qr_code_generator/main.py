import qrcode
import os

# The data to put into the QR code (can be a URL link or text)
data = input("Input link or text: ")

# Create the QR code
img = qrcode.make(data)

# Check for existing file names to avoid overwriting
counter = 1
while os.path.exists(os.path.join(os.path.dirname(__file__), f"qrcode_{counter}.png")):
    counter += 1

# Save the image
nama_file = os.path.join(os.path.dirname(__file__), f"qrcode_{counter}.png")
img.save(nama_file)
print(f"QR Code success created and saved as {nama_file}")
