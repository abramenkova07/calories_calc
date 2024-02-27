from http import HTTPStatus
import os

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient, APITestCase

from calories.models import Category, EatenProduct, Product


User = get_user_model()


class TestAPIEndpoints(APITestCase):

    @classmethod
    def getting_token(cls, user):
        return {
            'HTTP_AUTHORIZATION':
            f'Bearer {RefreshToken.for_user(user).access_token}'
        }

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.anonymous_user = APIClient()
        cls.admin = User.objects.create(username='admin',
                                        is_staff=True)
        cls.admin_token = cls.getting_token(cls.admin)
        cls.category = Category.objects.create(
            name='category',
            slug='slug'
        )
        cls.product = Product.objects.create(
            name='product',
            weight=100,
            unit_of_measurement='гр',
            kcal=100,
            category=cls.category
        )
        cls.author = User.objects.create(username='author')
        cls.author_token = cls.getting_token(cls.author)
        cls.author_product = EatenProduct.objects.create(
            product=cls.product,
            weight=100,
            kcal=100,
            user=cls.author
        )
        cls.reader = User.objects.create(username='reader')
        cls.reader_token = cls.getting_token(cls.reader)
        cls.BASE_PATH = 'http://127.0.0.1:8000/api/'
        cls.PRODUCTS_PATH = os.path.join(cls.BASE_PATH, 'products/')
        cls.CATEGORIES_PATH = os.path.join(cls.BASE_PATH, 'categories/')
        cls.MY_PRODUCTS_PATH = os.path.join(cls.BASE_PATH, 'my_products/')
        cls.MY_SINGLE_PRODUCT_PATH = os.path.join(cls.BASE_PATH,
                                                  'my_products/',
                                                  f'{cls.author_product.id}/')
        cls.TOTAL_KCAL_PATH = os.path.join(cls.BASE_PATH, 'total_kcal/')

    def test_pages_availability(self):
        urls = (
            (self.PRODUCTS_PATH, self.anonymous_user, None, HTTPStatus.OK),
            (self.PRODUCTS_PATH, self.admin, self.admin_token, HTTPStatus.OK),
            (self.CATEGORIES_PATH, self.anonymous_user, None,
             HTTPStatus.UNAUTHORIZED),
            (self.CATEGORIES_PATH, self.admin, self.admin_token,
             HTTPStatus.OK),
            (self.CATEGORIES_PATH, self.author, self.author_token,
             HTTPStatus.FORBIDDEN),
            (self.MY_PRODUCTS_PATH, self.author, self.author_token,
             HTTPStatus.OK),
            (self.MY_PRODUCTS_PATH, self.anonymous_user, None,
             HTTPStatus.UNAUTHORIZED),
            (self.MY_SINGLE_PRODUCT_PATH, self.author, self.author_token,
             HTTPStatus.OK),
            (self.MY_SINGLE_PRODUCT_PATH, self.reader, self.reader_token,
             HTTPStatus.NOT_FOUND),
            (self.MY_SINGLE_PRODUCT_PATH, self.anonymous_user, None,
             HTTPStatus.UNAUTHORIZED),
            (self.TOTAL_KCAL_PATH, self.anonymous_user, None,
             HTTPStatus.UNAUTHORIZED),
            (self.TOTAL_KCAL_PATH, self.author, self.author_token,
             HTTPStatus.OK)
        )
        for url, user, token, status in urls:
            if user != self.anonymous_user:
                response = self.client.get(url, **token)
            else:
                response = self.client.get(url)
            with self.subTest(name=url):
                self.assertEqual(response.status_code, status)
