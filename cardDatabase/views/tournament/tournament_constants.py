FIELD_TYPE_TEXT = 'text'
FIELD_TYPE_LINK = 'link'
FIELD_TYPE_EMAIL = 'email'
FIELD_TYPE_TEXTAREA = 'textarea'
FIELD_TYPE_YEAR = 'year'

TOURNAMENT_DEFAULT_META_DATA = [
    {
        'name': 'location',
        'label': 'Location',
        'required': True,
        'type': FIELD_TYPE_TEXTAREA,
        'maxlength': 500,
        'class': 'form-control'
    },
    {
        'name': 'fee',
        'label': 'Tournament Fee',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'prices',
        'label': 'Prices',
        'required': True,
        'type': FIELD_TYPE_TEXTAREA,
        'maxlength': 500,
        'class': 'form-control'
    },
    {
        'name': 'prices-link',
        'label': 'Prices Link',
        'required': False,
        'type': FIELD_TYPE_LINK,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'additional',
        'label': 'Additional Information',
        'required': False,
        'type': FIELD_TYPE_TEXTAREA,
        'maxlength': 500,
        'class': 'form-control'
    }
]

ONLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA = [
    {
        'name': 'firstname',
        'label': 'Firstname',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'lastname',
        'label': 'Lastname',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'email',
        'label': 'Email',
        'required': True,
        'type': FIELD_TYPE_EMAIL,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'username',
        'label': 'Online Username',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'additional',
        'label': 'Additional Information',
        'required': False,
        'type': FIELD_TYPE_TEXTAREA,
        'maxlength': 500,
        'class': 'form-control'
    }
]

OFFLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA = [
    {
        'name': 'firstname',
        'label': 'Firstname',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'lastname',
        'label': 'Lastname',
        'required': True,
        'type': FIELD_TYPE_TEXT,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'email',
        'label': 'Email',
        'required': True,
        'type': FIELD_TYPE_EMAIL,
        'maxlength': 200,
        'class': 'form-control'
    },
    {
        'name': 'birth-year',
        'label': 'Birth Year',
        'required': True,
        'type': FIELD_TYPE_YEAR,
        'maxlength': 4,
        'class': 'form-control'
    },
    {
        'name': 'additional',
        'label': 'Additional Information',
        'required': False,
        'type': FIELD_TYPE_TEXTAREA,
        'maxlength': 500,
        'class': 'form-control'
    }
]