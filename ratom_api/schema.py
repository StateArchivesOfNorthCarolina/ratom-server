import graphene


class Query(graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    pass


# remove the parameters for the server to start
# will not start correctly because we don't have any schema!
schema = graphene.Schema()
