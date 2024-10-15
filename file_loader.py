import os


class KeyValueFileParser:
    keywords = {
        "Unit",
        "Camp",

        "NS_40_05_state", 
        "NS_40_05_copy_count",

        "NS_40_60_state", 
        "NS_40_60_copy_count",

        "NS_01_60_state",
        "NS_01_60_copy_count",
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