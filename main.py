import subprocess
from os import path
import shutil

import os
import sys

from XF import XenonFile, XenonFileSimple
from album_task import AlbumTask
from file_loader import KeyValueFileParser, XenonFileParser

# set in main
working_dir = ''

xe_list_file_name = "conf_XeList.txt"
conf_file_name = "conf_Settings.txt"
conf_data = {}

permak_file_id = "SOSTALG.S0"
xenon_file_id = 'XE'

target_dir = ''
target_dir_abspath = ''

copy_patterns = {
    40: ('2', '3', '1'),
    300: ('5', '6', '4'),
    600: ('8', '9', '7'),
}


def copy():
    print(f"Используется каталог поиска {target_dir_abspath}")
    if not os.path.exists(target_dir_abspath):
        print(f"Каталог поиска не найден")
        return

    FILE_DIR = os.path.join(working_dir, target_dir)

    xenon_raw_files = [ f for f in os.scandir(FILE_DIR) if f.is_file() and f.name.startswith(xenon_file_id) and len(f.name) == 9 ]
    permak_files = [ f for f in os.scandir(FILE_DIR) if f.is_file() and f.name.startswith(permak_file_id) ]

    xe_file_list_parser = XenonFileParser(os.path.join(working_dir, xe_list_file_name))
    xenon_simple_list: list[XenonFileSimple] = xe_file_list_parser.parse_file()
    xenon_simple_list_processed: list[XenonFileSimple] = []

    for xe_file in xenon_simple_list:
        file_path = os.path.join(FILE_DIR, xe_file.file_name)
        if not os.path.exists(file_path):
            print(f"Указанный файл ксенона не найден: {file_path}")
            continue
        xenon_simple_list_processed.append(XenonFileSimple(file_path, xe_file.MoC, xe_file.state, xe_file.count))

    if (len(xenon_simple_list_processed) == 0):
        print(f"Не найдено файлов соответствующих формату файла ксенона")
        return

    print("Найдены файлы ксенона:")
    for xe_file in xenon_simple_list_processed:
        print(f"\t{xe_file.file_name}")
    

    perform_copy(xenon_simple_list_processed, permak_files)


def fast_copy_bulk(xenon_file: XenonFileSimple, permak_files: list[os.DirEntry], copy_pattern) -> set[str]:
    #  get_copies_count_states(xenon_file)

    copies_count, state = (xenon_file.count, xenon_file.state)
    written_files: set[str] = set()

    copy_list: list[str] = []
    copy_list.append("@echo off")

    ## Для первых трех файлов
    for i in range(0, len(copy_pattern)):
        src_filename = ''.join((permak_file_id, copy_pattern[i]))
        src_file = find_dir_entry_by_name(permak_files, src_filename)
        if src_file == None:
            raise FileNotFoundError(f'Не найден файл {src_filename}')

        dest_filepath = '.'.join((xenon_file.file_name, f'S{(i + 1):02d}'))
            
        src = os.path.join(working_dir, src_file.path)
        dest = os.path.join(working_dir, dest_filepath)

        copy_list.append(f'copy {src} {dest}')

        written_files.add(dest)

        print(f"Добавлена задача копирования: {src_file.path} -> {dest_filepath}")

    print('...')
    # для остальных
    for i in range(len(copy_pattern), copies_count):
        dest_filepath = '.'.join((xenon_file.file_name, f'S{(i + 1):02d}'))
        
        src = os.path.join(working_dir, src_file.path)
        dest = os.path.join(working_dir, dest_filepath)

        copy_list.append(f'copy {src} {dest}')

        written_files.add(dest)

    print(f"Добавлена задача копирования: {src_file.path} -> {dest_filepath}")

    copy_task = '\n'.join(copy_list)
    
    copy_task_path = os.path.join(working_dir, os.path.join(working_dir, 'copy.bat'))
    print(f'Создан скрипт копирования {copy_task_path}')
    with open(copy_task_path, 'w') as f:
        f.write(copy_task)

    command = [copy_task_path]
    try:
        print("Запуск скрипта копирования")
        result = subprocess.run(command, capture_output=False, stdout=subprocess.DEVNULL)
        print("Вывод:")
        print(result.stdout)  # Standard output
        print('---')

    except subprocess.CalledProcessError as e:
        print("Ошибка:")
        print(e.stderr)  # Standard error output

    except OSError:
        print("Запуск пропущен")
    
    finally:
        os.remove(copy_task_path)
        print('Работа скрипта завершена, файл скрипта удален')

    return written_files

def perform_copy(xenon_files: list[XenonFileSimple], permak_files: list[os.DirEntry]):
    for xenon_file in xenon_files:
        print()
        print(f"Выполняется копирование для файла {xenon_file.file_name}")

        copy_pattern = copy_patterns.get(xenon_file.MoC)
        if copy_pattern == None:
            raise Exception(F"Не найден шаблон для заданного параметра MoC = {xenon_file.MoC}. Файл: {xenon_file.file_name}.")

        # copies_count, state = get_copies_count_states(xenon_file)
        copies_count, state = (xenon_file.count, xenon_file.state)
        
        written_files: set[str] = fast_copy_bulk(xenon_file, permak_files, copy_pattern)
        
        new_dir = os.path.join(working_dir, xenon_file.file_name + "_dir")
        
        album_task_str = AlbumTask.get_task_text(xenon_file, copies_count, state, new_dir, conf_data.get('Camp'))
        album_task_path = os.path.join(working_dir, os.path.join(xenon_file.directory, 'man.dat'))

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)

        with open(album_task_path, 'w') as f:
            f.write(album_task_str)
        print(f'Создан файл задачи альбома {album_task_path}')

        alb_bat_filename = "alb.bat"
        
        command = [os.path.join(os.path.abspath(xenon_file.directory), alb_bat_filename), album_task_path, '-m']

        try:
            print("Запуск альбома")
            result = subprocess.run(command, capture_output=False)
            print("Вывод:")
            print(result.stdout)  # Standard output
            print('---')

        except subprocess.CalledProcessError as e:
            print("Ошибка при выполнении:")
            print(e.stderr)  # Standard error output

        except OSError:
            print("Запуск альбома пропущен")
        
        finally:
            pass
            # os.remove(album_task_path)
            # print('Файл задачи альбома удален')
        
        
        removed_counter = 0
        for written_file in written_files:
            if (path.exists(written_file)):
                os.remove(written_file)
                removed_counter += 1
        
        print(f"Файлов удалено: {removed_counter}")

        pass


def find_dir_entry_by_name(entries, target_name):
    # Search for the instance with the specified name
    result = [entry for entry in entries if entry.name == target_name]
    return result[0] if result else None


def get_configurations():
    conf_File_parser = KeyValueFileParser(os.path.join(working_dir, conf_file_name))
    global conf_data
    conf_data = conf_File_parser.parse_file()

    global target_dir
    global target_dir_abspath
    target_dir = os.path.join(conf_data.get('Unit'), conf_data.get('Camp'))
    target_dir_abspath = os.path.join(working_dir, target_dir)


def get_current_directory():
    if getattr(sys, 'frozen', False):
        # If the program is running as an executable
        return os.path.dirname(sys.executable)
    else:
        # If the program is running as a script
        return os.path.dirname(os.path.abspath(__file__))


def main():
    global working_dir
    working_dir = get_current_directory()

    try:
        get_configurations()
    except FileNotFoundError as ex:
        print(ex)
        return
    
    except KeyError as ex:
        print(ex)
        return
    
    copy()


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)
        raise ex
    finally:
        pass
        print("Нажмите ENTER чтобы закрыть")
        input()

    