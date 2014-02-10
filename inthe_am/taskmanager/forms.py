from django import forms


class TaskdConfigurationForm(forms.Form):
    certificate = forms.CharField()
    key = forms.CharField()
    ca = forms.CharField(required=False)
    trust = forms.ChoiceField(
        choices=(
            ('no', 'Do not trust'),
            ('yes', 'Trust'),
        )
    )

    server = forms.CharField(max_length=255)
    credentials = forms.RegexField(
        max_length=255,
        regex='[^/]+/[^/]+/[^/]'
    )
