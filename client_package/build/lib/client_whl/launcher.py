import subprocess

def main():
    process = []

    while True:
        action = input('Выберите действие: q - выход, s - запуск сервера, k - запуск клиента, x - закрыть все: ')
        if action == 'q':
            break
        elif action == 's':
            process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегино необходимое кол-во клинетов с паролем 123456')
            print('Из-за генерации ключей первый запуск может быть долгим')
            clients_count = int(input('Введите кол-во тестовых клиентов для запуска: '))
            for i in range(clients_count):
                process.append(subprocess.Popen(f'python client.py -n test{i + 1} -p 123456', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'x':
            while process:
                process.pop().kill()


if __name__ == '__main__':
    main()
