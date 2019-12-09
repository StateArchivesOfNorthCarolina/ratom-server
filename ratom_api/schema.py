import graphene

import ratom.schema


class RootQuery(ratom.schema.Query, graphene.ObjectType):
    pass


class RootMutation(ratom.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=RootQuery, mutation=RootMutation)
#ratom.schema.Query