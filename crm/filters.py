import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_at_gte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_lte = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Customer
        fields = ["created_at", "name", "email"]


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    stock__gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock__lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    price__lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    price__gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")

    class Meta:
        model = Product
        fields = ["stock", "price"]


class OrderFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    total_amount__gte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    total_amount__lte = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )
    customer_name = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    product_name = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains"
    )

    product_id = django_filters.NumberFilter(
        field_name="products__id", lookup_expr="exact"
    )

    class Meta:
        model = Order
        fields = ["total_amount", "customer", "products"]
