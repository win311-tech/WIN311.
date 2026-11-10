from win.models import ContactMessage


def store_contact_message(validated_data, ip_address=None):
    return ContactMessage.objects.create(
        name=validated_data["name"],
        email=validated_data["email"],
        organisation=validated_data.get("organisation", ""),
        division=validated_data.get("division", "general"),
        category=validated_data.get("category", ""),
        message=validated_data["message"],
        ip_address=ip_address,
    )
