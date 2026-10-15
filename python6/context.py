"""Контекстный менеджер операции провайдера."""

from contextlib import contextmanager
from datetime import datetime


class OperationContext:
    """Фиксирует начало и конец операции, в том числе при исключении."""

    def __init__(self, title):
        self.title = title
        self.started = None

    def __enter__(self):
        self.started = datetime.now()
        print(f"[контекст] начало: {self.title}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            print(f"[контекст] завершение без ошибок: {self.title}")
        else:
            print(f"[контекст] завершение с ошибкой {exc_type.__name__}: {exc_value}")
        return False


@contextmanager
def timed_block(title):
    started = datetime.now()
    print(f"[contextmanager] {title}")
    try:
        yield
    finally:
        elapsed = (datetime.now() - started).total_seconds()
        print(f"[contextmanager] {title} заняла {elapsed:.4f} с")
