import structlog


def get_logger(name: str):
    return structlog.get_logger(module_name=name)
