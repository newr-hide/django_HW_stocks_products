from rest_framework import serializers, viewsets

from logistic.models import Product, Stock, StockProduct
from rest_framework.exceptions import ValidationError


class ProductSerializer(serializers.ModelSerializer):
    class Meta():
        model = Product
        fields = ['id', 'title', 'description']


class PositionSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        if not all([data['product'], data['quantity']]):
            raise ValidationError({'error': 'Missing required fields: product or quantity.'})
        return data



class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta():
        model = StockProduct
        fields = ['product', 'quantity', 'price']




class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)
    
    class Meta():
        model = Stock
        fields = ['id', 'address', 'products', 'positions']



    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        stock = super().create(validated_data)

        for i in positions:
            StockProduct.objects.create(stock=stock, **i)

        return stock



    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        for i in positions:
            obj, created = StockProduct.objects.update_or_create(
                stock=stock,
                product=i['product'],
                defaults={'stock': stock, 'product': i['product'], 'quantity': i['quantity'],
                          'price': i['price']}
            )
        return stock


