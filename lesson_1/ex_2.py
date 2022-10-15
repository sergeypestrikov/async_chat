# Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования
# в последовательность кодов (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.

byte_string = [b'class', b'function', b'method']

for s in byte_string:
    print(type(s), s, len(s))