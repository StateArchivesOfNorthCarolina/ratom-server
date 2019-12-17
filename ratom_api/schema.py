import graphene
import graphql_jwt

import ratom.schema


class RootQuery(ratom.schema.Query, graphene.ObjectType):
    pass


class RootMutation(ratom.schema.Mutation, graphene.ObjectType):
    token_auth = ratom.schema.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
