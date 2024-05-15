import cv2
import os
import asyncio
from image_process_async import plate_recognize

async def main():
    # Отримання списку файлів у каталозі DS/img/
    img_dir = 'DS/img/'
    img_files = os.listdir(img_dir)

    # Створення каталогу для збереження розпізнаних знаків
    results_dir = 'DS/results/'
    os.makedirs(results_dir, exist_ok=True)

    # Створення каталогу для збереження нерозпізнаних знаків
    unrecognized_dir = 'DS/unrecognized/'
    os.makedirs(unrecognized_dir, exist_ok=True)

    # Проходження по кожному файлу у каталозі
    for img_file in img_files:
        # Повний шлях до поточного файлу
        img_path = os.path.join(img_dir, img_file)
        
        # Виклик функції plate_recognize() для розпізнавання номерного знаку
        result_img, recognized_symbols = await plate_recognize(img_path)
        
        # Якщо номерний знак був розпізнаний, зберегти результат
        if recognized_symbols:
            # Шлях для збереження результату
            result_filename = os.path.join(results_dir, f"{recognized_symbols}.jpg")
            cv2.imwrite(result_filename, result_img)
            print(f"Результат для файлу {img_file} був збережений у {result_filename}")
        else:
            # Якщо номерний знак не був розпізнаний, зберегти його у каталозі DS/unrecognized/
            unrecognized_filename = os.path.join(unrecognized_dir, img_file)
            cv2.imwrite(unrecognized_filename, result_img)
            print(f"Нерозпізнаний знак у файлі {img_file} був збережений у {unrecognized_filename}")

# Запуск асинхронної функції main()
asyncio.run(main())