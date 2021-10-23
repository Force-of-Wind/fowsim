from django import forms

from fowsim import constants as CONS


class SearchForm(forms.Form):
    generic_text = forms.CharField(label='', strip=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Search...'}))


class AdvancedSearchForm(forms.Form):
    generic_text = forms.CharField(label='', strip=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Search...'}), required=False)
    text_exactness = forms.ChoiceField(label='Search card for:', required=False, choices=CONS.TEXT_EXACTNESS_OPTIONS)
    text_search_fields = forms.MultipleChoiceField(label='Search Card:', choices=CONS.TEXT_SEARCH_FIELD_CHOICES, required=False)
    colours = forms.MultipleChoiceField(label='Color(s):', choices=CONS.COLOUR_CHOICES, required=False)
    sets = forms.MultipleChoiceField(label='Set(s):', choices=CONS.SET_CHOICES, required=False)
    cost = forms.MultipleChoiceField(label='Total Cost(s):', choices=CONS.TOTAL_COST_CHOICES, required=False)
    card_type = forms.MultipleChoiceField(label='Card Type(s):', choices=CONS.DATABASE_CARD_TYPE_CHOICES, required=False)
    rarity = forms.MultipleChoiceField(label='Rarity:', choices=CONS.RARITY_CHOICE_VALUES, required=False)
    divinity = forms.MultipleChoiceField(label='Divinity:', choices=CONS.DIVINITY_CHOICES, required=False)
    atk_value = forms.IntegerField(label='ATK', required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Attack'}))
    atk_comparator = forms.ChoiceField(required=False, choices=CONS.ATK_DEF_COMPARATOR_CHOICES)
    def_value = forms.IntegerField(label='DEF', required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Defense'}))
    def_comparator = forms.ChoiceField(required=False, choices=CONS.ATK_DEF_COMPARATOR_CHOICES)