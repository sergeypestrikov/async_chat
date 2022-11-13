from datetime import datetime

enable_tracing = True
if enable_tracing:
    info_call = open('info_call.log', 'w')


def log(func):
    if enable_tracing:
        def wrapper(*args, **kwargs):
            info_call.write(f'log: {datetime.now()} вызвана функция {func.__name__} с аргументами {args} {kwargs}')
            r = func(*args, **kwargs)
            print(f'Функция {func.__name__} вернула {r}')
            return r
        return wrapper
    else:
        return func