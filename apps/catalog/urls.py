from django.urls import path


from apps.catalog.views import order, pos, purchase, views, warehouse


app_name = 'catalog'

urlpatterns = [

    ##########  Catalog Category Admin #########
    path('catalog/category/', views.AdminCatalogCategoriesList, name='AdminCatalogCategoriesList'),
    path('catalog/category/detail/<slug:slug>/', views.AdminCatalogCategoriesDetail,
         name='AdminCatalogCategoriesDetail'),
    path('catalog/category/update/<slug:slug>/', views.AdminCatalogCategoriesUpdate, name='AdminCatalogCategoriesUpdate'),
    path('catalog/category/delete/<slug:slug>/', views.AdminCatalogCategoriesDelete,
         name='AdminCatalogCategoriesDelete'),

    ##########  Catalog Product Admin #########
    path('catalog/product/', views.AdminCatalogProductList, name='AdminCatalogProductList'),
    path('catalog/product/add/', views.AdminCatalogProductCreate, name='AdminCatalogProductCreate'),
    path('catalog/product/simple/add/', views.AdminCatalogProductSimpleCreate, name='AdminCatalogProductSimpleCreate'),
    path('catalog/product/detail/<slug:slug>/', views.AdminDetailsCatalogProduct, name='AdminCatalogProductDetails'),
    path('catalog/product/update/<slug:slug>/', views.AdminCatalogProductUpdate, name='AdminCatalogProductUpdate'),
    path('catalog/product/delete/<slug:slug>/', views.AdminDeleteCatalogProduct, name='AdminCatalogProductDelete'),
    path('catalog/product/price/', views.AdminProductFinalPrice, name='AdminProductFinalPrice'),

    ##########  Catalog Variant Admin #########
    path('catalog/variant/', views.AdminCatalogVariantsList, name='AdminCatalogVariantList'),
    path('catalog/variant/update/<slug:slug>/', views.AdminCatalogVariantsUpdate, name='AdminCatalogVariantUpdate'),
    path('catalog/variant/delete/<slug:slug>/', views.AdminCatalogVariantsDelete.as_view(), name='AdminCatalogVariantDelete'),


##########  Catalog Unit Admin #########
    path('catalog/unit/', views.AdminCatalogUnitsList, name='AdminCatalogUnitsList'),
    path('catalog/unit/update/<slug:slug>/', views.AdminCatalogUnitsUpdate, name='AdminCatalogUnitsUpdate'),
    path('catalog/unit/delete/<slug:slug>/', views.AdminCatalogUnitsDelete, name='AdminCatalogUnitsDelete'),

    ##########  Catalog Manufacturer Admin #########
    path('catalog/manufacturer/', views.AdminCatalogManufacturerList, name='AdminCatalogManufacturerList'),
    path('catalog/manufacturer/add/', views.AdminCatalogManufacturerList, name='AdminCatalogManufacturerCreate'),
    path('catalog/manufacturer/update/<slug:slug>/', views.AdminCatalogManufacturerUpdate,
         name='AdminCatalogManufacturerUpdate'),
    path('catalog/manufacturer/delete/<slug:slug>/', views.AdminCatalogManufacturerDelete.as_view(),
         name='AdminCatalogManufacturerDelete'),

    ##########   Catalog Barcode Admin #########
    path('catalog/barcode/', views.AdminCatalogManufacturerList, name='AdminCatalogBarcodeList'),
    path('catalog/barcode/add/', views.AdminCatalogManufacturerList, name='AdminCatalogBarcodeCreate'),
    path('catalog/barcode/detail/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminBarcodeDetail'),
    path('catalog/barcode/update/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminCatalogBarcodeUpdate'),
    path('catalog/barcode/delete/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminCatalogBarcodeDelete'),

    ##########   Catalog Stock Admin #########
    path('catalog/stock/', warehouse.AdminCatalogProductsStockList, name='AdminCatalogProductsStockList'),
    path('catalog/stock/add/', views.AdminCatalogManufacturerList, name='AdminCatalogStockCreate'),
    path('catalog/stock/detail/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminCatalogStockDetail'),
    path('catalog/stock/update/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminCatalogStockUpdate'),
    path('catalog/stock/delete/<slug:slug>/', views.AdminCatalogManufacturerList, name='AdminCatalogStockDelete'),

    # path('category/', views.category_list, title='category_list'),
    # path('category/<int:id>/<slug:slug>/', views.Products_detail, title='Products_detail'),

    # path('FilterAutocomplete/', FilterAutocomplete, title='FilterAutocomplete')

    ########## Catalog Warehouse Admin #########
    path('catlog/warehouse/', warehouse.AdminCatalogWarehouseList, name='AdminCatalogWarehouseList'),
    path('catalog/warehouse/detail/<slug:slug>/', warehouse.AdminCatalogWarehouseUpdate, name='AdminCatalogWarehouseDetail'),
path('catalog/warehouse/update/<slug:slug>/', warehouse.AdminCatalogWarehouseUpdate, name='AdminCatalogWarehouseUpdate'),


    ########## purchase Admin #########
    path('catlog/purchase/', purchase.AdminCatalogPurchaseList, name='AdminCatalogPurchaseList'),
    path('catlog/purchase/add/', purchase.AdminCatalogPurchaseCreate, name='AdminCatalogPurchaseCreate'),
    path('catlog/purchase/update/<slug:slug>/', purchase.AdminCatalogPurchaseUpdate, name='AdminCatalogPurchaseUpdate'),

    ########## invoice Admin #########
    path('catlog/invoice/', purchase.AdminCatalogInvoiceList, name='AdminCatalogInvoiceList'),
    #     path('catlog/invoice/add/', AdminCatalogPurchaseCreate, title='AdminCatalogPurchaseCreate'),
    path('catalog/invoice/detail/<slug:slug>/', purchase.AdminCatalogInvoiceDetails, name='AdminCatalogInvoiceDetails'),
    path('catalog/invoice/pdf/<slug:slug>/', purchase.AdminCatalogInvoicePDF, name='AdminCatalogInvoicePDF'),
    # path('catlog/invoice/update/<slug:slug>/', AdminCatalogPurchaseUpdate, title='AdminCatalogPurchaseUpdate'),

########## Orders Admin #########

    path('orders/', order.OrdersList, name='AdminOrdersList'),
    path('orders/details/<slug:slug>/', order.OrdersDetails, name='AdminOrdersDetails'),

    ########## Refund Admin #########
    path('catlog/refund/', order.RefundList, name='AdminCatalogRefundList'),
    path('refund/details/<slug:slug>/', order.RefundDetails, name='AdminRefundDetails'),
    path('refund/add/', order.RefundAdd, name='AdminRefundAdd'),
    path('api/refund/order/<slug:slug>/', order.getRefundOrder, name='AdminRefundApiOrder'),
    path('api/refund/items/<slug:slug>/', order.getRefundOrderItems, name='AdminRefundApiOrderItems'),
    path('api/refund/item/<int:item_id>/<int:product_id>/', order.RefundOrderItem, name='AdminRefundApiOrderItem'),
    path('api/refund/updateorder/<int:item_id>/', order.RefundUpdateOrder, name='AdminRefundUpdateOrder'),
    path('api/refund/orderitem/', order.refundUpdateOrderItems, name='AdminRefundCurrentOrderItems'),

    ########## POS   #########
    path('catlog/pos/', pos.AdminCatalogPos, name='AdminCatalogPos'),
    path('addition', pos.addition, name='AdminAddition'),  # path('api/pos/', order, title='AdminPosCash'),
    path('pos/stock/', pos.view_stock, name='view_stock'),
    path('catlog/pos/test/', pos.AdminCataloTESTposPAge, name='AdminCataloTESTposPAge'),






]
