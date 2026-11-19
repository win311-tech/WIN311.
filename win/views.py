from django.shortcuts import redirect, render

from .forms import ContactForm
from .services.contact_service import submit_contact_message


def get_client_ip(request):
    return request.META.get('REMOTE_ADDR')


def index(request):
    return render(request, 'index.html')


def systems(request):
    return render(request, 'systems.html')


def services(request):
    return render(request, 'services.html')






def about(request):
    return render(request, 'about.html')


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            result = submit_contact_message(
                form.cleaned_data,
                ip_address=get_client_ip(request),
                request=request,
            )
            if result.delivered:
                request.session["contact_enquiry_sent"] = True
                return redirect("contact")

            form.add_error(
                None,
                "Your enquiry was saved, but we couldn't send it just now. "
                "Please try again later or email us directly.",
            )
            return render(request, "contact.html", {"form": form})
    else:
        form = ContactForm()

    sent = request.session.pop("contact_enquiry_sent", False)
    return render(request, "contact.html", {"form": form, "sent": sent})



def update(request):
    return render(request, 'update.html')
