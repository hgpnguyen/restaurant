from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register('menu-items', views.MenuItemsView)
router.register('groups/manager/users', views.ManagersView)

urlpatterns = [
  path('', include(router.urls)),
]