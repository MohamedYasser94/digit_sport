from django.urls import path

from core.views.payment_gateway.fawry_payment import PaymentFawry
from core.views.payment_gateway.paymob import PaymentMyPaymob
from core.views.payment_gateway.stripe import PaymentStripe
from home.views import blog, catalog, contact, services, shop, views, payment

app_name = 'home'

urlpatterns = [

    path('', views.HomeIndex, name='HomeIndex'),
    path("about/", contact.FrontAbout, name="FrontAbout"),
    path("contact/", contact.ContactFront, name="FrontContact"),
    path("contactform/", contact.FrontContactForm, name="FrontContactForm"),
    path("sendnumber/", contact.FrontSendPhoneForm, name="FrontSendPhoneForm"),
    path("contactform/message_sent", contact.contact_view, name="MessageSent"),
    path("newsletter/", contact.FrontNewsletterSubscriber, name="FrontNewsletterSubscriber"),
    path("vision/", contact.FrontOurVision, name="FrontOurVision"),
    path("portfolio/", contact.FrontOurPortfolio, name="FrontOurPortfolio"),

    path("team/", views.TheTeamFront, name="FrontTeamList"),
    path("team/<slug:slug>/", views.FrontTheTeamDetails, name="FrontTeamDetails"),
    path("faq", views.FAQ, name="FrontFAQ"),
    path("privacy-policy", views.FrontPrivacyPolicy, name="FrontPrivacyPolicy"),
    path("termsofservice", views.FAQ, name="FrontTermsOfService"),
    path("termsofservice", views.FAQ, name="FrontRequestAQuote"),

    path("test/", views.FrontTestPage, name="FrontTestPage"),

    ########## Services Front #########
    path('services/', services.FrontService, name='FrontServices'),
    path('services/<slug:slug>/', services.front_service_detail, name='FrontDetailsServices'),
    path("work", services.front_work, name="FrontOurWork"),
    path('work/<slug:slug>/', services.front_work_detail, name='FrontWorksDetails'),
    path("package", services.front_package, name="FrontPackage"),
    path('product/', services.front_product, name='FrontProducts'),
    path('product/<slug:slug>', services.front_product_detail, name='FrontProductDetails'),
    path('portfolio/', services.front_portfolio, name='FrontPortfolio'),
    path('portfolio/<slug:slug>/', services.front_portfolio_detail, name='FrontDetailsPortfolio'),
    path('appointment/', services.FrontBookAppointment, name='FrontBookAppointment'),

    ########## Blog Front #########
    path('blog/', blog.BlogList, name='FrontBlog'),
    path('blog/<slug:slug>', blog.ArticleDetailFront, name='FrontArticleDetails'),
    path('blog/author/<slug:slug>', blog.AuthorDetailFront, name='FrontArticleAuthorDetails'),
    path('blog/category/<slug:slug>/', blog.ArticleCategoryDetailFront.as_view(), name='FrontArticleCategoryDetails'),
    path('blog/tag/<slug:slug>/', blog.ArticleTagDetailFront.as_view(), name='FrontArticleTagDetails'),

    ########## Category Front #########

    path('category/', catalog.FrontCatagoriesList, name='FrontCategories'),
    path('category/<slug:slug>/', catalog.CategoryDetails, name='FrontDetailsCategory'),
    path('blog/<slug:slug>/', blog.ArticleDetailFront, name='FrontArticleDetails'),
    path('blog/<slug:slug>/<int:y>/<int:m>/<int:d>/', blog.ArticleDetailFront, name='FrontArticleWithTimeDetails'),
    path('blog/category/<slug:slug>/', blog.ArticleCategoryDetailFront.as_view(), name='FrontArticleCategoryDetails'),
    path('blog/tag/<slug:slug>/', blog.ArticleTagDetailFront.as_view(), name='FrontArticleTagDetails'),

    ########## Product Front #########
    path('category/product/<slug:slug>/', catalog.ProductDetails, name='FrontDetailsProduct'),
    path('category/product/image/<int:id>/', catalog.ProductImageDetails, name='FrontDetailsProductImage'),

    ########## Order Front #########

    path('cart/add/<int:id>', shop.AddToCart, name='FrontProductAddToCart'),
    path('cart/', shop.CartDetails, name='CartDetails'), path('cart', shop.updateCartItem, name='AjaxUpdateItem'),
    # <-- this one here
    path('checkout/', shop.Checkout, name='Checkout'),
    path('checkout', shop.ShippingOrderCalculate, name='AjaxShippingOrderCalculate'),  # <-- this one here

    ##############wishlist#####################
    path('wishlist/', shop.WishlistView, name="Wishlist"), path('addwishlist/', shop.addWishlist, name="AddWishlist"),
    path('deletefromwishlist/<int:id>', shop.deletefromWishlist, name='DeleteFromWishlist'),

    ##############Payment#####################
    path('payment/<payment_option>/', shop.PaymentView.as_view(), name='payment'),
    path('PaymentStripe/', PaymentStripe.as_view(), name='PaymentStripe'),
    path('PaymentMyPaymob/', PaymentMyPaymob.as_view(), name='PaymentMyPaymob'),
    path('PaymentFawry/', PaymentFawry.as_view(), name='PaymentFawry'),

    path('api/checkout-session/', payment.create_checkout_session.as_view(), name='OrderStripe'),
    path('api/webhookstripe/', payment.my_webhook_view, name='WebhookStripe'),
    path('cart/success/', payment.PaymentSuccess, name='PaymentSuccess'),
    path('failed/', payment.PaymentFailedView.as_view(), name='PaymentFailed'),
    path('history/', payment.OrderHistoryListView.as_view(), name='history'),
    path('create-payment-intent/<pk>/', payment.StripeIntentView.as_view(), name='create-payment-intent'),
    path('webhooks/stripe/', payment.stripe_webhook, name='stripe-webhook'),
    path('cancel/', payment.CancelView.as_view(), name='cancel'),
    path('success/', payment.SuccessView.as_view(), name='success'),
    path('create-checkout-session/<pk>/', payment.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),

    ########### Error Url ###############

    path('403', views.error403, name='Error403'),

    # path('admin/logout', AdminIndex, title='AdminIndex'),

]
