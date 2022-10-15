# Выполнить пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовать результаты из байтовового в строковый тип на кириллице.

import subprocess
import chardet

args = ['ping', 'yandex.ru']

subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    char_det = chardet.detect(line)
    result = line.decode(char_det['encoding']).encode('UTF-8')
    print(type(result), result.decode('UTF-8'))