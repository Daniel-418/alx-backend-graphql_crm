from graphene import ObjectType, String, Schema


class Query(ObjectType):
    name = String()

    def resolve_name(root, info):
        return "Hello, GraphQL!"


schema = Schema(query=Query)
