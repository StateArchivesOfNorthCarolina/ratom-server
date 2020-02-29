import os
import pytest

pytestmark = [
    pytest.mark.skipif(
        os.getenv("TEST_ELASTICSEARCH", "false") == "false",
        reason="TEST_ELASTICSEARCH is not set to 'true'",
    ),
    pytest.mark.django_db,
]


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
    assert event.name in response.data["results"][0]["audit"]["labels"][0]["name"]


def test_label_match_excludes_others(url, api_client, sally1, sally2, event, org):
    sally1.audit.labels.add(event)
    sally2.audit.labels.add(org)
    sally1.save()
    sally2.save()
    response = api_client.get(url, data={"labels_importer": event.name})
    assert event.name in response.data["results"][0]["audit"]["labels"][0]["name"]
    assert org.name not in response.data["results"][0]["audit"]["labels"][0]["name"]


def test_label_match__or(url, api_client, sally1, sally2, sally3, event, org, date):
    sally1.audit.labels.add(event)
    sally2.audit.labels.add(org)
    sally3.audit.labels.add(date)
    sally1.save()
    sally2.save()
    sally3.save()
    response = api_client.get(
        url, data={"labels_importer__terms": f"{event.name}__{org.name}"}
    )
    matched_messages = [result["id"] for result in response.data["results"]]
    assert sally1.pk in matched_messages and sally2.pk in matched_messages
    assert sally3.pk not in matched_messages
