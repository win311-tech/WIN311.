from win.models import ContactMessage


def store_contact_message(validated_data, ip_address=None):
    return ContactMessage.objects.create(
        name=validated_data["name"],
        email=validated_data["email"],
        message=validated_data["message"],
        ip_address=ip_address,
    )
