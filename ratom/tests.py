from graphene_django.utils.testing import GraphQLTestCase
from ratom_api.schema import schema
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase


class TestAuthentication(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="test", password="1234")

    def test_authentication_mutation(self):
        response = self.query(
            """
             mutation Login($email: String, $password: String) {
                tokenAuth(username: $email, password: $password) {
                token
                user {
                        id
                    }
                }
            }
            """,
            op_name="tokenAuth",
            input_data={"email": "test", "password": "1234"},
        )
        import pudb

        pudb.set_trace()
        self.assertResponseHasErrors(response)


class TestAuthenticationWithJSON(JSONWebTokenTestCase):
    pass
