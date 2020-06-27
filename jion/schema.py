import graphene
import luci.schema as luci_schema


class Query(graphene.ObjectType, luci_schema.Query):
    pass

schema = graphene.Schema(query=Query, auto_camelcase=False)