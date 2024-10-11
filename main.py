import subprocess
from os import path
import shutil

import os

from XF import XenonFile
from album_task import AlbumTask

working_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_dir)

permak_file_id = "SOSTALG.S0"
xenon_file_id = 'XE'

# tagret_dir
target_dir = path.join('B34', 'K07')
target_dir_abspath = os.path.join(working_dir, target_dir)

copy_patterns = {
    '040': ('2', '3', '1'),
    '300': ('5', '6', '4'),
    '600': ('8', '9', '7'),
}


def copy():
    print(f"Используется каталог поиска {target_dir_abspath}")
    if not os.path.exists(target_dir_abspath):
        print(f"Каталог поиска не найден")
        return

    xenon_raw_files = [ f for f in os.scandir(os.path.join(working_dir, target_dir)) if f.is_file() and f.name.startswith(xenon_file_id) and len(f.name) == 9 ]
    permak_files = [ f for f in os.scandir(os.path.join(working_dir, target_dir)) if f.is_file() and f.name.startswith(permak_file_id) ]

    xenon_files: list[XenonFile] = []
    for file in xenon_raw_files:
        xenon_files.append(XenonFile(file))

    if (len(xenon_files) == 0):
        print(f"Не найдено файлов соответствующих формату файла ксенона")
        return

    print("Найдены файлы XE:")
    for xe_file in xenon_files:
        print(f"\t{xe_file.DirEntry.name}")
    

    perform_copy(xenon_files, permak_files)


def fast_copy_bulk(xenon_file: XenonFile, permak_files: list[os.DirEntry], copy_pattern) -> set[str]:
    copies_count, state = get_copies_count_states(xenon_file)
    written_files: set[str] = set()

    copy_list: list[str] = []

    ## Для первых трех файлов
    for i in range(0, len(copy_pattern)):
        src_filename = ''.join((permak_file_id, copy_pattern[i]))
        src_file = find_dir_entry_by_name(permak_files, src_filename)

        dest_filepath = '.'.join((xenon_file.DirEntry.path, f'S{(i + 1):02d}'))
            
        src = os.path.join(working_dir, src_file.path)
        dest = os.path.join(working_dir, dest_filepath)

        copy_list.append(f'copy {src} {dest}')

        written_files.add(dest)

        print(f"Добавлена задача копирования: {src_file.path} -> {dest_filepath}")

    print('...')
    # для остальных
    for i in range(len(copy_pattern), copies_count):
        dest_filepath = '.'.join((xenon_file.DirEntry.path, f'S{(i + 1):02d}'))
        
        src = os.path.join(working_dir, src_file.path)
        dest = os.path.join(working_dir, dest_filepath)

        copy_list.append(f'copy {src} {dest}')

        written_files.add(dest)

    print(f"Добавлена задача копирования: {src_file.path} -> {dest_filepath}")

    copy_task = '\n'.join(copy_list)

    
    copy_task_path = os.path.join(working_dir, os.path.join(xenon_file.directory, 'copy.bat'))
    print(f'Создан скрипт копирования {copy_task_path}')
    with open(copy_task_path, 'w') as f:
        f.write(copy_task)

    command = [copy_task_path]
    try:
        print("Запуск скрипта копирования")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
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

def perform_copy(xenon_files: list[XenonFile], permak_files: list[os.DirEntry]):
    for xenon_file in xenon_files:
        print()
        print(f"Выполняется копирование для файла {xenon_file.file_name}")

        copy_pattern = copy_patterns.get(xenon_file.time)
        if copy_pattern == None:
            raise Exception(F"Не найден шаблон для заданного параметра Time. Файл: {xenon_file.file_name}.")

        copies_count, state = get_copies_count_states(xenon_file)
        
        written_files: set[str] = fast_copy_bulk(xenon_file, permak_files, copy_pattern)
        
        new_dir = os.path.join(working_dir, xenon_file.DirEntry.path + "_dir")
        
        album_task_str = AlbumTask.get_task_text(xenon_file, copies_count, state, new_dir)
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
            result = subprocess.run(command, capture_output=True, text=True, check=True)
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


def get_copies_count_states(xenon_file: XenonFile) -> tuple[int]:
    errmsg = f"Неверная комбинация S и P. Файл: {xenon_file.file_name}; (P, S) = ({xenon_file.power}, {xenon_file.shut_down})"

    count = -1
    state = -1

    if xenon_file.power == '40':
        if xenon_file.shut_down == '05':
            count = 387
            state = 87
        elif xenon_file.shut_down == '60':
            count = 717
            state = 414
    elif xenon_file.power == '01':
        if xenon_file.shut_down == '60':
            count = 747
            state = 447
    
    if count == -1 or state == -1:
        raise Exception(errmsg)
    
    return count, state



def find_dir_entry_by_name(entries, target_name):
    # Search for the instance with the specified name
    result = [entry for entry in entries if entry.name == target_name]
    return result[0] if result else None



def main():
    copy()


if __name__ == '__main__':
    main()