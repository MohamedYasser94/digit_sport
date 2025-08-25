from django.urls import path


from home.views import blog,  contact, views

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


    path("faq", views.FAQ, name="FrontFAQ"),
    path("privacy-policy", views.FrontPrivacyPolicy, name="FrontPrivacyPolicy"),
    path("termsofservice", views.FAQ, name="FrontTermsOfService"),
    path("termsofservice", views.FAQ, name="FrontRequestAQuote"),

    path("test/", views.FrontTestPage, name="FrontTestPage"),



    ########## Blog Front #########
    path('blog/', blog.BlogList, name='FrontBlog'),
    path('blog/<slug:slug>', blog.ArticleDetailFront, name='FrontArticleDetails'),
    path('blog/author/<slug:slug>', blog.AuthorDetailFront, name='FrontArticleAuthorDetails'),
    path('blog/category/<slug:slug>/', blog.ArticleCategoryDetailFront.as_view(), name='FrontArticleCategoryDetails'),
    path('blog/tag/<slug:slug>/', blog.ArticleTagDetailFront.as_view(), name='FrontArticleTagDetails'),



    ########### Error Url ###############

    path('403', views.error403, name='Error403'),

    # path('admin/logout', AdminIndex, title='AdminIndex'),

]
