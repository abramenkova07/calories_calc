from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, EatenProductViewSet,
                    ProductViewSet, TotalKcalViewSet)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('products', ProductViewSet, basename='products')
router.register('my_products', EatenProductViewSet, basename='my_products')
router.register('total_kcal', TotalKcalViewSet, basename='total_kcal')

urlpatterns = [
    path(
        'auth/', include(
            [
                path('', include('djoser.urls')),
                path('', include('djoser.urls.jwt'))
            ]
        )
    ),
    path('', include(router.urls))
]
