import os
import pytest
import gzip
import json

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


def test_keywords_use_or_searching(url, api_client, sally4_known_bodies):
    m1, m2 = sally4_known_bodies
    response = api_client.get(
        url, data={"search_simple_query_string": "FileZilla,Zombie"}
    )
    assert m1.file.message_set.all().count() == 5
    assert len(response.data["results"]) == 2
    decomposed = list(response.data["results"][0].values()) + list(
        response.data["results"][1].values()
    )
    assert str(m1.source_id) in decomposed
    assert str(m2.source_id) in decomposed


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


def test_export_match_one_file(export_url, api_client, sally1, eric1, org, event):
    sally1.audit.labels.add(event)
    sally1.save()
    eric1.audit.labels.add(org)
    eric1.save()
    response = api_client.get(
        export_url, data={"labels_importer__terms": f"{org.name}"}
    )
    resp_data = json.loads(gzip.decompress(response.data))
    assert len(resp_data) == 1
    assert eric1.file.filename in resp_data[0].values()
    assert eric1.file.sha256 in resp_data[0].values()
    assert eric1.source_id in list(resp_data[0].values())[2]


def test_export_match_two_file(
    export_url, api_client, sally1, sally2, eric1, org, event
):
    sally1.audit.labels.add(event)
    sally2.audit.labels.add(org)
    sally1.save()
    sally2.save()
    eric1.audit.labels.add(org)
    eric1.save()
    response = api_client.get(
        export_url, data={"labels_importer__terms": f"{org.name}__{event.name}"}
    )
    resp_data = json.loads(gzip.decompress(response.data))
    assert len(resp_data) == 2
    decomposed = list(resp_data[0].values()) + list(resp_data[1].values())
    source_ids = decomposed[2] + decomposed[5]
    assert eric1.file.filename in decomposed
    assert eric1.file.sha256 in decomposed
    assert sally1.file.filename in decomposed
    assert sally1.file.sha256 in decomposed
    assert eric1.source_id in source_ids
    assert sally1.source_id in source_ids
    assert sally2.source_id in source_ids
