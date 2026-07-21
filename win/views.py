from django.shortcuts import render,redirect
from django.http import JsonResponse
from .forms import ContactForm
from .services.contact_service import store_contact_message


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if not form.is_valid():
            return JsonResponse({
                "status": "errors",
                "errors": form.errors}, status=400)

        ip_address = get_client_ip(request)
        store_contact_message(form.cleaned_data, ip_address)
        return JsonResponse({
            "status": "success",
            "message": "Your message has been received. Thank you!"})

    return render(request,'contact.html',{'form':ContactForm()})



def index(request):
    return render(request,'index.html')






def about(request):
    return render(request,'about.html')



def contact(request):
    return render(request,'contact.html')



def update(request):
    return render(request,'update.html')
