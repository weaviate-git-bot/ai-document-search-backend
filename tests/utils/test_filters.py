from ai_document_search_backend.services.chatbot_service import Filter
from ai_document_search_backend.utils.filters import construct_and_filter


def test_empty_filters():
    and_filter = construct_and_filter([])
    assert and_filter == {}


def test_one_filter_with_no_value():
    and_filter = construct_and_filter([Filter(property_name="isin", values=[])])
    assert and_filter == {}


def test_one_filter_with_no_value_and_one_with_value():
    and_filter = construct_and_filter(
        [
            Filter(property_name="isin", values=[]),
            Filter(property_name="industry", values=["Real Estate - Commercial"]),
        ]
    )
    assert and_filter == {
        "operator": "And",
        "operands": [
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["industry"],
                        "operator": "Equal",
                        "valueText": "Real Estate - Commercial",
                    },
                ],
            },
        ],
    }


def test_one_filter_with_one_value():
    and_filter = construct_and_filter([Filter(property_name="isin", values=["NO1111111111"])])
    assert and_filter == {
        "operator": "And",
        "operands": [
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO1111111111",
                    },
                ],
            },
        ],
    }


def test_one_filter_with_multiple_values():
    and_filter = construct_and_filter(
        [Filter(property_name="isin", values=["NO1111111111", "NO2222222222"])]
    )
    assert and_filter == {
        "operator": "And",
        "operands": [
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO1111111111",
                    },
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO2222222222",
                    },
                ],
            },
        ],
    }


def test_multiple_filters_with_one_value():
    and_filter = construct_and_filter(
        [
            Filter(property_name="isin", values=["NO1111111111"]),
            Filter(property_name="industry", values=["Real Estate - Commercial"]),
        ]
    )
    assert and_filter == {
        "operator": "And",
        "operands": [
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO1111111111",
                    },
                ],
            },
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["industry"],
                        "operator": "Equal",
                        "valueText": "Real Estate - Commercial",
                    },
                ],
            },
        ],
    }


def test_multiple_filters_with_multiple_values():
    and_filter = construct_and_filter(
        [
            Filter(property_name="isin", values=["NO1111111111", "NO2222222222"]),
            Filter(
                property_name="industry",
                values=["Real Estate - Commercial", "Real Estate - Residential"],
            ),
        ]
    )
    assert and_filter == {
        "operator": "And",
        "operands": [
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO1111111111",
                    },
                    {
                        "path": ["isin"],
                        "operator": "Equal",
                        "valueText": "NO2222222222",
                    },
                ],
            },
            {
                "operator": "Or",
                "operands": [
                    {
                        "path": ["industry"],
                        "operator": "Equal",
                        "valueText": "Real Estate - Commercial",
                    },
                    {
                        "path": ["industry"],
                        "operator": "Equal",
                        "valueText": "Real Estate - Residential",
                    },
                ],
            },
        ],
    }
