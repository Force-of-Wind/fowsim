from django import forms


class SearchForm(forms.Form):
    generic_text = forms.CharField(label='', strip=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Search for cards here...'}))


TEXT_SEARCH_FIELD_CHOICES = [
    ('name', 'Name'),
    ('races__name', 'Race/Trait'),
    ('ability_texts__text', 'Abilities')
]


class AdvancedSearchForm(SearchForm):
    text_search_fields = forms.MultipleChoiceField(label='Search Card:', choices=TEXT_SEARCH_FIELD_CHOICES, widget=forms.CheckboxSelectMultiple)
