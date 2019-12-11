import graphene
import graphql_jwt

import ratom.schema


class RootQuery(ratom.schema.Query, graphene.ObjectType):
    pass


class RootMutation(ratom.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    # pass


schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
#ratom.schema.Query