# type: ignore
import re
import graphene
import graphene_django
from .models import Customer


class CustomerType(graphene_django.DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    success = graphene.Boolean()
    message = graphene.String()
    customer = graphene.Field(CustomerType)

    def mutate(root, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(
                success=False, message="Error: Invalid email", customer=None
            )

        if phone:
            phone_pattern = re.compile(
                r"^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
            )
            if not phone_pattern.match(phone):
                return CreateCustomer(
                    success=False,
                    message="Error: Invalid phone number format.",
                    customer=None,
                )

        try:
            customer = Customer(name=name, email=email, phone=phone)
            customer.save()
            return CreateCustomer(
                customer=customer, success=True, message="Customer created successfully"
            )
        except Exception as e:
            return CreateCustomer(
                success=False, customer=None, message=f"error: {str(e)}"
            )


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
