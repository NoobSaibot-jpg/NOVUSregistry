import PyInstaller.__main__
import os
import sys
import time

# Путь к иконке
icon_path = os.path.join('icon.ico')

# Путь к выходному файлу
output_path = os.path.join('dist', 'NOVUS.exe')

# Удаляем старый exe-файл, если он существует
if os.path.exists(output_path):
    try:
        os.remove(output_path)
        # Даем системе время на освобождение файла
        time.sleep(1)
    except PermissionError:
        print("Ошибка: Не удалось удалить старый файл. Возможно, он запущен.")
        print("Пожалуйста, закройте приложение и попробуйте снова.")
        sys.exit(1)

# Параметры для PyInstaller
params = [
    'main.py',  # Основной файл
    '--name=NOVUS',  # Имя приложения
    f'--icon={icon_path}',  # Путь к иконке
    '--noconsole',  # Не показывать консоль
    '--add-data=static;static',  # Добавить статические файлы
    '--add-data=config.ini;.',  # Добавить конфигурационный файл
    '--add-data=bases;bases',  # Добавить базу данных
    '--hidden-import=hypercorn',  # Добавляем hypercorn
    '--hidden-import=hypercorn.asyncio',  # Добавляем асинхронный модуль hypercorn
    '--onefile',  # Собрать в один файл
]

# Запуск сборки
PyInstaller.__main__.run(params) 