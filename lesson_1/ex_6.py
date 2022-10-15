# Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор». Проверить кодировку файла по умолчанию.
# Принудительно открыть файл в формате Unicode и вывести его содержимое.
import locale

coding = locale.getpreferredencoding()

with open('text_for_six.txt', 'r', encoding=coding) as f:
    for line in f:
        print(line)

