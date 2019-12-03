import graphene

import ratom.schema


class RootQuery(ratom.schema.Query, graphene.ObjectType):
    pass


# class RootMutation(graphene.ObjectType):
#     pass


# remove the parameters for the server to start
# will not start correctly because we don't have any schema!
schema = graphene.Schema(query=ratom.schema.Query)
