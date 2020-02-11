from http import HTTPStatus
import pytest

from django.urls import reverse

from core.models import File

pytestmark = pytest.mark.django_db


def test_reset(settings, api_client):
    """Simple test to make sure 2 files exist after running a sample data reset."""
    settings.RATOM_SAMPLE_DATA_ENABLED = True
    response = api_client.post(reverse("reset_sample_data"))
    assert response.status_code == HTTPStatus.OK.value
    assert File.objects.count() == 2
