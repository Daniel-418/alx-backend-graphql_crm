from graphene import ObjectType, String, Schema


class Query(ObjectType):
    hello = String()

    def resolve_hello(root, info):
        return "Hello, GraphQL!"


schema = Schema(query=Query)
