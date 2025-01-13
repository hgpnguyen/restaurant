from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MenuItem
from .serializers import MenuItemSerializer
from .permissions import IsManager

# Create your views here.
class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action != 'list' and self.action != 'retrieve':
            permission_classes.append(IsManager)

        return [permission() for permission in permission_classes]