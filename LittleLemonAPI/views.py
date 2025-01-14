from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import MenuItem, Cart
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
from .permissions import IsManager

class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action != 'list' and self.action != 'retrieve':
            permission_classes.append(IsManager)

        return [permission() for permission in permission_classes]
    
User = get_user_model()
class GroupView(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderView(viewsets.GenericViewSet):
    pass