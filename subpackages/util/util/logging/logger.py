import structlog
from structlog.dev import ConsoleRenderer, _ColorfulStyles
import textwrap

def dedent_processor(logger, method, event_dict):
    event = event_dict['event']
    event = textwrap.dedent(event).strip("\n")
    event = textwrap.indent(event,"    ")
    event = f"\n\n{event}\n\n"
    event_dict['event'] = event
    return event_dict

def get_logger(name: str):
    logger = structlog.get_logger(name)
    return structlog.wrap_logger(
        logger,
        processors=[
            dedent_processor,
        ]
    )
