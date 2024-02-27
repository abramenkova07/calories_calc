from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets

from calories.models import Category, EatenProduct, Product
from .filters import CategoryFilter
from .permissions import AccessForUser, AdminOrReadOnly
from .serializers import (CategorySerializer, EatenProductSerializer,
                          ProductSerializer, TotalKcalSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAdminUser,)
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (CategoryFilter, filters.SearchFilter)
    search_fields = ('name',)


class EatenProductViewSet(viewsets.ModelViewSet):
    serializer_class = EatenProductSerializer
    permission_classes = (permissions.IsAuthenticated, AccessForUser)
    filter_backends = (CategoryFilter, DjangoFilterBackend,
                       filters.SearchFilter)
    filterset_fields = ('publication_date',)
    search_fields = ('product__name',)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return EatenProduct.objects.none()
        return self.request.user.eaten_products.all()

    def perform_create(self, serializer):
        product_instance = get_object_or_404(
            Product, id=serializer.initial_data['product'])
        product_weight = product_instance.weight
        product_kcal = product_instance.kcal
        eaten_product_weight = serializer.initial_data['weight']
        calculated_kcal = product_kcal / product_weight * int(
            eaten_product_weight)
        serializer.save(
            user=self.request.user,
            kcal=calculated_kcal,
            unit_of_measurement=product_instance.unit_of_measurement,
            category=product_instance.category)


class TotalKcalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TotalKcalSerializer
    lookup_field = 'publication_date'

    def get_queryset(self):
        return EatenProduct.objects.select_related(
            'category', 'product', 'user').filter(
                user=self.request.user).values('publication_date').annotate(
                    total_kcal_for_day=Sum('kcal')).order_by(
                        '-publication_date')
