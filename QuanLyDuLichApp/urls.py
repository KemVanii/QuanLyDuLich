from django.urls import path, include
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
# router.register(r'tintuc', BaiDangTinTucViewSet, basename='tintuc')
router.register('users', UserViewSet, basename='users')
router.register(r'danhmuc', DanhMucViewSet, basename='danhmuc')
router.register('tags',TagViewSet,basename='tags')
router.register('comments', CommentViewSet, basename='comment')
router.register('local',LocalViewSet,basename='local')
router.register('picture',PictureViewSet,basename='picture')
router.register('transports',TransportationViewSet,basename='transports')

urlpatterns = [
    path('', include(router.urls)),
    # path('api/user_pay/', save_user_data, name='save_user_data'),
    path('api/save_invoice_and_send_email', save_invoice_and_send_email, name='save_invoice_and_send_email'),
]
