# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

f = open('3.txt')

for line in f:
    try:
        non_bytes = line.encode('ascii')
        print(f'{line} - можно записать в байтах')
    except:
        print(f'{line} - неможно записать в байтах')



