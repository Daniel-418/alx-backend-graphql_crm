# type: ignore
import re
import graphene
import graphene_django
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Order, Product
from .filters import CustomerFilter, OrderFilter, ProductFilter


class ProductType(graphene_django.DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class CustomerType(graphene_django.DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = ("id", "name", "email", "phone", "created_at")


class OrderType(graphene_django.DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


def validate_and_save_customer(name, email, phone=None):
    if Customer.objects.filter(email=email).exists():
        return False, "Error: This email already exists.", None

    if phone:
        phone_pattern = re.compile(
            r"^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
        )
        if not phone_pattern.match(phone):
            return False, "Error: Invalid phone number format.", None

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


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(required=False)

    success = graphene.Boolean()
    product = graphene.Field(ProductType)
    error_message = graphene.String()

    def mutate(root, info, name, price, stock):
        if price > 0 and stock >= 0:
            try:
                product = Product.objects.create(name=name, price=price, stock=stock)
                status = True
                return CreateProduct(success=status, product=product)
            except Exception as e:
                status = False
                return CreateProduct(
                    success=status,
                    product=None,
                    error_message=f"error creating product: {e}",
                )


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.Int(required=True)
        products = graphene.List(graphene.ID)

    success = graphene.Boolean()
    order = graphene.Field(OrderType)
    error_message = graphene.String()

    def mutate(root, info, customer_id, products):
        customer = Customer.objects.filter(pk=customer_id).first()

        if customer:
            try:
                if products:
                    local_order = Order()
                    local_order.customer = customer

                    local_order.save()

                    for p_id in products:
                        product = Product.objects.get(pk=p_id)
                        local_order.products.add(product)
                        local_order.total_amount += product.price

                    local_order.save()
                    return CreateOrder(success=True, order=local_order)
            except Exception as e:
                return CreateOrder(
                    success=False,
                    order=None,
                    error_message=f"Error creating order: {e}",
                )
            else:
                return CreateOrder(
                    success=False,
                    order=None,
                    error_message="At least one product must be specified with an order",
                )
        else:
            return CreateOrder(
                success=False, order=None, error_message="Customer does not exist"
            )


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerType, filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType, filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    hello = graphene.String(default_value="Hello, GraphQL!")
    customer = graphene.List(CustomerType)
    product = graphene.List(ProductType)
    order = graphene.List(OrderType)

    def resolve_customer(root, info):
        return Customer.objects.all()

    def resolve_product(root, info):
        return Product.objects.all()

    def resolve_order(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customer = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
