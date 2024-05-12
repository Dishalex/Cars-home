import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from keras.models import load_model

CASCADE_ClASIFIER = 'DS/models/haarcascade_ua_license_plate.xml'
MODEL = 'DS/models/model.keras'


model = load_model(MODEL, compile=False)
plate_cascade = cv2.CascadeClassifier(CASCADE_ClASIFIER)



def detect_plate(img, text=''): 
    """
    Функція призначена для виявлення та обробки номерних знаків на зображенні.
    
    Параметри:
    img (numpy.array): Зображення, на якому потрібно виявити та обробити номерні знаки.
    text (str, optional): Текст, який можна додати на зображення навколо номерного знаку.
    
    Повертає:
    numpy.array: Зображення з виділеними номерними знаками та, за бажанням, доданим текстом.
    numpy.array or None: Зображення області номерного знаку для подальшої обробки або None, якщо номерний знак не був виявлений.
    """
    plate_img = img.copy()  # Копіюємо вхідне зображення для обробки
    roi = img.copy()  # Копіюємо вхідне зображення для виділення області номерного знаку
    
    # Виявлення номерних знаків на зображенні
    plate_rect = plate_cascade.detectMultiScale(plate_img, scaleFactor=1.15, minNeighbors=14)
    
    # Ініціалізуємо змінну plate перед використанням
    plate = None
    
    # Обробка кожного виявленого номерного знаку
    for (x, y, w, h) in plate_rect:
        # Витягаємо область номерного знаку для подальшої обробки
        roi_ = roi[y:y+h, x:x+w, :]
        plate = roi[y:y+h, x:x+w, :]
        
        # Малюємо прямокутник навколо номерного знаку на вихідному зображенні
        cv2.rectangle(plate_img, (x-10, y), (x+w+10, y+h-3), (51, 181, 155), 3)
    
    # Перетворюємо зображення номерного знаку на відтінки сірого
    if plate is not None:
        plate = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    
    # Додавання тексту (якщо вказано)
    if text != '':
        plate_img = cv2.putText(plate_img, text, (x-w//2, y-h//2),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (51, 181, 155), 1, cv2.LINE_AA)
    
    # Повертаємо оброблене зображення з виділеними номерними знаками та область номерного знаку
    return plate_img, plate if plate is not None else None




def find_contours(dimensions, img):
    """
    Функція призначена для знаходження контурів символів на зображенні номерного знака.
    
    Параметри:
        dimensions (list): Список, що містить набір розмірів контурів символів. Потрібно задати 
                           lower_width, upper_width, lower_height та upper_height.
        img (numpy.ndarray): Вхідне зображення, на якому потрібно знайти контури символів.
        
    Повертає:
        numpy.ndarray: Масив, що містить зображення контурів символів, відсортованих за координатою x.
    """
    # Find all contours in the image
    cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Retrieve potential dimensions
    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    # Check largest 15 contours for characters
    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    x_cntr_list = []
    target_contours = []
    img_res = []
    for cntr in cntrs:
        # Detect contour in binary image and return the coordinates of rectangle enclosing it
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # Check the dimensions of the contour to filter out the characters by contour's size
        if intWidth > lower_width and intWidth < upper_width and intHeight > lower_height and intHeight < upper_height:
            x_cntr_list.append(intX)  # Store the x coordinate of the character's contour, to be used later for indexing the contours

            char_copy = np.zeros((44, 24))
            # Extract each character using the enclosing rectangle's coordinates
            char = img[intY:intY+intHeight, intX:intX+intWidth]
            char = cv2.resize(char, (20, 40))

            # Make result formatted for classification: invert colors
            char = cv2.subtract(255, char)

            # Resize the image to 24x44 with black border
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0

            img_res.append(char_copy)  # List that stores the character's binary image (unsorted)

    # Return characters on ascending order with respect to the x-coordinate (most-left character first)
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        img_res_copy.append(img_res[idx])  # Store character images according to their index
    img_res = np.array(img_res_copy)

    return img_res


def segment_characters(image):
    """
    Знаходить символи на зображенні номерного знака.

    Параметри:
     - image: Зображення номерного знака, з якого будуть вилучені символи.

    Повертає:
     - char_list: Список контурів символів, знайдених на зображенні.
    """
    # Попередньо оброблюємо обрізане сіре зображення номерного знака
    img_lp = cv2.resize(image, (333, 75))
    _, img_binary_lp = cv2.threshold(img_lp, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_binary_lp = cv2.erode(img_binary_lp, (3,3))
    img_binary_lp = cv2.dilate(img_binary_lp, (3,3))

    LP_WIDTH = img_binary_lp.shape[0]
    LP_HEIGHT = img_binary_lp.shape[1]

    # Робимо межі білими
    img_binary_lp[0:3,:] = 255
    img_binary_lp[:,0:3] = 255
    img_binary_lp[72:75,:] = 255
    img_binary_lp[:,330:333] = 255

    # Приблизні розміри контурів символів обрізаного номерного знака
    dimensions = [LP_WIDTH/6,
                   LP_WIDTH/2,
                   LP_HEIGHT/10,
                   2*LP_HEIGHT/3]

    # Візуалізуємо оброблене зображення
    plt.imshow(img_binary_lp, cmap='gray')
    plt.show()
    cv2.imwrite('contour.jpg', img_binary_lp)

    # Отримуємо контури на обрізаному номерному знаку
    char_list = find_contours(dimensions, img_binary_lp)

    return char_list



def fix_dimension(img):
    """
    Функція для вирівнювання розмірів зображення до розмірів (28, 28, 3).

    Параметри:
    img (numpy.ndarray): Вхідне зображення з розмірами (n, m), де n та m - цілі числа.

    Повертає:
    numpy.ndarray: Зображення з розмірами (28, 28, 3), де 3 - кількість каналів (RGB).
    """
    new_img = np.zeros((28,28,3))
    for i in range(3):
        new_img[:,:,i] = img
    return new_img


def show_results(char):
    """
    Функція для показу результатів розпізнавання символів на номерному знаку.

    Параметри:
    char (list): Список зображень символів номерного знаку.

    Повертає:
    str: Рядок, що містить розпізнану номерну знаку, складену з окремих символів.
    """
    dic = {}
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, c in enumerate(characters):
        dic[i] = c

    output = []
    for i, ch in enumerate(char): # ітеруємося по символах
        img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
        img = fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3) # підготовка зображення для моделі
        y_proba = model.predict(img, verbose=0)[0] # отримуємо ймовірності для кожного класу
        y_ = np.argmax(y_proba) # вибираємо клас з найвищою ймовірністю
        character = dic[y_] # отримуємо символ, відповідний прогнозованому класу
        output.append(character) # зберігаємо результат у списку

    plate_number = ''.join(output) # об'єднуємо всі символи у рядок

    return plate_number


def recognize_license_plate(image):
    """
    Розпізнає номерний знак на зображенні автомобіля.

    Параметри:
     - image: Зображення автомобіля з номерним знаком.

    Повертає:
     - plate_img: Зображення з виділеними рамками номерного знаку та розпізнаними символами.
     - recognized_plate: Розпізнаний номерний знак.
    """
    # Виявлення номерного знаку на зображенні
    plate_img, plate = detect_plate(image)

    # Перевірка, чи був виявлений номерний знак
    if plate is not None:
        # Знаходження символів на зображенні номерного знаку
        characters = segment_characters(plate)

        # Розпізнавання символів та отримання номерного знаку
        recognized_plate = show_results(characters)
    else:
        recognized_plate = "Number plate not detected"

    return plate_img, recognized_plate


