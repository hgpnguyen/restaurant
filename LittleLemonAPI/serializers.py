from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
    
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')
        read_only_fields = ('email',)
    
class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('user', 'menuitem', 'quantity', 'unit_price', 'price')

class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('user', 'delivery_crew', 'status', 'total', 'date')