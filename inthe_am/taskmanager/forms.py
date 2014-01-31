from django import forms


class TaskdConfigurationForm(forms.Form):
    certificate = forms.FileField()
    key = forms.FileField()
    ca = forms.FileField()

    server = forms.CharField(max_length=255)
    credentials = forms.RegexField(
        max_length=255,
        regex='[^/]+/[^/]+/[^/]'
    )
