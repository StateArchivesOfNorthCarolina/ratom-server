import pytest

from django_elasticsearch_dsl.registries import registry

from api.documents.message import MessageDocument


pytestmark = pytest.mark.django_db


@pytest.fixture
def elasticsearch(autouse=True):
    registry.register_document(MessageDocument)
    for index in registry.get_indices():
        index.delete(ignore=404)
    for index in registry.get_indices():
        index.create()


def test_empty_search_returns_results(url, api_client, ratom_message):
    response = api_client.get(url, data={"account": ratom_message.account.pk})
    assert response.data["results"][0]["id"] == ratom_message.pk


def test_search_account_does_not_exist(url, api_client, ratom_message):
    response = api_client.get(url, data={"account": 1000})
    assert len(response.data["results"]) == 0
