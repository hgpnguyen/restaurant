from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator 
from .models import MenuItem, Category, Cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'slug')

class MenuItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuItem
        fields = '__all__'

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('email',)
    
class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'unit_price', 'quantity', 'price']
        read_only_fields = ('price',)
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['user', 'menuitem']
            ),
        ]
    
    def validate(self, attrs):
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('order', 'menuitem', 'quantity', 'unit_price', 'price')
class OrderSerializer(serializers.ModelSerializer):

    orderitem = OrderItemSerializer(many=True, read_only=True, source='order')
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 
                  'status', 'total', 'date', 'orderitem']
    
    def validate_delivery_crew(self, value):
        try:
            delivery = User.objects.get(pk=value.pk)
        except User.DoesNotExist:
            raise serializers.ValidationError("Delivery crew not found")
        if not delivery.groups.filter(name='Delivery crew').exists():
            raise serializers.ValidationError("This user is not a delivery crew")
        return value
    
    
class DeliveryOrderSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(required=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'delivery_crew', 'status', 'total', 'date')
        read_only_fields = ('user', 'delivery_crew', 'total', 'date')



