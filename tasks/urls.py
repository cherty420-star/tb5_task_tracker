from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, StatusViewSet, PriorityViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'statuses', StatusViewSet, basename='status')
router.register(r'priorities', PriorityViewSet, basename='priority')

urlpatterns = [
    path('', include(router.urls)),
]