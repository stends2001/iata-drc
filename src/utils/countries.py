countries_highglighted = [
    'burundi',
    'drc',
    'south_sudan',
    'rwanda',
    'uganda'    
    ]

countries_background = [
    'angola',
    'cameroon',
    'caf',
    'chad',
    'congo',
    'ethiopia',
    'gabon',
    'kenya',
    'malawi',
    'mozambique',
    'nigeria',
    'sudan',
    'tanzania',
    'zambia',
    'zimbabwe',
    ]


countrycodes_dict = {
    # highlight
    'drc'           : 'cod',
    'south_sudan'   : 'ssd',
    'uganda'        : 'uga',
    'burundi'       : 'bdi',        
    'rwanda'        : 'rwa',  

    # background
    'angola'        : 'ago',
    'cameroon'      : 'cmr',
    'chad'          : 'tcd',
    'caf'           : 'caf',
    'congo'         : 'cog',
    'ethiopia'      : 'eth',
    'gabon'         : 'gab',
    'kenya'         : 'ken',
    'malawi'        : 'mwi',
    'mozambique'    : 'moz',
    'nigeria'       : 'nga',
    'sudan'         : 'sdn',
    'tanzania'      : 'tza',
    'zambia'        : 'zmb',
    'zimbabwe'      : 'zwe'
}

capital_mappings = {
    'democratic republic of the congo'    : 'drc',
    'south sudan'                         : 'south_sudan',
    'central african republic'            : 'caf',
    'united republic of tanzania'         : 'tanzania'    
}

european_countries_hl = [
    'Belgium',
    'France',
    'Germany',
    'Italy',
    'Spain',
]

european_countries = [
    'Austria',
    'Belgium',
    'Bulgaria',
    'Croatia',
    'Cyprus',
    'Czechia',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hungary',
    'Iceland',
    'Ireland',
    'Italy',
    'Latvia',
    'Lithuania',
    'Luxembourg',
    'Malta',
    'Netherlands',
    'Norway',
    'Poland',
    'Portugal',
    'Romania',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'Switzerland',
]

countries_by_continent = {}
for cont, names in {
    'Neighboring countries': ['uganda', 'rwanda', 'burundi', 'south_sudan', 'Central African Republic', 'congo', 'Angola','Zambia','Tanzania United Republic of'],
    'Africa (other)': ['Algeria', 'Cameroon', 'Comoros', "Cote d'Ivoire", 'Egypt', 'Ethiopia', 'Ghana', 'Kenya',
        'Madagascar', 'Malawi', 'Mauritius', 'Morocco', 'Nigeria', 'Senegal', 'South Africa',
        'Togo', 'Tunisia', 'Zimbabwe',  'Benin', 'Botswana',
        'Burkina Faso', 'Cape Verde', 'Chad', 'Djibouti', 'Equatorial Guinea',
        'Eritrea', 'Eswatini', 'Gabon', 'Gambia', 'Guinea', 'Guinea-Bissau', 'Lesotho', 'Liberia',
        'Libyan Arab Jamahiriya', 'Mali', 'Mauretania', 'Mayotte', 'Mozambique', 'Namibia', 'Niger', 'Reunion',
        'Seychelles', 'Sierra Leone', 'Somalia', 'Sudan', 'Sao Tome and Principe'],
    'Europe': ['Austria', 'Belarus', 'Belgium', 'Cyprus', 'Czechia', 'Denmark', 'Finland', 'France', 'Germany',
        'Greece', 'Hungary', 'Ireland', 'Italy', 'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal',
        'Russian Federation', 'Serbia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom', 'Albania',
        'Bulgaria', 'Croatia', 'Estonia', 'Iceland', 'Isle of Man', 'Jersey', 'Latvia', 'Lithuania', 'Luxembourg',
        'Moldova Republic of', 'Republic of North Macedonia', 'Romania', 'Bosnia and Herzegovina', 'Montenegro',
        'Svalbard & Jan Mayen Island', 'Aland Islands', 'Faroe Islands', 'Guernsey', 'Slovakia', 'Gibraltar'],
    'Middle East & Türkiye': ['Iran', 'Iraq', 'Israel', 'Jordan', 'Lebanon', 'Oman', 'Qatar', 'Saudi Arabia',
        'United Arab Emirates', 'Bahrain', 'Kuwait', 'Syrian Arab Republic', 'Yemen Republic of', 'Turkiye'],
    'Asia': ['China', 'Hong Kong (SAR) China', 'India', 'Indonesia', 'Japan', 'Korea Republic of', 'Malaysia',
        'Pakistan', 'Philippines', 'Singapore', 'Sri Lanka', 'Tajikistan', 'Thailand', 'Viet Nam', 'Afghanistan',
        'Armenia', 'Azerbaijan', 'Bangladesh', 'Cambodia', 'Chinese Taipei', 'Georgia', 'Kazakhstan', 'Kyrgyzstan',
        "Lao People's Democratic Republic", 'Maldives', 'Mongolia', 'Myanmar', 'Nepal', 'Turkmenistan',
        'Uzbekistan', 'Timor-Leste', 'Bhutan', 'Brunei Darussalam', 'Macao (SAR) China'],
    'Americas': ['Brazil', 'Canada', 'Colombia', 'Panama', 'UNITED STATES OF AMERICA', 'Argentina', 'Barbados',
        'Bermuda', 'Bolivia', 'Bonaire Sint Eustatius and Saba', 'Chile', 'Costa Rica', 'Cuba', 'Dominican Republic',
        'El Salvador', 'Grenada', 'Guatemala', 'Guyana', 'Honduras', 'Jamaica', 'Mexico', 'Peru', 'Puerto Rico',
        'Sint Maarten', 'Suriname', 'Trinidad and Tobago', 'Virgin Islands U.S.', 'Aruba', 'French Guyana',
        'Saint Lucia', 'Venezuela', 'Paraguay', 'Uruguay', 'Ecuador', 'Bahamas', 'Cayman Islands', 'Martinique',
        'Guadeloupe', 'Antigua and Barbuda', 'Nicaragua', 'Turks and Caicos Islands', 'Curacao', 'Belize',
        'Dominica', 'Saint Kitts and Nevis', 'Virgin Islands British'],
    'Oceania': ['Australia', 'New Zealand', 'Fiji', 'Papua New Guinea', 'French Polynesia', 'Solomon Islands',
        'Tonga', 'New Caledonia', 'Cook Islands', 'Vanuatu', 'Samoa', 'Palau'],
}.items():
    countries_by_continent.update({n: cont for n in names})

continent_colors = {'Neighboring countries' : '#e87ba4', 
                  'Africa (other)'          : '#eda100', 
                  'Europe'                  : '#2a78d6',
                  'Middle East & Türkiye'   : '#eb6834', 
                  'Asia'                    : '#1baf7a', 
                  'Americas'                : '#4a3aa7',
                  'Oceania'                 : '#008300', 
                  'other/unknown'           : '#c3c2b7'}
