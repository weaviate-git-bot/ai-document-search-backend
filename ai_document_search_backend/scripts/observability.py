import json

import weaviate
from dependency_injector.wiring import inject, Provide

from ai_document_search_backend.container import Container


def get_batch_with_cursor(client, class_name, class_properties, batch_size, cursor=None):
    query = (
        client.query.get(class_name, class_properties)
        .with_additional(["id"])
        .with_limit(batch_size)
    )

    if cursor is not None:
        return query.with_after(cursor).do()
    else:
        return query.do()


def get_number_of_objects(client: weaviate.Client, class_name: str) -> int:
    """
    Source: https://weaviate.io/developers/weaviate/manage-data/read-all-objects
    """

    cursor = None
    aggregate_count = 0
    while True:
        results = get_batch_with_cursor(
            client, class_name=class_name, class_properties=[], batch_size=100, cursor=cursor
        )
        # If empty, we're finished
        if len(results["data"]["Get"][class_name]) == 0:
            break

        objects_list = results["data"]["Get"][class_name]
        aggregate_count += len(objects_list)

        # Update the cursor to the id of the last retrieved object
        cursor = results["data"]["Get"][class_name][-1]["_additional"]["id"]
    return aggregate_count


def print_schema(client, class_name: str) -> None:
    print(json.dumps(client.schema.get(class_name), indent=2))


@inject
def main(
    client: weaviate.Client = Provide[Container.weaviate_client],
    class_name: str = Provide[Container.config.weaviate.class_name],
) -> None:
    number_of_objects = get_number_of_objects(client, class_name)
    print(f"Number of objects: {number_of_objects}")

    print_schema(client, class_name)


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    main()
