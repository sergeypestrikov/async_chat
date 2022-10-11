# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

a = b'attribute'
b = b'класс'
c = b'функция'
d = b'type'

# Ответ: в байтовом типе невозможно записать слова на кириллице

#
# /usr/local/bin/python3.9 /Users/mac/PycharmProjects/async_chat_new/lesson_1/ex_3.py
#   File "/Users/mac/PycharmProjects/async_chat_new/lesson_1/ex_3.py", line 4
#     b = b'класс'
#                      ^
# SyntaxError: bytes can only contain ASCII literal characters.
#
# Process finished with exit code 1