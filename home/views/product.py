from django.shortcuts import render
from django.views.generic import ListView
from core.models.blog import BlogServices
from home.views.views import FRONTEND_TEMPLATES


def test(request):
    return render(request, f'{FRONTEND_TEMPLATES}/product/product-details.html', )


##########################      Services Admin            ################################
class ServicesList(ListView):
    model = BlogServices
    template_name = f'{FRONTEND_TEMPLATES}/product/product-details.html'



