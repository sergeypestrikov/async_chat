# Преобразовать слова «разработка», «администрирование», «protocol», «standard»
# из строкового представления в байтовое и выполнить обратное преобразование (используя методы encode и decode)

string_list = ['разработка', 'администрирование', 'protocol', 'standard']

for s in string_list:
    en = s.encode('UTF-8')
    print(en)
    de = bytes.decode(en, 'UTF-8')
    print(de)
