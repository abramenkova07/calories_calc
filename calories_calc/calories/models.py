from django.contrib.auth import get_user_model
from django.db import models

from .constants import (CHARACTER_QUANTITY, NAME_MAX_LENGTH,
                        UNIT_OF_MEASUREMENT, UOM_MAX_LENGTH)


User = get_user_model()


class NameModel(models.Model):
    name = models.CharField('Название',
                            max_length=NAME_MAX_LENGTH,
                            unique=True)

    class Meta:
        abstract = True


class WeightModel(models.Model):
    weight = models.PositiveSmallIntegerField('Вес')
    unit_of_measurement = models.CharField('Единица измерения',
                                           max_length=UOM_MAX_LENGTH,
                                           choices=UNIT_OF_MEASUREMENT)
    kcal = models.PositiveSmallIntegerField('Ккал')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категория')

    class Meta:
        abstract = True


class Category(NameModel):
    slug = models.SlugField('Слаг',
                            max_length=NAME_MAX_LENGTH,
                            unique=True)

    class Meta:
        ordering = ('slug',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class Product(NameModel, WeightModel):
    pass

    class Meta:
        ordering = ('name',)
        default_related_name = 'products'
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'

    def __str__(self):
        return self.name[:CHARACTER_QUANTITY]


class EatenProduct(WeightModel):
    publication_date = models.DateField('Дата добавления продукта',
                                        auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Продукт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        ordering = ('-publication_date',)
        default_related_name = 'eaten_products'
        verbose_name = 'съеденный продукт'
        verbose_name_plural = 'съеденные продукты'

    def __str__(self):
        return f'{self.user} - {self.publication_date} - {self.product}'
