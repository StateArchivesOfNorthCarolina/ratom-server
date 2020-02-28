import pytest

pytestmark = pytest.mark.django_db


def test_account_message_in_results(url, api_client, ratom_message):
    response = api_client.get(url, data={"account": ratom_message.account.pk})
    assert response.data["results"][0]["id"] == ratom_message.pk


def test_account_does_not_exist(url, api_client, ratom_message):
    response = api_client.get(url, data={"account": 1000})
    assert not response.data["results"]


def test_label_match_single_term(url, api_client, sally1, event):
    sally1.audit.labels.add(event)
    sally1.save()
    response = api_client.get(url, data={"labels_importer": event.name})
    assert event.name in response.data["results"][0]["labels"]["importer"]


def test_label_match_exclude_others(url, api_client, sally1, sally2, event, org):
    sally1.audit.labels.add(event)
    sally1.save()
    sally2.audit.labels.add(org)
    sally2.save()
    response = api_client.get(url, data={"labels_importer": event.name})
    assert event.name in response.data["results"][0]["labels"]["importer"]
    assert org.name not in response.data["results"][0]["labels"]["importer"]
