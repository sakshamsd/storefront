from django.urls import path
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-review')

carts_router = routers.NestedDefaultRouter(
    router, 'carts', lookup='cart')
carts_router.register('cartitems', views.CartItemViewSet,
                      basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls
