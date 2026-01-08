# type: ignore
import re
import graphene
import graphene_django
from .models import Customer


class CustomerType(graphene_django.DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


def validate_and_save_customer(name, email, phone=None):
    """
    Tries to create a customer.
    Returns: (success_boolean, message_string, customer_object_or_None)
    """
    # 1. Check Email
    if Customer.objects.filter(email=email).exists():
        return False, "Error: This email already exists.", None

    # 2. Check Phone
    if phone:
        phone_pattern = re.compile(
            r"^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
        )
        if not phone_pattern.match(phone):
            return False, "Error: Invalid phone number format.", None

    # 3. Save
    try:
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return True, "Customer created successfully", customer
    except Exception as e:
        return False, f"Error: {str(e)}", None


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    success = graphene.Boolean()
    message = graphene.String()
    customer = graphene.Field(CustomerType)

    def mutate(root, info, name, email, phone=None):
        success, message, customer = validate_and_save_customer(
            name=name, email=email, phone=phone
        )
        return CreateCustomer(success=success, message=message, customer=customer)


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CustomerInput, required=True)

    success = graphene.Boolean()
    customers_created = graphene.List(lambda: CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, customers):
        customer_objects = []
        local_errors = []

        for customer in customers:
            success, message, customer = validate_and_save_customer(
                name=customer.name, phone=customer.phone, email=customer.email
            )

            if success:
                customer_objects.append(customer)
            else:
                local_errors.append(f"Failed to create {customer.name}: {message}")

        status = len(local_errors) == 0

        return BulkCreateCustomers(
            customers_created=customer_objects,
            success=status,
            errors=local_errors,
        )


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    customer = graphene.List(CustomerType)

    def resolve_customer(root, info):
        return Customer.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customer = BulkCreateCustomers.Field()
