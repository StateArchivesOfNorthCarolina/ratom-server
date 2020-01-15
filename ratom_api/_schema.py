# import graphene
# import graphql_jwt
# from graphene_django.debug import DjangoDebug

# import ratom.schema


# class RootQuery(ratom.schema.Query, graphene.ObjectType):
#     debug = graphene.Field(DjangoDebug, name="_debug")


# class RootMutation(ratom.schema.Mutation, graphene.ObjectType):
#     token_auth = ratom.schema.ObtainJSONWebToken.Field()
#     verify_token = graphql_jwt.Verify.Field()
#     refresh_token = graphql_jwt.Refresh.Field()


# schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
