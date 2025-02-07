class DBDataBiggerThanTableException(Exception):
    """Исключение, если данные, полученные из БД, не умещаются в таблицу."""
