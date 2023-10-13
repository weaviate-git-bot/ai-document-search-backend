import logging

from dependency_injector.wiring import Provide, inject

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.chatbot_service import ChatbotService
from ai_document_search_backend.utils.relative_path_from_file import (
    relative_path_from_file,
)

PDF_DIR_PATH = relative_path_from_file(__file__, "../../data/pdfs_subset/")
METADATA_PATH = relative_path_from_file(__file__, "../../data/clean_data_subset.csv")


@inject
def main(chatbot_service: ChatbotService = Provide[Container.chatbot_service]) -> None:
    chatbot_service.delete_schema()

    chatbot_service.store(PDF_DIR_PATH, METADATA_PATH)

    # chatbot_service.answer("What is the Loan to value ratio?", "user1")


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    logging.basicConfig(level=logging.INFO)
    main()
