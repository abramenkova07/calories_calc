from datetime import datetime
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient, APITestCase

from calories.models import Category, EatenProduct, Product


User = get_user_model()


class UserCredentials(TestCase):

    @classmethod
    def getting_token(cls, user):
        return {
            'HTTP_AUTHORIZATION':
            f'Bearer {RefreshToken.for_user(user).access_token}'
        }

    def getting_credentials(self, user_token):
        client = APIClient()
        client.credentials(
            HTTP_AUTHORIZATION=f"{user_token['HTTP_AUTHORIZATION']}")
        return client


class TestCreation(APITestCase, UserCredentials):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username='admin',
                                             is_staff=True)
        cls.categories_data = {
            'name': 'category',
            'slug': 'slug'
        }
        cls.products_data = {
            'name': 'product',
            'weight': 100,
            'kcal': 100,
            'unit_of_measurement': 'гр',
            'category': 'slug'
        }
        cls.eaten_product_data = {
            'product': 1,
            'weight': 100,
        }
        cls.admin_token = cls.getting_token(cls.admin)
        cls.author = User.objects.create_user(username='author',
                                              is_staff=False)
        cls.author_token = cls.getting_token(cls.author)
        cls.anonymous_user = APIClient()
        cls.CATEGORIES_PATH = '/api/categories/'
        cls.PRODUCTS_PATH = '/api/products/'
        cls.EATEN_PRODUCTS_PATH = '/api/my_products/'

    def test_admin_can_create_category(self):
        initial_count = Category.objects.count()
        client = self.getting_credentials(self.admin_token)
        response = client.post(self.CATEGORIES_PATH,
                               data=self.categories_data
                               )
        updated_count = Category.objects.count()
        category = Category.objects.get()
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(initial_count + 1, updated_count)
        self.assertEqual(self.categories_data['name'], category.name)
        self.assertEqual(self.categories_data['slug'], category.slug)

    def test_other_users_cant_create_category(self):
        initial_count = Category.objects.count()
        client = self.getting_credentials(self.author_token)
        response = client.post(self.CATEGORIES_PATH,
                               data=self.categories_data)
        updated_count = Category.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(initial_count, updated_count)
        request = self.anonymous_user.post(self.CATEGORIES_PATH,
                                           data=self.categories_data
                                           )
        updated_count = Category.objects.count()
        self.assertEqual(request.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(initial_count, updated_count)

    def test_admin_can_create_product(self):
        Category.objects.create(
            name='category',
            slug='slug'
        )
        initial_count = Product.objects.count()
        client = self.getting_credentials(self.admin_token)
        response = client.post(self.PRODUCTS_PATH,
                               data=self.products_data
                               )
        updated_count = Product.objects.count()
        product = Product.objects.get()
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(initial_count + 1, updated_count)
        self.assertEqual(self.products_data['name'], product.name)
        self.assertEqual(self.products_data['weight'], product.weight)
        self.assertEqual(self.products_data['kcal'], product.kcal)
        self.assertEqual(self.products_data['unit_of_measurement'],
                         product.unit_of_measurement)
        self.assertEqual(self.products_data['category'], product.category.slug)

    def test_other_users_cant_create_product(self):
        initial_count = Product.objects.count()
        client = self.getting_credentials(self.author_token)
        response = client.post(self.PRODUCTS_PATH,
                               data=self.products_data)
        updated_count = Product.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(initial_count, updated_count)
        request = self.anonymous_user.post(self.PRODUCTS_PATH,
                                           data=self.products_data)
        updated_count = Product.objects.count()
        self.assertEqual(request.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(initial_count, updated_count)

    def test_author_can_create_eaten_products(self):
        category = Category.objects.create(
            name='category',
            slug='slug'
        )
        Product.objects.create(
            name='product',
            weight=100,
            unit_of_measurement='гр',
            kcal=100,
            category=category
        )
        initial_count = EatenProduct.objects.count()
        client = self.getting_credentials(self.author_token)
        response = client.post(self.EATEN_PRODUCTS_PATH,
                               data=self.eaten_product_data)
        updated_count = EatenProduct.objects.count()
        eaten_product = EatenProduct.objects.get()
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(initial_count + 1, updated_count)
        self.assertEqual(self.eaten_product_data['product'],
                         eaten_product.product.id)
        self.assertEqual(self.eaten_product_data['weight'],
                         eaten_product.weight)
        self.assertEqual(eaten_product.product.kcal /
                         eaten_product.product.weight *
                         int(eaten_product.weight), eaten_product.kcal)
        self.assertEqual(eaten_product.product.unit_of_measurement,
                         eaten_product.unit_of_measurement)
        self.assertEqual(eaten_product.category, eaten_product.category)
        self.assertEqual(datetime.today().date(),
                         eaten_product.publication_date)

    def test_anonymous_user_cant_create_eaten_product(self):
        category = Category.objects.create(
            name='category',
            slug='slug'
        )
        Product.objects.create(
            name='product',
            weight=100,
            unit_of_measurement='гр',
            kcal=100,
            category=category
        )
        initial_count = EatenProduct.objects.count()
        response = self.anonymous_user.post(self.EATEN_PRODUCTS_PATH,
                                            data=self.eaten_product_data)
        updated_count = EatenProduct.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEqual(initial_count, updated_count)


class TestEditDelete(APITestCase, UserCredentials):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_token = cls.getting_token(cls.author)
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
        cls.eaten_product = EatenProduct.objects.create(
            product=cls.product,
            weight=100,
            kcal=100,
            user=cls.author
        )
        cls.reader = User.objects.create(username='reader')
        cls.reader_token = cls.getting_token(cls.reader)
        cls.new_eaten_product_data = {
            'product': 1,
            'weight': 50
        }
        cls.EATEN_PRODUCT_PUT_DELETE_PATH = (f'/api/my_products/'
                                             f'{cls.eaten_product.id}/')

    def test_author_can_edit_eaten_product(self):
        client = self.getting_credentials(self.author_token)
        client.put(self.EATEN_PRODUCT_PUT_DELETE_PATH,
                   data=self.new_eaten_product_data)
        self.eaten_product.refresh_from_db()
        new_eaten_product = EatenProduct.objects.get()
        self.assertEqual(self.new_eaten_product_data['weight'],
                         new_eaten_product.weight)

    def test_other_user_cant_edit_eaten_product(self):
        client = self.getting_credentials(self.reader_token)
        response = client.put(self.EATEN_PRODUCT_PUT_DELETE_PATH,
                              data=self.new_eaten_product_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.eaten_product.refresh_from_db()
        new_eaten_product = EatenProduct.objects.get()
        self.assertEqual(self.eaten_product.weight,
                         new_eaten_product.weight)

    def test_author_can_delete_eaten_product(self):
        client = self.getting_credentials(self.author_token)
        initial_count = EatenProduct.objects.count()
        client.delete(self.EATEN_PRODUCT_PUT_DELETE_PATH)
        new_count = EatenProduct.objects.count()
        self.assertEqual(initial_count - 1, new_count)

    def test_other_user_cant_delete_eaten_product(self):
        client = self.getting_credentials(self.reader_token)
        initial_count = EatenProduct.objects.count()
        response = client.delete(self.EATEN_PRODUCT_PUT_DELETE_PATH)
        new_count = EatenProduct.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(initial_count, new_count)
