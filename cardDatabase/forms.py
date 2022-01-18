from django import forms

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, Race, AbilityText
from cardDatabase.models.Ability import Keyword
from cardDatabase.management.commands.importjson import remove_punctuation


class SearchForm(forms.Form):
    generic_text = forms.CharField(label='', strip=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Search...'}), required=False)


def get_races():
    try:
        race_values = Race.objects.values('name')
        race_map = map(lambda x : (x['name'], x['name']), race_values)
    except:
        return []

    return list(race_map)


def get_keywords_choices():
    try:
        return [(x.search_string, x.name) for x in Keyword.objects.all().order_by('name')]
    except:
        return []


class AdvancedSearchForm(forms.Form):
    race_values = Race.objects.values('name')
    race_map = map(lambda x : (x['name'], x['name']), race_values)

    generic_text = forms.CharField(label='', strip=True,
                                   widget=forms.TextInput(attrs={'placeholder': 'Search...'}), required=False)
    text_exactness = forms.ChoiceField(label='Search card for:', required=False, choices=CONS.TEXT_EXACTNESS_OPTIONS)
    text_search_fields = forms.MultipleChoiceField(label='Search Card:', choices=CONS.TEXT_SEARCH_FIELD_CHOICES, required=False)
    sort_by = forms.ChoiceField(label='Sort results by:', choices=CONS.DATABASE_SORT_BY_CHOICES, required=False)
    reverse_sort = forms.BooleanField(label='Reverse sorting:', required=False)
    colours = forms.MultipleChoiceField(label='Color(s):', choices=CONS.COLOUR_CHOICES, required=False)
    race = forms.MultipleChoiceField(label='Race(s):', choices=get_races(), required=False)
    sets = forms.MultipleChoiceField(label='Set(s):', choices=CONS.SET_CHOICES, required=False)
    cost = forms.MultipleChoiceField(label='Total Cost(s):', choices=CONS.TOTAL_COST_CHOICES, required=False)
    card_type = forms.MultipleChoiceField(label='Card Type(s):', choices=CONS.DATABASE_CARD_TYPE_CHOICES, required=False)
    rarity = forms.MultipleChoiceField(label='Rarity:', choices=CONS.RARITY_CHOICE_VALUES, required=False)
    divinity = forms.MultipleChoiceField(label='Divinity:', choices=CONS.DIVINITY_CHOICES, required=False)
    atk_value = forms.IntegerField(label='ATK', required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Attack'}))
    atk_comparator = forms.ChoiceField(required=False, choices=CONS.ATK_DEF_COMPARATOR_CHOICES)
    def_value = forms.IntegerField(label='DEF', required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Defense'}))
    def_comparator = forms.ChoiceField(required=False, choices=CONS.ATK_DEF_COMPARATOR_CHOICES)
    keywords = forms.MultipleChoiceField(label='Keyword(s):', choices=get_keywords_choices(), required=False)


class AddCardForm(forms.ModelForm):
    races = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Each race must be separated by a single newline'}))
    ability_texts = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Each ability must be separated by TWO newlines at the end. Single newlines will be counted as part of 1 ability.'}))

    class Meta:
        model = Card
        fields = ['name', 'card_id', 'card_image', 'cost', 'divinity', 'flavour',
                  'rarity', 'ATK', 'DEF', 'types', 'colours']
        widgets = {
            'types': forms.CheckboxSelectMultiple(),
            'cost': forms.TextInput(attrs={'placeholder': 'Each value must be inside {}, GRUWB, T for Time, M for Moon e.g. "{1}{M}{T}{W}{W}", "0" if "0" and blank if no cost '}),
            'card_id': forms.TextInput(attrs={'placeholder': 'e.g. LEL-123'}),
            'card_image': forms.ClearableFileInput(attrs={'required': True}),
            'colours': forms.CheckboxSelectMultiple()
        }

    @classmethod
    def split_abilities(cls, ability_text):
        output = []
        current_ability = ''
        for text in ability_text.splitlines():
            if text:
                current_ability += text + '\n'
            else:  # Two newlines, new ability
                output.append(current_ability)
                current_ability = ''
        output.append(current_ability)
        return output

    def save(self):
        card_instance = super().save(commit=False)
        card_instance.name_without_punctuation = remove_punctuation(card_instance.name)
        # Save model before using it with manytomany relations
        card_instance.save()

        abilities_to_add = AddCardForm.split_abilities(self.cleaned_data['ability_texts'])
        for ability_to_add in abilities_to_add:
            card_instance.ability_texts.add(AbilityText.objects.get_or_create(text=ability_to_add)[0])

        races_to_add = self.cleaned_data['races'].splitlines()
        for race_to_add in races_to_add:
            card_instance.races.add(Race.objects.get_or_create(name=race_to_add)[0])

        for colour_to_add in self.cleaned_data['colours']:
            card_instance.colours.add(colour_to_add)

        return card_instance

