import graphene
import luci.schema as luci_schema


class Query(graphene.ObjectType, luci_schema.Query):
    pass

class Mutation(graphene.ObjectType, luci_schema.Mutation):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)