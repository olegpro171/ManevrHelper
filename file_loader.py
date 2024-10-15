import os

from XF import XenonFileSimple

class KeyValueFileParser:
    keywords = {
        "Unit",
        "Camp",
    }

    used_keywords = set()


    def __init__(self, filepath):
        """
        Initializes the class with a file name and a list of optional keywords to filter.
        
        :param file_name: Name of the file to read.
        """
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Не найден файл конфигурации {filepath}")
        
        self.file_name = filepath


    def parse_file(self):
        """
        Reads the file and returns a dictionary of key-value pairs.
        
        :return: Dictionary containing key-value pairs from the file.
        """
        data = {}
        with open(self.file_name, 'r') as file:
            for line in file:
                # Strip whitespace and split by "=" to get key and value
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if not key in self.keywords:
                        raise KeyError(f'Неопознанный ключ в файле конфигурации: {key}')
                    
                    if key in self.used_keywords:
                        raise KeyError(f'Дубликат ключа {key} в файле конфигурации')
                    
                    if value is None or value == '':
                        raise KeyError(f'Не задано значение ключа {key} в файле конфигурации')
                    
                    data[key] = value
                    self.used_keywords.add(key)

        if len(self.used_keywords) != len(self.keywords):
            raise KeyError(f'В файле конфигурации отсутствует определение ключей: {self.keywords - self.used_keywords}')
        
        return data
    


class XenonFileParser:
    file_name: str

    def __init__(self, list_file_name: str):
        """
        :param base_directory: Directory where the files are located
        """

        if not os.path.exists(list_file_name):
            raise FileNotFoundError(f"Не найден файл списка ксеноновых файлов {list_file_name}")
        

        self.file_name = list_file_name


    def parse_file(self):
        """
        Parses the given text file and returns a list of XenonFileSimple objects.
        
        :return: List of XenonFileSimple objects
        """
        xenon_files = []

        with open(self.file_name, 'r') as file:
            line_counter = 0
            for line in file:
                line_counter += 1
                if line.startswith('#'):
                    continue
                # Remove any extra whitespace and split the line by commas
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 4:
                        name = parts[0].strip()
                        try:
                            MoC = int(parts[1].strip())
                            state = int(parts[2].strip())
                            count = int(parts[3].strip())
                        except:
                            raise TypeError(f"Ошибка на строке {line_counter} в файле {self.file_name}, '{line}'.")
                        
                        # Create XenonFileSimple object
                        xenon_file = XenonFileSimple(
                            file_name=name,
                            MoC=MoC,
                            state=state,
                            count=count
                        )
                        xenon_files.append(xenon_file)

        return xenon_files