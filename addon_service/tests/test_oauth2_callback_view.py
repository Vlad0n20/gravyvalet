from http import HTTPStatus

from django.test import SimpleTestCase
from django.urls import reverse


class TestOAuth2CallbackViewErrors(SimpleTestCase):
    def test_error_response_from_provider(self):
        _resp = self.client.get(
            reverse("oauth2-callback"),
            {
                "error": "access_denied",
                "error_description": "user said no",
                "state": "1.nonce",
            },
        )
        self.assertEqual(_resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("access_denied", _resp.content.decode())
        self.assertIn("user said no", _resp.content.decode())
