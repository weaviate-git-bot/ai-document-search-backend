from dependency_injector import containers, providers

from . import services
from .utils import relative_path_from_file

CONFIG_PATH = relative_path_from_file.relative_path_from_file(__file__, "../config.yml")


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".endpoints"])

    config = providers.Configuration(yaml_files=[CONFIG_PATH])

    summarization_service = providers.Factory(
        services.SummarizationService,
    )
