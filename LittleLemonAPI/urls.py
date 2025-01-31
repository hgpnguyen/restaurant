from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter(trailing_slash=False)
router.register('menu-items/category', views.CategoryView, 'category')
router.register('menu-items', views.MenuItemsView)
router.register('groups/manager/users', views.ManagersView, 'manager')
router.register('groups/delivery-crew/users', views.DeliveryCrewsView, 'delivery-crew')
router.register('orders', views.OrderView, 'orders')

urlpatterns = [
  path('', include(router.urls)),
  path('cart/menu-items', views.CartView.as_view(), name='cart')
]