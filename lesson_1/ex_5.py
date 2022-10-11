# Выполнить пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовать результаты из байтовового в строковый тип на кириллице.

import subprocess

args = ['ping', 'yandex.ru']

subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    result = line.decode('cp866')
    print(type(result), result)