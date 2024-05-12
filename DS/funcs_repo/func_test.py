import cv2
from matplotlib import pyplot as plt

from funcs_repo import recognize_license_plate
# Завантаження фотографії
image_path = "DS/img/аі8702ом.jpg"
image = cv2.imread(image_path)

# Виклик функції recognize_license_plate
plate_img, recognized_plate = recognize_license_plate(image)

# Відображення результатів
plt.imshow(cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB))
plt.title("Результат виявлення номерного знаку")
plt.axis('off')
plt.show()

if recognized_plate is not None:
    print("Розпізнаний номерний знак:", recognized_plate)
else:
    print("Номерний знак не був розпізнаний.")
