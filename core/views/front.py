import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, DetailView, DeleteView, UpdateView, ListView

from core.forms.design import BannersAddForm, SliderAddForm, AdminTestimonialsForm
from core.models.core import CommonMediaFiles
from core.models.front import Slider, Banners, Testimonials
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, staff_only, authenticated_staf


####################Testimonials#######################
@authenticated_staf
@staff_only
def AdminTestimonialsList(request):
    testimonials = Testimonials.objects.all()
    if request.method == "POST":
        testimonials_form = AdminTestimonialsForm(request.POST or None, request.FILES or None)
        if testimonials_form.is_valid():
            title = request.POST.get('title')
            description = request.POST.get('description')
            author = request.POST.get('author')
            position = request.POST.get('position')
            image = request.FILES.get('image')
            testimonials_object = Testimonials(title=title, description=description, author=author, position=position, image=image)
            testimonials_object.save()
            messages.success(request, 'Testimonials created successfully', extra_tags='Testimonials')
            return HttpResponseRedirect(reverse_lazy('core:AdminTestimonialsList'))
    else:
       messages.error(request, 'Testimonials not created', extra_tags='Testimonials')


    return render(request, f'{BACKEND_TEMPLATES}/design/testimonials/admin.html', {'testimonials': testimonials})


@authenticated_staf
@staff_only
def AdminTestimonialsDetail(request, slug):
    testimonials = Testimonials.objects.get(slug=slug)
    return render(request, f'{BACKEND_TEMPLATES}/design/testimonials/admin.html', {'testimonials': testimonials})

@authenticated_staf
@staff_only
def  AdminTestimonialsUpdate(request, slug):
    testimonial = Testimonials.objects.get(slug=slug)
    if request.method == "POST":
        testimonials_form = AdminTestimonialsForm(request.POST or None, request.FILES or None, instance=testimonial)
        if testimonials_form.is_valid():
            title = request.POST.get('title')
            description = request.POST.get('description')
            author = request.POST.get('author')
            position = request.POST.get('position')
            image = request.FILES.get('image')
            testimonials_object = Testimonials.objects.get(slug=slug)
            testimonials_object.title = title
            testimonials_object.description = description
            testimonials_object.author = author
            testimonials_object.position = position
            if image == None or image == '':

                testimonials_object.image = testimonial.image
            else:
                testimonials_object.image = image

            testimonials_object.save()
            testimonials_form.save()
            messages.success(request, 'Testimonials updated successfully', extra_tags='Testimonials')
            return HttpResponseRedirect(reverse_lazy('core:AdminTestimonialsList'))
    else:
        messages.error(request, 'Testimonials not updated', extra_tags='Testimonials')
    context =  {

        'testimonial': testimonial,
        'testimonials_form': AdminTestimonialsForm(instance=testimonial),
        'current_page': 'Update',
        'prev_Page': 'Testimonials',
        'prev_url': reverse_lazy('core:AdminTestimonialsList'),

    }

    return render(request, f'{BACKEND_TEMPLATES}/design/testimonials/update.html', context)

@authenticated_staf
@staff_only
def AdminTestimonialsArchive(request, slug):
    testimonials = Testimonials.objects.get(slug=slug)
    if request.method == "POST":
        testimonials.status = 'Archive'
        testimonials.save()
        messages.success(request, 'Testimonials archived successfully', extra_tags='Testimonials')
        return HttpResponseRedirect(reverse_lazy('core:AdminTestimonialsList'))
    else:
        messages.error(request, 'Testimonials not archived', extra_tags='Testimonials')





def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    # print('response', response)
    # print('response.content', response.content)
    #
    # print( request.build_absolute_uri())
    # print( request.build_absolute_uri().split('/')[-2])
    print('content_url', request.get_full_path())

    print('content_url', request.META['HTTP_REFERER'])
    print('actual', request.META['HTTP_REFERER'].split('/')[-2])
    print('content_url', request.META['HTTP_HOST'])
    print('content_url', request.META['HTTP_USER_AGENT'])
    print('content_url', request.META['HTTP_ACCEPT'])
    print('content_url', request.META['HTTP_ACCEPT_LANGUAGE'])
    print('content_url', request.META['HTTP_ACCEPT_ENCODING'])
    print('content_url', request.META['HTTP_COOKIE'])
    print('content_url', request.META['HTTP_CONNECTION'])
    print('content_url', request.META['HTTP_HOST'])
    print('content_url', request.META['HTTP_ORIGIN'])
    print('content_url', request.META['HTTP_REFERER'])
    print('content_url', request.META['HTTP_USER_AGENT'])

    format = request.POST.get('format')
    # print('format', format)
    model = request.META['HTTP_REFERER'].split('/')[-2]
    model_info = ContentType.objects.filter(app_label='core', model=model)
    model = model_info.first().model_class()
    # print('model_info', model)

    writer = csv.writer(response)
    writer.writerow([f.title for f in model._meta.get_fields()])
    testimonials = model.objects.all()
    for testimonial in testimonials:
        writer.writerow([testimonial.__getattribute__(f.title) for f in model._meta.get_fields()])


    return response


#################### Slider ###################

class SliderView(TemplateView):
    template_name = "../template/../templates/good/design/slider/admin.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sliders'] = Slider.objects.all()
        return context

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(SliderView, self).dispatch(*args, **kwargs)


class SliderDetailView(DetailView):
    model = Slider
    context_object_name = 'slider'
    template_name = '../template/../templates/good/design/slider/site.html'

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(SliderDetailView, self).dispatch(*args, **kwargs)


class SliderDelete(DeleteView):
    model = Slider
    fields = '__all__'
    success_url = reverse_lazy('core:AdminSlider')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(SliderDelete, self).dispatch(*args, **kwargs)


class SliderCreate(View):
    def get(self, request, *args, **kwargs):
        slider = Slider.objects.all()

        return render(request, "../template/../templates/good/design/slider/add.html",
                      {"groups": slider, })

   

    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        group = request.POST.get("group")
        status = request.POST.get("status")
        sort_order = request.POST.get("sort_order")
        media_type_list = request.POST.getlist("media_type[]")
        images = request.FILES.getlist("images")
        media_link_list = request.POST.getlist("media_link[]")

       

        # status = request.POST.get("status")

        slider = Slider(title=title, group=group, status=status, sort_order=sort_order,
                        )
        slider.save()

        i = 0
        for image in images:

            slider_image = CommonMediaFiles(image=image, type='hero',
                                        owner_model=ContentType.objects.get(model='Slider'),
                                        owner_id=slider.id)

            slider_image.save()
            i = i + 1

        # return HttpResponse("OK")
        return HttpResponseRedirect(reverse_lazy('core:AdminSliderView'))

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(SliderCreate, self).dispatch(*args, **kwargs)


class SliderEdit(UpdateView):
    model = Slider
    form_class = SliderAddForm
    template_name = '../template/../templates/good/design/slider/site.html'
    success_url = reverse_lazy('core:AdminSliderView')

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(SliderEdit, self).dispatch(*args, **kwargs)


###################Banners#############

class BannersView(ListView):
    model = Banners
    template_name = "../template/../templates/good/design/banner/admin.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(BannersView, self).dispatch(*args, **kwargs)


class BannerDetailView(DetailView):
    model = Banners
    context_object_name = 'design'
    template_name = '../template/../templates/good/design/banner/details.html'

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(BannerDetailView, self).dispatch(*args, **kwargs)


class BannerDelete(DeleteView):
    model = Banners
    fields = '__all__'
    success_url = reverse_lazy('core:AdminBanner')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(BannerDelete, self).dispatch(*args, **kwargs)


@login_required(login_url='/dashboard/login')
@superuser_only
def BannerCreate(request):  # sourcery skip: aug-assign, convert-to-enumerate

    if request.method == "POST":
       

        banner_form = BannersAddForm(request.POST or None, request.FILES or None)

        if banner_form.is_valid():
            return _extracted_from_BannerCreate_10(request, banner_form)
      
       
        messages.error(request, "Error")

    else:
        banner_form = BannersAddForm()
    # return redirect(reverse('core:ProductAdd'))

    return render(request, '../template/../templates/good/design/banner/add.html',
                  {'banner_form': banner_form, }
                  )


def _extracted_from_BannerCreate_10(request, banner_form):
   
    product_created = True
    position = banner_form.cleaned_data['position']
    status = banner_form.cleaned_data['status']

    media_content = banner_form.cleaned_data['media_content']
    media_link = banner_form.cleaned_data['media_link']

    banner_form = None
    if not banner_form:
       
       

        banner_form = Banners(position=position, status=status,
                              media_content=media_content, media_link=media_link,
                              )

        banner_form.save()

       
        # use django messages framework
    messages.success(request,
                     "Yeeew, check it out on the home page!")

    return HttpResponseRedirect(reverse_lazy('core:AdminBannerView'))


class BannerEdit(UpdateView):
    model = Banners
    form_class = BannersAddForm
    template_name = '../template/../templates/good/design/banner/site.html'
    success_url = reverse_lazy('core:AdminBannerView')

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(BannerEdit, self).dispatch(*args, **kwargs)



