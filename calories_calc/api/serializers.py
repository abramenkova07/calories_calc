from django.shortcuts import get_object_or_404
from rest_framework import serializers

from calories.models import Category, EatenProduct, Product


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Product
        fields = '__all__'


class EatenProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    category = serializers.SlugRelatedField(
        read_only=True, slug_field='slug'
    )

    class Meta:
        model = EatenProduct
        fields = '__all__'
        read_only_fields = ('publication_date', 'kcal',
                            'unit_of_measurement')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        product_name = get_object_or_404(Product, id=representation[
            'product']).name
        representation['product'] = product_name
        return representation


class TotalKcalSerializer(serializers.ModelSerializer):
    total_kcal_for_day = serializers.IntegerField(read_only=True)
    date = serializers.DateField(read_only=True,
                                 source='publication_date')
    lookup_field = 'publication_date'
    extra_kwargs = {
        'url': {'lookup_field': 'publication_date'}
    }

    class Meta:
        model = EatenProduct
        fields = ('date', 'total_kcal_for_day')
