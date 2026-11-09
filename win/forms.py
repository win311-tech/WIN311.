from django import forms

SERVICE_CATEGORIES = (
    ('Web Development', 'Web Development'),
    ('Networking', 'Networking'),
    ('System Designs and Architecture', 'System Designs and Architecture'),
    ('IT Training', 'IT Training'),
    ('IP Camera Installations', 'IP Camera Installations'),
    ('IT Monitoring', 'IT Monitoring'),
    ('Database Management', 'Database Management'),
    ('Project Management', 'Project Management'),
)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    organisation = forms.CharField(max_length=180, required=False)
    division = forms.ChoiceField(choices=(('systems', 'WIN311 Systems'), ('services', 'WIN311 Services'), ('general', 'General enquiry')))
    category = forms.ChoiceField(choices=(('', 'Choose a service (optional)'),) + SERVICE_CATEGORIES, required=False)
    message = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('division') != 'services':
            cleaned_data['category'] = ''
        return cleaned_data
