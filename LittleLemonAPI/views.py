from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from rest_framework.response import Response
from .models import MenuItem, Cart, Order, OrderItem, Category
from .serializers import *
from .permissions import IsManager, IsDeliveryCrew
from datetime import date

class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['featured', 'category']
    ordering_fields = ['featured', 'price']
    search_fields = ['title', 'category__title']
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action != 'list' and self.action != 'retrieve':
            permission_classes.append(IsManager)

        return [permission() for permission in permission_classes]
    
class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManager]
    ordering_fields = ['title', 'slug']
    search_fields = ['title', 'slug']
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    
User = get_user_model()
class GroupView(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    ordering_fields = ['username']
    search_fields = ['username', 'email']
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    group = ''

    def get_queryset(self):
        if self.action == 'list' or self.action == 'retrieve':
            queryset = User.objects.filter(groups__name=self.group)
        else:
            queryset = User.objects.all()
        return queryset

    def get_group(self):
        group, _ = Group.objects.get_or_create(name=self.group)
        return group
    
    def create(self, request, *args, **kwargs):
        user = generics.get_object_or_404(self.queryset, username=request.data['username'])
        group = self.get_group()
        user.groups.add(group)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        group = self.get_group()
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)

class ManagersView(GroupView):
    group = "Manager"

class DeliveryCrewsView(GroupView):
    group = "Delivery crew"

class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated)
    filterset_fields = ['menuitem__featured', 'menuitem__category']
    ordering_fields = ['price', 'unit_price']
    search_fields = ['menuitem__title']
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    

    def delete(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderView(mixins.ListModelMixin,
                mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    filterset_fields = ['user', 'delivery_crew', 'status']
    ordering_fields = ['total', 'date']
    search_fields = ['user__username', 'delivery_crew__username']
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            queryset = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            queryset = Order.objects.filter(delivery_crew=self.request.user)
        else:
            queryset = Order.objects.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.request.user.groups.filter(name='Delivery crew').exists():
            return DeliveryOrderSerializer
        return super().get_serializer_class()
        
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        permissionDict = {
            'update': [IsManager],
            'partial_update': [IsManager|IsDeliveryCrew],
            'destroy': [IsManager] 
        }
        return [permission() for permission in permission_classes + permissionDict.get(self.action, [])]
    
    def create(self, request, *args, **kwargs):
        carts = Cart.objects.filter(user=request.user)
        totalPrice = sum(cart.price for cart in carts)
        order = Order(user=request.user, total=totalPrice, status=False, date=date.today())
        order.save()
        for cart in carts:
            orderItem = OrderItem(order=order, menuitem=cart.menuitem, 
                                  quantity=cart.quantity, unit_price=cart.unit_price, 
                                  price=cart.price)
            orderItem.save()
            cart.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        orderItemView = OrderItemView(request=request, args=self.args, kwargs=self.kwargs)
        orderItemView.initial(request, *args, **kwargs)
        return orderItemView.list(request, *args, **kwargs)


class OrderItemView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    filterset_fields = ['menuitem__featured', 'menuitem__category']
    ordering_fields = ['price', 'unit_price']
    search_fields = ['menuitem__title']

    def get_queryset(self):
        queryset = OrderItem.objects.filter(order__id=self.kwargs['pk'])
        return queryset

