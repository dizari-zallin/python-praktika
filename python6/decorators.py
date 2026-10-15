"""Декораторы журналирования, проверки и повтора."""

from functools import wraps


def log_call(func):
    """Пишет имя функции и результат."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[декоратор log_call] вызов {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[декоратор log_call] {func.__name__} завершена")
        return result

    return wrapper


def require_positive(func):
    """Проверяет, что числовые аргументы больше нуля."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for value in list(args) + list(kwargs.values()):
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value <= 0:
                raise ValueError("числовой аргумент должен быть больше нуля")
        return func(*args, **kwargs)

    return wrapper


# Сначала принимается параметр times, и только потом декоратор оборачивает функцию.
def repeat(times):
    """Декоратор с параметром: повторяет вызов times раз, возвращает последний результат."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for index in range(times):
                result = func(*args, **kwargs)
                print(f"[декоратор repeat] проход {index + 1} из {times}")
            return result

        return wrapper

    return decorator
