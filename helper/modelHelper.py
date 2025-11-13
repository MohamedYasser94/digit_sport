from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

######################## Regex ###############
Alphanumeric_Regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
Number_Regex = '^[0-9]$'
Password_Regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]+$'

Email_Validator = RegexValidator(EMAIL_REGEX, _('Enter a valid email address.'))
Number_Validator = RegexValidator(Number_Regex, _('Only Number  are allowed.'))
Alphanumeric_Validator = RegexValidator(Alphanumeric_Regex, _('Only alphanumeric characters are allowed.'))
Password_Validator = RegexValidator(Password_Regex, _('password must contain are allowed.'))
######################## Months ###############
Months_Helper = (
    ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
    ('10', '10'), ('11', '11'), ('12', '12'))
DurationUnit = (('Hours', _('Hours')), ('Minutes', _('Minutes')), ('None', 'None'),)
DurationTime = ((10, 10), (15, 15), (30, 30), (60, 60),)
WorkingDay = (('Saturday', _('Saturday')), ('Sunday', _('Sunday')), ('Monday', _('Monday')), ('Tuesday', _('Tuesday')),
              ('Wednesday', _('Wednesday')), ('Thursday', _('Thursday')), ('Friday', _('Friday')),)
# DayType = (('Morning', _('Morning')), ('Evening', _('Evening')), ('All', _('All Day')),('Holiday', _('Holiday')),)
TimeSlotType = (('Morning', _('Morning')), ('Evening', _('Evening')), ('All', _('All Day')), ('Holiday', _('Holiday')))
######################## Status ###############
Soft_Delete = ((True, "Soft Deleted"), (False, "Not Deleted"))
Genesis_Block = ((True, "Is a Genesis Block."), (False, "Is not a Genesis Block."),)
Notice_Status = ((True, "Send Notice Now"), (False, "Don't Send Notice Now"),)
Importance_Status = ((1, "Critical"), (2, "Very Important"), (3, "Important"))
Active_Status = (('Active', _('Active')), ('Archive', _('Archive')), ('Inactive', _('Inactive')),)
Waiting_Status = (('Active', _('Active')), ('Waiting', _('Waiting for activation')), ('Inactive', _('Inactive')),)
Public_Status = (('Yes', _('Yes')), ('NO', _('NO')),)
Publish_Status = (('Published', _('Published')), ('Scheduled', _('Scheduled')), ('Draft', _('Draft')),)
WALLET_STATUS = (('Create', _('Create')), ('Login', _('Login')), ('Logout', _('Logout')), ('Suspend', _('Suspend')),)
Signin_Type = (('NeedActive', _('Need Active')), ('NotNeedActive', _('Not Need Active')), ('Paid', _('Paid')))
AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'twitter': 'twitter', 'email': 'email'}
Social_Providers = (
    ('facebook', 'facebook'), ('twitter', 'twitter'), ('instagram', 'instagram'), ('linkedIn ', 'linkedIn'),
    ('behance ', 'behance'), ('youtube ', 'youtube'), ('other ', 'other'),)
Friend_Request_Status = (
('NOREQUEST', 'NOREQUEST'), ('SENT', 'SENT'), ('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'), ('DECLINE', 'DECLINE'))
Follower_Type = (('FOLLOWER', _('FOLLOWER')), ('FOLLOWING', _('FOLLOWING')))
Otp_Type = (
    ('App', _("App")), ('Email', _("Email")), ('WhatsApp', _("WhatsApp")), ('SMS', _("SMS")), ('None', _("None")),)

Email_Type = (('Personal', _('Personal')), ('Work', _('Work')), ('Other', _('Other')))
Email_status = (
    ('Read', _('Read')), ('Unread', _('Unread')), ('Archive', _('Archive')), ('Trash', _('Trash')), ('Spam', _('Spam')),
    ('Important', _('Important')), ('Starred', _('Starred')), ('Draft', _('Draft')), ('Sent', _('Sent')),
    ('Scheduled', _('Scheduled')), ('Inactive', _('Inactive')),)
Attendees_History_Type = (
('CheckIn', _('CheckIn')), ('CheckOut', _('CheckOut')), ('Break', _('Break')), ('Leave', _('Leave')),
('Absent', _('Absent')), ('Early', _('Early')), ('NotChecked', _('Not Checked')))
################### FRONTEND TEMPLATES #############################
BACKEND_TEMPLATES = (('good', 'good'), ('multikart', 'multikart'), ('kundol', 'kundol'),)
MAINTENANCE_TEMPLATES = (('creasoon', 'creasoon'), ('marvio', 'marvio'), ('landio', 'landio'),)
FRONTEND_TEMPLATES = (
    ('arino', 'arino'), ('via', 'via'), ('opal', 'opal'), ('particle', 'particle'), ('landio', 'landio'),
    ('adara', 'adara'), ('multikart', 'multikart'), ('kundol', 'kundol'), ('techy', 'techy'), ('podes', 'podes'),
    ('centrix ', 'centrix'), ('kons', 'kons'), ('record', 'record'), ('rexlaw', 'rexlaw'), ('mintech', 'mintech'),
    ('volna', 'volna'), ('carenow', 'carenow'), ('medin', 'medin'), ('medikal', 'medikal'), ('dentisto', 'dentisto'),
    ('doccure', 'doccure'), ('creasoon', 'creasoon'), ('marvio', 'marvio'), ('exhibiz', 'exhibiz'),
    ('exvent', 'exvent'), ('soccer', 'soccer'))

Home_Index = (('Home', 'Home'), ('Home2', 'Home2'), ('Home3', 'Home3'), ('Home4', 'Home4'), ('Home5', 'Home5'),)

############### Country List ###############

Continents_List = (
('Africa', _('Africa')), ('Antarctica', _('Antarctica')), ('Asia', _('Asia')), ('Australia', _('Australia')),
('Europe', _('Europe')), ('North America', _('North America')), ('South America', _('South America')),)

Country_List = (('Afghanistan', _('Afghanistan')), ('Albania', _('Albania')), ('Algeria', _('Algeria')),
                ('American Samoa', _('American Samoa')), ('Andorra', _('Andorra')), ('Angola', _('Angola')),
                ('Anguilla', _('Anguilla')), ('Antarctica', _('Antarctica')),
                ('Antigua and Barbuda', _('Antigua and Barbuda')), ('Argentina', _('Argentina')),
                ('Armenia', _('Armenia')), ('Aruba', _('Aruba')), ('Australia', _('Australia')),
                ('Austria', _('Austria')), ('Azerbaijan', _('Azerbaijan')), ('Bahamas', _('Bahamas')),
                ('Bahrain', _('Bahrain')), ('Bangladesh', _('Bangladesh')), ('Barbados', _('Barbados')),
                ('Belarus', _('Belarus')), ('Belgium', _('Belgium')), ('Belize', _('Belize')), ('Benin', _('Benin')),
                ('Bermuda', _('Bermuda')), ('Bhutan', _('Bhutan')), ('Bolivia', _('Bolivia')),
                ('Bosnia and Herzegovina', _('Bosnia and Herzegovina')), ('Botswana', _('Botswana')),
                ('Bouvet Island', _('Bouvet Island')), ('Brazil', _('Brazil')),
                ('British Indian Ocean Territory', _('British Indian Ocean Territory')),
                ('Brunei Darussalam', _('Brunei Darussalam')), ('Bulgaria', _('Bulgaria')),
                ('Burkina Faso', _('Burkina Faso')), ('Burundi', _('Burundi')), ('Cambodia', _('Cambodia')),
                ('Cameroon', _('Cameroon')), ('Canada', _('Canada')), ('Cape Verde', _('Cape Verde')),
                ('Cayman Islands', _('Cayman Islands')), ('Central African Republic', _('Central African Republic')),
                ('Chad', _('Chad')), ('Chile', _('Chile')), ('China', _('China')),
                ('Christmas Island', _('Christmas Island')), ('Cocos (Keeling) Islands', _('Cocos (Keeling) Islands')),
                ('Colombia', _('Colombia')), ('Comoros', _('Comoros')), ('Congo', _('Congo')),
                ('Congo, The Democratic Republic of The', _('Congo, The Democratic Republic of The')),
                ('Cook Islands', _('Cook Islands')), ('Costa Rica', _('Costa Rica')),
                ('Cote Divoire', _('Cote Divoire')), ('Croatia', _('Croatia')), ('Cuba', _('Cuba')),
                ('Cyprus', _('Cyprus')), ('Czech Republic', _('Czech Republic')), ('Denmark', _('Denmark')),
                ('Djibouti', _('Djibouti')), ('Dominica', _('Dominica')),
                ('Dominican Republic', _('Dominican Republic')), ('Ecuador', _('Ecuador')), ('Egypt', _('Egypt')),
                ('El Salvador', _('El Salvador')), ('Equatorial Guinea', _('Equatorial Guinea')),
                ('Eritrea', _('Eritrea')), ('Estonia', _('Estonia')), ('Ethiopia', _('Ethiopia')),
                ('Falkland Islands (Malvinas)', _('Falkland Islands (Malvinas)')),
                ('Faroe Islands', _('Faroe Islands')), ('Fiji', _('Fiji')), ('Finland', _('Finland')),
                ('France', _('France')), ('French Guiana', _('French Guiana')),
                ('French Polynesia', _('French Polynesia')),
                ('French Southern Territories', _('French Southern Territories')), ('Gabon', _('Gabon')),
                ('Gambia', _('Gambia')), ('Georgia', _('Georgia')), ('Germany', _('Germany')), ('Ghana', _('Ghana')),
                ('Gibraltar', _('Gibraltar')), ('Greece', _('Greece')), ('Greenland', _('Greenland')),
                ('Grenada', _('Grenada')), ('Guadeloupe', _('Guadeloupe')), ('Guam', _('Guam')),
                ('Guatemala', _('Guatemala')), ('Guinea', _('Guinea')), ('Guinea-bissau', _('Guinea-bissau')),
                ('Guyana', _('Guyana')), ('Haiti', _('Haiti')),
                ('Heard Island and Mcdonald Islands', _('Heard Island and Mcdonald Islands')),
                ('Holy See (Vatican City State)', _('Holy See (Vatican City State)')), ('Honduras', _('Honduras')),
                ('Hong Kong', _('Hong Kong')), ('Hungary', _('Hungary')), ('Iceland', _('Iceland')),
                ('India', _('India')), ('Indonesia', _('Indonesia')),
                ('Iran, Islamic Republic of', _('Iran, Islamic Republic of')), ('Iraq', _('Iraq')),
                ('Ireland', _('Ireland')), ('Italy', _('Italy')), ('Jamaica', _('Jamaica')), ('Ireland', _('Ireland')),
                ('Japan', _('Japan')), ('Jordan', _('Jordan')), ('Kazakhstan', _('Kazakhstan')), ('Kenya', _('Kenya')),
                ('Kiribati', _('Kiribati')),
                ('Korea, Democratic Peoples Republic of', _('Korea, Democratic Peoples Republic of')),
                ('Korea, Republic of', _('Korea, Republic of')), ('Kuwait', _('Kuwait')),
                ('Kyrgyzstan', _('Kyrgyzstan')),
                ('Lao Peoples Democratic Republic', _('Lao Peoples Democratic Republic')), ('Latvia', _('Latvia')),
                ('Lebanon', _('Lebanon')), ('Lesotho', _('Lesotho')), ('Liberia', _('Liberia')),
                ('Libyan Arab Jamahiriya', _('Libyan Arab Jamahiriya')), ('Liechtenstein', _('Liechtenstein')),
                ('Lithuania', _('Lithuania')), ('Luxembourg', _('Luxembourg')), ('Macao', _('Macao')),
                ('Macedonia, The Former Yugoslav Republic of', _('Macedonia, The Former Yugoslav Republic of')),
                ('Madagascar', _('Madagascar')), ('Malawi', _('Malawi')), ('Malaysia', _('Malaysia')),
                ('Maldives', _('Maldives')), ('Mali', _('Mali')), ('Malta', _('Malta')),
                ('Marshall Islands', _('Marshall Islands')), ('Martinique', _('Martinique')),
                ('Mauritania', _('Mauritania')), ('Mauritius', _('Mauritius')), ('Mayotte', _('Mayotte')),
                ('Mexico', _('Mexico')), ('Micronesia, Federated States of', _('Micronesia, Federated States of')),
                ('Moldova, Republic of', _('Moldova, Republic of')), ('Monaco', _('Monaco')),
                ('Mongolia', _('Mongolia')), ('Montserrat', _('Montserrat')), ('Morocco', _('Morocco')),
                ('Mozambique', _('Mozambique')), ('Myanmar', _('Myanmar')), ('Namibia', _('Namibia')),
                ('Nauru', _('Nauru')), ('Nepal', _('Nepal')), ('Netherlands', _('Netherlands')),
                ('Netherlands Antilles', _('Netherlands Antilles')), ('New Caledonia', _('New Caledonia')),
                ('New Zealand', _('New Zealand')), ('Nicaragua', _('Nicaragua')), ('Niger', _('Niger')),
                ('Nigeria', _('Nigeria')), ('Niue', _('Niue')), ('Norfolk Island', _('Norfolk Island')),
                ('Northern Mariana Islands', _('Northern Mariana Islands')), ('Norway', _('Norway')),
                ('Oman', _('Oman')), ('Pakistan', _('Pakistan')), ('Palau', _('Palau')),
                ('Palestinian Territory, Occupied', _('Palestinian Territory, Occupied')), ('Panama', _('Panama')),
                ('Papua New Guinea', _('Papua New Guinea')), ('Paraguay', _('Paraguay')), ('Peru', _('Peru')),
                ('Philippines', _('Philippines')), ('Pitcairn', _('Pitcairn')), ('Poland', _('Poland')),
                ('Portugal', _('Portugal')), ('Puerto Rico', _('Puerto Rico')), ('Qatar', _('Qatar')),
                ('Reunion', _('Reunion')), ('Romania', _('Romania')), ('Russian Federation', _('Russian Federation')),
                ('Rwanda', _('Rwanda')), ('Saint Helena', _('Saint Helena')),
                ('Saint Kitts and Nevis', _('Saint Kitts and Nevis')), ('Saint Lucia', _('Saint Lucia')),
                ('Saint Pierre and Miquelon', _('Saint Pierre and Miquelon')),
                ('Saint Vincent and The Grenadines', _('Saint Vincent and The Grenadines')), ('Samoa', _('Samoa')),
                ('San Marino', _('San Marino')), ('Sao Tome and Principe', _('Sao Tome and Principe')),
                ('Saudi Arabia', _('Saudi Arabia')), ('Senegal', _('Senegal')),
                ('Serbia and Montenegro', _('Serbia and Montenegro')), ('Seychelles', _('Seychelles')),
                ('Sierra Leone', _('Sierra Leone')), ('Singapore', _('Singapore')), ('Slovakia', _('Slovakia')),
                ('Slovenia', _('Slovenia')), ('Solomon Islands', _('Solomon Islands')), ('Somalia', _('Somalia')),
                ('South Africa', _('South Africa')),
                ('South Georgia and The South Sandwich Islands', _('South Georgia and The South Sandwich Islands')),
                ('Spain', _('Spain')), ('Sri Lanka', _('Sri Lanka')), ('Sudan', _('Sudan')),
                ('Suriname', _('Suriname')), ('Svalbard and Jan Mayen', _('Svalbard and Jan Mayen')),
                ('Swaziland', _('Swaziland')), ('Sweden', _('Sweden')), ('Switzerland', _('Switzerland')),
                ('Syrian Arab Republic', _('Syrian Arab Republic')),
                ('Taiwan, Province of China', _('Taiwan, Province of China')), ('Tajikistan', _('Tajikistan')),
                ('Tanzania, United Republic of', _('Tanzania, United Republic of')), ('Thailand', _('Thailand')),
                ('Timor-leste', _('Timor-leste')), ('Togo', _('Togo')), ('Tokelau', _('Tokelau')),
                ('Tonga', _('Tonga')), ('Trinidad and Tobago', _('Trinidad and Tobago')), ('Tunisia', _('Tunisia')),
                ('Turkmenistan', _('Turkmenistan')), ('Tuvalu', _('Tuvalu')), ('Uganda', _('Uganda')),
                ('Ukraine', _('Ukraine')), ('United Kingdom', _('United Kingdom')),
                ('United States', _('United States')), ('United Arab Emirates', _('United Arab Emirates')),
                ('Uruguay', _('Uruguay')), ('Uzbekistan', _('Uzbekistan')), ('Vanuatu', _('Vanuatu')),
                ('Venezuela', _('Venezuela')), ('Viet Nam', _('Viet Nam')),
                ('Virgin Islands, British', _('Virgin Islands, British')),
                ('Virgin Islands, U.S.', _('Virgin Islands, U.S.')), ('Wallis and Futuna', _('Wallis and Futuna')),
                ('Western Sahara', _('Western Sahara')), ('Yemen', _('Yemen')), ('Zambia', _('Zambia')),
                ('Zimbabwe', _('Zimbabwe')),)
#################### Egypt Cities ####################

############### Governorates List ###############
Governorates_List = (
    ('Alexandria', _('Alexandria')), ('Aswan', _('Aswan')), ('Asyut', _('Asyut')), ('Beheira', _('Beheira')),
    ('Beni Suef', _('Beni Suef')), ('Cairo', _('Cairo')), ('Dakahlia', _('Dakahlia')), ('Damietta', _('Damietta')),
    ('Faiyum', _('Faiyum')), ('Gharbia', _('Gharbia')), ('Giza', _('Giza')), ('Ismailia', _('Ismailia')),
    ('Kafr El Sheikh', _('Kafr El Sheikh')), ('Luxor', _('Luxor')), ('Matruh', _('Matruh')), ('Minya', _('Minya')),
    ('Monufia', _('Monufia')), ('New Valley', _('New Valley')), ('North Sinai', _('North Sinai')),
    ('Port Said', _('Port Said')), ('Qalyubia', _('Qalyubia')), ('Qena', _('Qena')), ('Red Sea', _('Red Sea')),
    ('Sharqia', _('Sharqia')), ('Sohag', _('Sohag')), ('South Sinai', _('South Sinai')), ('Suez', _('Suez')),)
############### City List ###############


############### Language List ###############
Language_List = (('Arabic', _('Arabic')), ('English', _('English')), ('French', _('French')), ('German', _('German')),
                 ('Italian', _('Italian')), ('Japanese', _('Japanese')), ('Korean', _('Korean')),
                 ('Portuguese', _('Portuguese')), ('Russian', _('Russian')), ('Spanish', _('Spanish')),
                 ('Turkish', _('Turkish')), ('Chinese', _('Chinese')),)
############### Currency List ###############
Currency_List = (
    ('USD', _('USD')), ('EUR', _('EUR')), ('GBP', _('GBP')), ('JPY', _('JPY')), ('AUD', _('AUD')), ('CAD', _('CAD')),
    ('CHF', _('CHF')), ('CNY', _('CNY')), ('SEK', _('SEK')), ('NZD', _('NZD')), ('MXN', _('MXN')), ('SGD', _('SGD')),
    ('HKD', _('HKD')), ('NOK', _('NOK')), ('KRW', _('KRW')), ('TRY', _('TRY')), ('RUB', _('RUB')), ('INR', _('INR')),
    ('BRL', _('BRL')), ('ZAR', _('ZAR')), ('DKK', _('DKK')), ('PLN', _('PLN')), ('TWD', _('TWD')), ('THB', _('THB')),
    ('IDR', _('IDR')), ('HUF', _('HUF')), ('CZK', _('CZK')), ('ILS', _('ILS')), ('CLP', _('CLP')), ('PHP', _('PHP')),
    ('AED', _('AED')), ('COP', _('COP')), ('SAR', _('SAR')), ('MYR', _('MYR')), ('RON', _('RON')), ('ARS', _('ARS')),
    ('PEN', _('PEN')), ('PKR', _('PKR')), ('IQD', _('IQD')), ('QAR', _('QAR')), ('KWD', _('KWD')), ('OMR', _('OMR')),
    ('BHD', _('BHD')), ('JOD', _('JOD')), ('LBP', _('LBP')), ('EGP', _('EGP')), ('BDT', _('BDT')), ('NGN', _('NGN')),
    ('TZS', _('TZS')), ('UGX', _('UGX')), ('GHS', _('GHS')), ('KES', _('KES')), ('XAF', _('XAF')), ('XOF', _('XOF')),
    ('XPF', _('XPF')), ('MAD', _('MAD')), ('DZD', _('DZD')), ('TND', _('TND')), ('MRO', _('MRO')), ('LYD', _('LYD')),
    ('TMT', _('TMT')), ('MZN', _('MZN')), ('GMD', _('GMD')), ('AOA', _('AOA')), ('ZMW', _('ZMW')), ('CDF', _('CDF')),
    ('BIF', _('BIF')), ('RWF', _('RWF')), ('STD', _('STD')), ('SLL', _('SLL')), ('LRD', _('LRD')), ('GEL', _('GEL')),
    ('AMD', _('AMD')), ('ALL', _('ALL')), ('HNL', _('HNL')), ('NIO', _('NIO')), ('CRC', _('CRC')), ('MKD', _('MKD')),
    ('BAM', _('BAM')), ('TOP', _('TOP')), ('FJD', _('FJD')), ('BBD', _('BBD')), ('BSD', _('BSD')), ('BZD', _('BZD')),
    ('BMD', _('BMD')), ('SBD', _('SBD')), ('SRD', _('SRD')), ('GYD', _('GYD')), ('AZN', _('AZN')), ('SVC', _('SVC')),
    ('PGK', _('PGK')), ('LAK', _('LAK')), ('SOS', _('SOS')), ('MMK', _('MMK')), ('KGS', _('KGS')), ('UZS', _('UZS')),
    ('TJS', _('TJS')), ('MOP', _('MOP')), ('KZT', _('KZT')), ('KPW', _('KPW')), ('SSP', _('SSP')), ('SYP', _('SYP')),
    ('YER', _('YER')), ('TWD', _('TWD')), ('MRU', _('MRU')), ('BYN', _('BYN')), ('BGN', _('BGN')), ('CDF', _('CDF')),
    ('BAM', _('BAM')), ('BBD', _('BBD')), ('BMD', _('BMD')), ('BND', _('BND')), ('BSD', _('BSD')), ('BWP', _('BWP')),
    ('BZD', _('BZD')), ('CAD', _('CAD')), ('CLP', _('CLP')), ('CNY', _('CNY')), ('COP', _('COP')), ('CRC', _('CRC')),
    ('CUP', _('CUP')), ('CZK', _('CZK')), ('DKK', _('DKK')), ('DOP', _('DOP')), ('EGP', _('EGP')), ('EUR', _('EUR')),
    ('FJD', _('FJD')), ('GBP', _('GBP')), ('GHS', _('GHS')), ('GMD', _('GMD')), ('GTQ', _('GTQ')), ('GYD', _('GYD')),
    ('HKD', _('HKD')), ('HRK', _('HRK')), ('HUF', _('HUF')), ('IDR', _('IDR')), ('ILS', _('ILS')), ('INR', _('INR')),
    ('ISK', _('ISK')), ('JMD', _('JMD')), ('JPY', _('JPY')), ('KES', _('KES')), ('KGS', _('KGS')), ('KHR', _('KHR')),
    ('KRW', _('KRW')), ('KYD', _('KYD')), ('KZT', _('KZT')), ('LAK', _('LAK')), ('LBP', _('LBP')), ('LKR', _('LKR')),
    ('LRD', _('LRD')), ('MAD', _('MAD')), ('MDL', _('MDL')), ('MKD', _('MKD')), ('MMK', _('MMK')), ('MNT', _('MNT')),
    ('MOP', _('MOP')), ('MUR', _('MUR')), ('MVR', _('MVR')), ('MWK', _('MWK')), ('MXN', _('MXN')), ('MYR', _('MYR')),
    ('MZN', _('MZN')), ('NAD', _('NAD')), ('NGN', _('NGN')), ('NIO', _('NIO')), ('NOK', _('NOK')), ('NPR', _('NPR')),
    ('NZD', _('NZD')), ('PAB', _('PAB')), ('PEN', _('PEN')), ('PGK', _('PGK')), ('PHP', _('PHP')), ('PKR', _('PKR')),
    ('PLN', _('PLN')), ('PYG', _('PYG')), ('QAR', _('QAR')), ('RON', _('RON')), ('RSD', _('RSD')), ('RUB', _('RUB')),
    ('RWF', _('RWF')), ('SAR', _('SAR')), ('SBD', _('SBD')), ('SCR', _('SCR')), ('SEK', _('SEK')), ('SGD', _('SGD')),
    ('SLL', _('SLL')), ('SOS', _('SOS')), ('SRD', _('SRD')), ('STD', _('STD')), ('SVC', _('SVC')), ('SZL', _('SZL')),
    ('THB', _('THB')), ('TJS', _('TJS')), ('TOP', _('TOP')), ('TRY', _('TRY')), ('TTD', _('TTD')), ('TWD', _('TWD')),

    ('TZS', _('TZS')), ('UAH', _('UAH')), ('UGX', _('UGX')), ('USD', _('USD')), ('UYU', _('UYU')), ('UZS', _('UZS')),
    ('VEF', _('VEF')), ('VND', _('VND')), ('VUV', _('VUV')), ('WST', _('WST')), ('XAF', _('XAF')), ('XCD', _('XCD')),
    ('XOF', _('XOF')), ('XPF', _('XPF')), ('YER', _('YER')), ('ZAR', _('ZAR')), ('ZMW', _('ZMW')), ('ZWL', _('ZWL')),)
############### Timezone List ###############
Timezone_List = (('Africa/Abidjan', _('Africa/Abidjan')), ('Africa/Accra', _('Africa/Accra')),
                 ('Africa/Addis_Ababa', _('Africa/Addis_Ababa')), ('Africa/Algiers', _('Africa/Algiers')),
                 ('Africa/Asmara', _('Africa/Asmara')), ('Africa/Asmera', _('Africa/Asmera')),
                 ('Africa/Bamako', _('Africa/Bamako')), ('Africa/Bangui', _('Africa/Bangui')),
                 ('Africa/Banjul', _('Africa/Banjul')), ('Africa/Bissau', _('Africa/Bissau')),
                 ('Africa/Blantyre', _('Africa/Blantyre')), ('Africa/Brazzaville', _('Africa/Brazzaville')),
                 ('Africa/Bujumbura', _('Africa/Bujumbura')), ('Africa/Cairo', _('Africa/Cairo')),
                 ('Africa/Casablanca', _('Africa/Casablanca')), ('Africa/Ceuta', _('Africa/Ceuta')),
                 ('Africa/Conakry', _('Africa/Conakry')), ('Africa/Dakar', _('Africa/Dakar')),
                 ('Africa/Dar_es_Salaam', _('Africa/Dar_es_Salaam')), ('Africa/Djibouti', _('Africa/Djibouti')),
                 ('Africa/Douala', _('Africa/Douala')), ('Africa/El_Aaiun', _('Africa/El_Aaiun')),
                 ('Africa/Freetown', _('Africa/Freetown')), ('Africa/Gaborone', _('Africa/Gaborone')),
                 ('Africa/Harare', _('Africa/Harare')), ('Africa/Johannesburg', _('Africa/Johannesburg')),
                 ('Africa/Juba', _('Africa/Juba')), ('Africa/Kampala', _('Africa/Kampala')),
                 ('Africa/Khartoum', _('Africa/Khartoum')), ('Africa/Kigali', _('Africa/Kigali')),
                 ('Africa/Kinshasa', _('Africa/Kinshasa')), ('Africa/Lagos', _('Africa/Lagos')),
                 ('Africa/Libreville', _('Africa/Libreville')), ('Africa/Lome', _('Africa/Lome')),
                 ('Africa/Luanda', _('Africa/Luanda')), ('Africa/Lubumbashi', _('Africa/Lubumbashi')),
                 ('Africa/Lusaka', _('Africa/Lusaka')), ('Africa/Malabo', _('Africa/Malabo')),
                 ('Africa/Maputo', _('Africa/Maputo')), ('Africa/Maseru', _('Africa/Maseru')),
                 ('Africa/Mbabane', _('Africa/Mbabane')), ('Africa/Mogadishu', _('Africa/Mogadishu')),
                 ('Africa/Monrovia', _('Africa/Monrovia')), ('Africa/Nairobi', _('Africa/Nairobi')),
                 ('Africa/Ndjamena', _('Africa/Ndjamena')), ('Africa/Niamey', _('Africa/Niamey')),
                 ('Africa/Nouakchott', _('Africa/Nouakchott')), ('Africa/Ouagadougou', _('Africa/Ouagadougou')),
                 ('Africa/Porto-Novo', _('Africa/Porto-Novo')), ('Africa/Sao_Tome', _('Africa/Sao_Tome')),
                 ('Africa/Timbuktu', _('Africa/Timbuktu')), ('Africa/Tripoli', _('Africa/Tripoli')),
                 ('Africa/Tunis', _('Africa/Tunis')), ('Africa/Windhoek', _('Africa/Windhoek')),
                 ('America/Adak', _('America/Adak')), ('America/Anchorage', _('America/Anchorage')),
                 ('America/Anguilla', _('America/Anguilla')), ('America/Antigua', _('America/Antigua')),
                 ('America/Araguaina', _('America/Araguaina')),
                 ('America/Argentina/Buenos_Aires', _('America/Argentina/Buenos_Aires')),
                 ('America/Argentina/Catamarca', _('America/Argentina/Catamarca')),
                 ('America/Argentina/ComodRivadavia', _('America/Argentina/ComodRivadavia')),
                 ('America/Argentina/Cordoba', _('America/Argentina/Cordoba')),
                 ('America/Argentina/Jujuy', _('America/Argentina/Jujuy')),
                 ('America/Argentina/La_Rioja', _('America/Argentina/La_Rioja')),
                 ('America/Argentina/Mendoza', _('America/Argentina/Mendoza')),
                 ('America/Argentina/Rio_Gallegos', _('America/Argentina/Rio_Gallegos')),
                 ('America/Argentina/Salta', _('America/Argentina/Salta')),
                 ('America/Argentina/San_Juan', _('America/Argentina/San_Juan')),
                 ('America/Argentina/San_Luis', _('America/Argentina/San_Luis')),
                 ('America/Argentina/Tucuman', _('America/Argentina/Tucuman')),
                 ('America/Argentina/Ushuaia', _('America/Argentina/Ushuaia')), ('America/Aruba', _('America/Aruba')),
                 ('America/Asuncion', _('America/Asuncion')), ('America/Atikokan', _('America/Atikokan')),
                 ('America/Atka', _('America/Atka')), ('America/Bahia', _('America/Bahia')),
                 ('America/Bahia_Banderas', _('America/Bahia_Banderas')), ('America/Barbados', _('America/Barbados')),
                 ('America/Belem', _('America/Belem')), ('America/Belize', _('America/Belize')),
                 ('America/Blanc-Sablon', _('America/Blanc-Sablon')), ('America/Boa_Vista', _('America/Boa_Vista')),
                 ('America/Bogota', _('America/Bogota')), ('America/Boise', _('America/Boise')),
                 ('America/Buenos_Aires', _('America/Buenos_Aires')),
                 ('America/Cambridge_Bay', _('America/Cambridge_Bay')),
                 ('America/Campo_Grande', _('America/Campo_Grande')), ('America/Cancun', _('America/Cancun')),
                 ('America/Caracas', _('America/Caracas')), ('America/Catamarca', _('America/Catamarca')),
                 ('America/Cayenne', _('America/Cayenne')), ('America/Cayman', _('America/Cayman')),
                 ('America/Chicago', _('America/Chicago')), ('America/Chihuahua', _('America/Chihuahua')),
                 ('America/Coral_Harbour', _('America/Coral_Harbour')),

                 ('America/Cordoba', _('America/Cordoba')), ('America/Costa_Rica', _('America/Costa_Rica')),
                 ('America/Creston', _('America/Creston')), ('America/Cuiaba', _('America/Cuiaba')),
                 ('America/Curacao', _('America/Curacao')), ('America/Danmarkshavn', _('America/Danmarkshavn')),
                 ('America/Dawson', _('America/Dawson')), ('America/Dawson_Creek', _('America/Dawson_Creek')),
                 ('America/Denver', _('America/Denver')), ('America/Detroit', _('America/Detroit')),
                 ('America/Dominica', _('America/Dominica')), ('America/Edmonton', _('America/Edmonton')),
                 ('America/Eirunepe', _('America/Eirunepe')), ('America/El_Salvador', _('America/El_Salvador')),
                 ('America/Ensenada', _('America/Ensenada')), ('America/Fort_Wayne', _('America/Fort_Wayne')),
                 ('America/Fortaleza', _('America/Fortaleza')), ('America/Glace_Bay', _('America/Glace_Bay')),
                 ('America/Godthab', _('America/Godthab')), ('America/Goose_Bay', _('America/Goose_Bay')),
                 ('America/Grand_Turk', _('America/Grand_Turk')), ('America/Grenada', _('America/Grenada')),
                 ('America/Guadeloupe', _('America/Guadeloupe')), ('America/Guatemala', _('America/Guatemala')),
                 ('America/Guayaquil', _('America/Guayaquil')), ('America/Guyana', _('America/Guyana')),
                 ('America/Halifax', _('America/Halifax')), ('America/Havana', _('America/Havana')),
                 ('America/Hermosillo', _('America/Hermosillo')),
                 ('America/Indiana/Indianapolis', _('America/Indiana/Indianapolis')),
                 ('America/Indiana/Knox', _('America/Indiana/Knox')),
                 ('America/Indiana/Marengo', _('America/Indiana/Marengo')),
                 ('America/Indiana/Petersburg', _('America/Indiana/Petersburg')),
                 ('America/Indiana/Tell_City', _('America/Indiana/Tell_City')),
                 ('America/Indiana/Vevay', _('America/Indiana/Vevay')),
                 ('America/Indiana/Vincennes', _('America/Indiana/Vincennes')),
                 ('America/Indiana/Winamac', _('America/Indiana/Winamac')),
                 ('America/Indianapolis', _('America/Indianapolis')), ('America/Inuvik', _('America/Inuvik')),
                 ('America/Iqaluit', _('America/Iqaluit')), ('America/Jamaica', _('America/Jamaica')),
                 ('America/Jujuy', _('America/Jujuy')), ('America/Juneau', _('America/Juneau')),
                 ('America/Kentucky/Louisville', _('America/Kentucky/Louisville')),
                 ('America/Kentucky/Monticello', _('America/Kentucky/Monticello')),
                 ('America/Knox_IN', _('America/Knox_IN')), ('America/Kralendijk', _('America/Kralendijk')),
                 ('America/La_Paz', _('America/La_Paz')), ('America/Lima', _('America/Lima')),
                 ('America/Los_Angeles', _('America/Los_Angeles')), ('America/Louisville', _('America/Louisville')),
                 ('America/Lower_Princes', _('America/Lower_Princes')), ('America/Maceio', _('America/Maceio')),
                 ('America/Managua', _('America/Managua')), ('America/Manaus', _('America/Manaus')),
                 ('America/Marigot', _('America/Marigot')), ('America/Martinique', _('America/Martinique')),
                 ('America/Matamoros', _('America/Matamoros')), ('America/Mazatlan', _('America/Mazatlan')),
                 ('America/Mendoza', _('America/Mendoza')), ('America/Menominee', _('America/Menominee')),
                 ('America/Merida', _('America/Merida')), ('America/Metlakatla', _('America/Metlakatla')),
                 ('America/Mexico_City', _('America/Mexico_City')), ('America/Miquelon', _('America/Miquelon')),
                 ('America/Moncton', _('America/Moncton')), ('America/Monterrey', _('America/Monterrey')),
                 ('America/Montevideo', _('America/Montevideo')), ('America/Montreal', _('America/Montreal')),
                 ('America/Montserrat', _('America/Montserrat')), ('America/Nassau', _('America/Nassau')),
                 ('America/New_York', _('America/New_York')), ('America/Nipigon', _('America/Nipigon')),
                 ('America/Nome', _('America/Nome')), ('America/Noronha', _('America/Noronha')),
                 ('America/North_Dakota/Beulah', _('America/North_Dakota/Beulah')),
                 ('America/North_Dakota/Center', _('America/North_Dakota/Center')),
                 ('America/North_Dakota/New_Salem', _('America/North_Dakota/New_Salem')),
                 ('America/Ojinaga', _('America/Ojinaga')), ('America/Panama', _('America/Panama')),
                 ('America/Pangnirtung', _('America/Pangnirtung')), ('America/Paramaribo', _('America/Paramaribo')),
                 ('America/Phoenix', _('America/Phoenix')), ('America/Port-au-Prince', _('America/Port-au-Prince')),
                 ('America/Port_of_Spain', _('America/Port_of_Spain')), ('America/Porto_Acre', _('America/Porto_Acre')),
                 ('America/Porto_Velho', _('America/Porto_Velho')), ('America/Puerto_Rico', _('America/Puerto_Rico')),
                 ('America/Rainy_River', _('America/Rainy_River')), ('America/Rankin_Inlet', _('America/Rankin_Inlet')),
                 ('America/Recife', _('America/Recife')), ('America/Regina', _('America/Regina')),
                 ('America/Resolute', _('America/Resolute')), ('America/Rio_Branco', _('America/Rio_Branco')),
                 ('America/Rosario', _('America/Rosario')), ('America/Santa_Isabel', _('America/Santa_Isabel')),
                 ('America/Santarem', _('America/Santarem')), ('America/Santiago', _('America/Santiago')),
                 ('America/Santo_Domingo', _('America/Santo_Domingo')), ('America/Sao_Paulo', _('America/Sao_Paulo')),
                 ('America/Scoresbysund', _('America/Scoresbysund')), ('America/Shiprock', _('America/Shiprock')),
                 ('America/Sitka', _('America/Sitka')), ('America/St_Barthelemy', _('America/St_Barthelemy')),
                 ('America/St_Johns', _('America/St_Johns')), ('America/St_Kitts', _('America/St_Kitts')),
                 ('America/St_Lucia', _('America/St_Lucia')), ('America/St_Thomas', _('America/St_Thomas')),
                 ('America/St_Vincent', _('America/St_Vincent')), ('America/Swift_Current', _('America/Swift_Current')),
                 ('America/Tegucigalpa', _('America/Tegucigalpa')), ('America/Thule', _('America/Thule')),
                 ('America/Thunder_Bay', _('America/Thunder_Bay')), ('America/Tijuana', _('America/Tijuana')),
                 ('America/Toronto', _('America/Toronto')), ('America/Tortola', _('America/Tortola')),
                 ('America/Vancouver', _('America/Vancouver')), ('America/Virgin', _('America/Virgin')),
                 ('America/Whitehorse', _('America/Whitehorse')), ('America/Winnipeg', _('America/Winnipeg')),
                 ('America/Yakutat', _('America/Yakutat')), ('America/Yellowknife', _('America/Yellowknife')),
                 ('Antarctica/Casey', _('Antarctica/Casey')), ('Antarctica/Davis', _('Antarctica/Davis')),
                 ('Antarctica/DumontDUrville', _('Antarctica/DumontDUrville')),
                 ('Antarctica/Macquarie', _('Antarctica/Macquarie')), ('Antarctica/Mawson', _('Antarctica/Mawson')),
                 ('Antarctica/McMurdo', _('Antarctica/McMurdo')), ('Antarctica/Palmer', _('Antarctica/Palmer')),
                 ('Antarctica/Rothera', _('Antarctica/Rothera')), ('Antarctica/South_Pole', _('Antarctica/South_Pole')),
                 ('Antarctica/Syowa', _('Antarctica/Syowa')), ('Antarctica/Troll', _('Antarctica/Troll')),
                 ('Antarctica/Vostok', _('Antarctica/Vostok')), ('Arctic/Longyearbyen', _('Arctic/Longyearbyen')),
                 ('Asia/Aden', _('Asia/Aden')), ('Asia/Almaty', _('Asia/Almaty')), ('Asia/Amman', _('Asia/Amman')),
                 ('Asia/Anadyr', _('Asia/Anadyr')), ('Asia/Aqtau', _('Asia/Aqtau')), ('Asia/Aqtobe', _('Asia/Aqtobe')),
                 ('Asia/Ashgabat', _('Asia/Ashgabat')), ('Asia/Ashkhabad', _('Asia/Ashkhabad')),
                 ('Asia/Baghdad', _('Asia/Baghdad')), ('Asia/Bahrain', _('Asia/Bahrain')),
                 ('Asia/Baku', _('Asia/Baku')), ('Asia/Bangkok', _('Asia/Bangkok')), ('Asia/Beirut', _('Asia/Beirut')),
                 ('Asia/Bishkek', _('Asia/Bishkek')), ('Asia/Brunei', _('Asia/Brunei')),
                 ('Asia/Calcutta', _('Asia/Calcutta')), ('Asia/Choibalsan', _('Asia/Choibalsan')),
                 ('Asia/Chongqing', _('Asia/Chongqing')), ('Asia/Chungking', _('Asia/Chungking')),
                 ('Asia/Colombo', _('Asia/Colombo')), ('Asia/Dacca', _('Asia/Dacca')),
                 ('Asia/Damascus', _('Asia/Damascus')), ('Asia/Dhaka', _('Asia/Dhaka')), ('Asia/Dili', _('Asia/Dili')),
                 ('Asia/Dubai', _('Asia/Dubai')), ('Asia/Dushanbe', _('Asia/Dushanbe')),)

Language_List = (('Arabic', _('Arabic')), ('English', _('English')), ('French', _('French')), ('German', _('German')),
                 ('Italian', _('Italian')), ('Japanese', _('Japanese')), ('Korean', _('Korean')),
                 ('Portuguese', _('Portuguese')), ('Russian', _('Russian')), ('Spanish', _('Spanish')),
                 ('Turkish', _('Turkish')), ('Chinese', _('Chinese')),)

############### Help Categories Helper ###############

Help_Categories = (
    ("FAQ", _("FAQ")), ("Tutorials", _("Tutorials")), ('Videos', _('Videos')), ('Documentations', _('Documentations')),
    ('Products ', _('Products ')), ('Services ', _('Services ')), ('Other', _('Other')),)
############### Catalog Helper ###############
Coupon_Type = (('Default', 'Default'), ('Paid', 'Paid'), ('Free', 'Free'), ('Admin', 'Admin'),)
Discount_Type = (('Percentage', _('Percentage')), ('Fixed', _('Fixed')), (None, _('None')))
Availability = ((True, 'In stock'), (False, 'Out of stock'),)
Size = ((1, 'XS'), (2, 'SM'), (3, 'M'), (4, 'L'), (5, 'XL'), (6, 'XXL'), (7, 'XXXL'),)
Is_Featured = ((False, "Not a featured."), (True, "Is featured."),)
Delivery_Status = ((1, 'Pending'), (2, 'In Progress'), (3, 'Delivered'), (4, 'Cancelled'),)
VARIANTS = (('Unit', _('Unit')), ('Size', _('Size')), ('Color', _('Color')), ('Size-Color', _('Size-Color')),)
OutStock = (('1', _('2-3 Day')), ('2', _('In Stock')), ('3', _('Out Stock')), ('4', 'Pre-order'),)
Purchase_Status = (("Received", "Received"), ("Partial", "Partial"), ("Pending", "Pending"))

Order_Status = (('New', 'New'), ('Accepted', 'Accepted'), ('Preparing', 'Preparing'), ('OnShipping', 'OnShipping'),
                ('Completed', 'Completed'), ('Canceled', 'Canceled'), ('Refund', 'Refund'), ('Rejected', 'Rejected'),
                ('Returned', 'Returned'), ('Draft', 'Draft'))
Delivery_By = (('Ydoob', 'Ydoob'), ('Self', 'Self'),)
Commission_System = (('Category', 'Category'), ('DigitalMarketing', 'Digital Marketing'), ('Referral', 'Referral'),
                     ('ShippingRate', 'Shipping Rate'),)
Shipping_Status = (('Active', 'Active'), ('Inactive', 'Inactive'), ('Free', 'Free'),)
Product_Transaction = (('BUY', 'BUY'), ('SELL', 'SELL'), ('REFUND', 'REFUND'))
Payment_Status = (("Pending", "Pending"), ("Complete", "Complete"), ("Partial", "Partial"), ("Other", "Other"),
                  ("Refunded", "Refunded"), ("Failed", "Failed"), ("Abandoned", "Abandoned"), ("Revoked", "Revoked"),
                  ("Preapproval", "Preapproval"), ("Cancelled", "Cancelled"), ("Subscription", "Subscription"),)
Payment_Methods = (("Online Payment", "Online Payment"), ("Cash on Delivery", "Cash on Delivery"),)
Payment_Gateway = (('COD', 'COD'), ('Fawry', 'Fawry'), ('Paymob', 'Paymob'))
Invoice_Status = [('CURRENT', 'CURRENT'), ('OVERDUE', 'OVERDUE'), ('PAID', 'PAID'), ]

Invoice_CreatedBy = [('CUSTOMER', 'CUSTOMER'), ('ADMIN', 'ADMIN'), ('STAFF', 'STAFF'), ('VENDOR', 'VENDOR'),
                     ('SHIPPING', 'SHIPPING'), ]
Transaction_Money_Type = (("Buy", _("Buy")), ("Sell", _("Sell")), ('Refund', _('Refund')), ('Withdraw', _('Withdraw')),
                          ('Deposit', _('Deposit')), ('Transfer', _('Transfer')), ('Commission', _('Commission')),
                          ('Shipping', _('Shipping')), ('Referral', _('Referral')), ('Rent', _('Rent')),
                          ('Leasing', _('Leasing')), ('Salary', _('Salary')), ('Cost', _('Cost')),
                          ('Leasing Cost', _('Leasing Cost')), ('Expenses', _('Expenses')),
                          ('Timesheet', _('Timesheet')),)

Transaction_Money_Mode = (("Cash", _("Cash")), ("Credit", _("Credit")), ('Debit', _('Debit')), ('Wallet', _('Wallet')),
                          ('Treasury', _('Treasury')), ("Pending", _("Pending")))
Transaction_Method = (
    ("Cash", _("Cash")), ("Visa", _("Visa")), ('Wallet', _('Wallet')), ('Cheque', _('Cheque')), ('Bank', _('Bank')),)
Transaction_Money_Status = (
    ("Pending", _("Pending")), ('Partial', _('Partial')), ("Complete", _("Complete")), ('Failed', _('Failed')),)
Transaction_Money_Category = (("Income", _("Income")), ("Expense", _("Expense")),)
Transaction_Product_Type = (("Buy", _("Buy")), ("Sell", _("Sell")), ('Refund', _('Refund')),)
Transaction_percent_type = (("1", 65), ("2", 3), ("3", 5),)

Duration_Type = (('Days', 'Days'), ('Weeks', 'Weeks'), ('Months', 'Months'), ('Years', 'Years'),)
Wallet_Mode = (("Administrator", _("Administrator")), ("Auditor", _("Auditor")), ("Accountant", _("Accountant")),
               ("User", _("User")),)
Current_App = (("Event", _("Event")), ("Press", _("Press")), ("Medical", _("Medical")), ("Digithup", _("Digithup")),
               ("Other", _("Other")),)
Barcode_Class = (("ean13", _("ean13")), ("code128", _("code128")), ("code39", _("code39")), ("code93", _("code93")),
                 ("code11", _("code11")), ("msi", _("msi")), ("codabar", _("codabar")), ("upc", _("upc")),
                 ("ean8", _("ean8")), ("upce", _("upce")), ("i2of5", _("i2of5")), ("ext_i2of5", _("ext_i2of5")),
                 ("postnet", _("postnet")), ("fim", _("fim")), ("itf14", _("itf14")), ("pzn", _("pzn")),
                 ("plessey", _("plessey")), ("msi10", _("msi10")), ("msi11", _("msi11")), ("msi1010", _("msi1010")),
                 ("msi1110", _("msi1110")), ("pharmacode", _("pharmacode")), ("code32", _("code32")),
                 ("code39ext", _("code39ext")), ("itf6", _("itf6")), ("itf16", _("itf16")), ("gs1_128", _("gs1_128")),
                 ("gs1_128_hr", _("gs1_128_hr")), ("gs1_128_hrt", _("gs1_128_hrt")), ("gs1_128_lgt", _("gs1_128_lgt")),
                 ("gs1_128_lgto", _("gs1_128_lgto")), ("gs1_128_lgts", _("gs1_128_lgts")),
                 ("gs1_128_exp", _("gs1_128_exp")), ("telepen", _("telepen")), ("telepen_num", _("telepen_num")),
                 ("pharmacode2", _("pharmacode2")), ("code25", _("code25")), ("code25_iata", _("code25_iata")),
                 ("code25_matrix", _("code25_matrix")), ("code25_interleaved", _("code25_interleaved")),
                 ("code25_industrial", _("code25_industrial")), ("code39_pmod", _("code39_pmod")),
                 ("code39_mod43", _("code39_mod43")), ("code93ext", _("code93ext")), ("code93_pmod", _("code93_pmod")),
                 ("bcs_code128", _("bcs_code128")), ("bcs_code128_pmod", _("bcs_code128_pmod")),
                 ("bcs_code128_mod43", _("bcs_code128_mod43")), ("bcs_code39", _("bcs_code39")),
                 ("bcs_code39_pmod", _("bcs_code39_pmod")), ("bcs_code39_mod43", _("bcs_code39_mod43")),
                 ("bcs_code93", _("bcs_code93")), ("bcs_code93_pmod", _("bcs_code93_pmod")),
                 ("bcs_code93_mod43", _("bcs_code93_mod43")), ("bcs_datamatrix", _("bcs_datamatrix")),
                 ("bcs_ean", _("bcs_ean")), ("bcs_ean2", _("bcs_ean2")), ("bcs_ean5", _("bcs_ean5")),
                 ("bcs_ean8", _("bcs_ean8")), ("bcs_ean13", _("bcs_ean13")), ("bcs_ean14", _("bcs_ean14")),
                 ("bcs_ean128", _("bcs_ean128")), ("bcs_ean128_pmod", _("bcs_ean128_pmod")),
                 ("bcs_ean128_mod43", _("bcs_ean128_mod43")), ("bcs_gs1", _("bcs_gs1")),
                 ("bcs_gs1_pmod", _("bcs_gs1_pmod")), ("bcs_gs1_mod43", _("bcs_gs1_mod43")),
                 ("bcs_itf14", _("bcs_itf14")), ("bcs_itf", _("bcs_itf")), ("bcs_itf_pmod", _("bcs_itf_pmod")),
                 ("bcs_itf_mod43", _("bcs_itf_mod43")), ("bcs_msi", _("bcs_msi")), ("bcs_msi_pmod", _("bcs_msi_pmod")),
                 ("bcs_msi_mod11", _("bcs_msi_mod11")), ("bcs_msi_mod1010", _("bcs_msi_mod1010")),
                 ("bcs_msi_mod1110", _("bcs_msi_mod1110")), ("bcs_pharmacode", _("bcs_pharmacode")),
                 ("bcs_pharmacode2", _("bcs_pharmacode2")), ("bcs_pzn", _("bcs_pzn")), ("bcs_pzn8", _("bcs_pzn8")),
                 ("bcs_rss14", _("bcs_rss14")), ("bcs_rss14_stacked", _("bcs_rss14_stacked")),
                 ("bcs_rss14_stacked_omni", _("bcs_rss14_stacked_omni")),
                 ("bcs_rss14_truncated", _("bcs_rss14_truncated")), ("bcs_rss14_limited", _("bcs_rss14_limited")),
                 ("bcs_rss14_expanded", _("bcs_rss14_expanded")),
                 ("bcs_rss14_expanded_stacked", _("bcs_rss14_expanded_stacked")),
                 ("bcs_rss14_expanded_stacked_omni", _("bcs_rss14_expanded_stacked_omni")),
                 ("bcs_rss14_expanded_stacked_omni", _("bcs_rss14_expanded_stacked_omni")),
                 ("bcs_rss14_lim_stack", _("bcs_rss14_lim_stack")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_exp_stack", _("bcs_rss14_exp_stack")),
                 ("bcs_rss14_exp_stack_omni", _("bcs_rss14_exp_stack_omni")),
                 ("bcs_rss14_exp_stack_omni", _("bcs_rss14_exp_stack_omni")),
                 ("bcs_rss14_trunc_stack", _("bcs_rss14_trunc_stack")),
                 ("bcs_rss14_trunc_stack_omni", _("bcs_rss14_trunc_stack_omni")),
                 ("bcs_rss14_trunc_stack_omni", _("bcs_rss14_trunc_stack_omni")),
                 ("bcs_rss14_lim_stack", _("bcs_rss14_lim_stack")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),)

########################## Podcast ############################
Video_Source = (('Youtube', 'Youtube'), ('Vimeo', 'Vimeo'), ('Self', 'Self'),)

########################## Employee ############################
Absent_Type = (('Sick', 'Sick'), ('Vacation', 'Vacation'), ('Other', 'Other'),)
Absent_Status = (('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'),)

########################## Ticket#########################
Ticket_Status = (('Open', 'Open'), ('Closed', 'Closed'), ('Pending', 'Pending'), ('Solved', 'Solved'),)
Transportation_Type = (
('Car', 'Car'), ('Bus', 'Bus'), ('Train', 'Train'), ('Plane', 'Plane'), ('Ship', 'Ship'), ('limousine', 'limousine'),)
########################## Clinic ############################
Gander_type = (("Male", _("Male")), ("Female", _("Female")),)
Marital_Status = ("Single", _("Single")), ("Married", _("Married")), ("Divorced", _("Divorced")), (
    "Widowed", _("Widowed"))
Blood_type = (
("A+", _("A+")), ("A-", _("A-")), ("B+", _("B+")), ("B-", _("B-")), ("O+", _("O+")), ("O-", _("O-")), ("AB+", _("AB+")),
("AB-", _("AB-")),)
Dose_Time = (
    ("Morning", _("Morning")), ("Afternoon", _("Afternoon")), ("Evening", _("Evening")), ("Night", _("Night")),)
Medical_Out_Service = (("X-ray", _("X-ray")), ("Lab", _("Lab")), ("Ultrasound", _("Ultrasound")), ("ECG", _("ECG")),
                       ("Medical analysis", _("Medical analysis")), ("Other", _("Other")),)
Complete_Status = (
    ("New", _("New")), ("Pending", _("Pending")), ("InProgress", _("InProgress")), ("Complete", _("Complete")),
    ("Cancel", _("Cancel")),)
Examination_type = (
('Examination', _('Examination')), ('Followup', _('Followup')), ('Urgent', _('Urgent')), ('Completed', _('Completed')))
Appointment_Status = (
('New', _('New')), ('Scheduled', _('Scheduled')), ('Medical Service', _('Medical Service')), ('Results', _('Results')),
('Completed', _('Completed')), ('Followup', _('Followup')), ('Late', _('Late')), ('Cancelled', _('Cancelled')),)
Clinic_Category = (
    ('Anesthesiologist ', _('Anesthesiologist ')), ('Cardiologist', _('Cardiologist')), ('Dentist', _('Dentist')),
    ('Dermatologist', _('Dermatologist')), ('Endocrinologist', _('Endocrinologist')),
    ('Gastroenterologist', _('Gastroenterologist')), ('Gynecologist', _('Gynecologist')),
    ('Hematologist', _('Hematologist')), ('Internist', _('Internist')), ('Nephrologist', _('Nephrologist')),
    ('Neurologist', _('Neurologist')), ('Neurosurgeon', _('Neurosurgeon')), ('Obstetrician', _('Obstetrician')),
    ('Oncologist', _('Oncologist')), ('Ophthalmologist', _('Ophthalmologist')), ('Orthopedist', _('Orthopedist')),
    ('Otolaryngologist', _('Otolaryngologist')), ('Pathologist', _('Pathologist')), ('Pediatrician', _('Pediatrician')),
    ('Physiologist', _('Physiologist')), ('Plastic Surgeon', _('Plastic Surgeon')), ('Podiatrist', _('Podiatrist')),
    ('Psychiatrist', _('Psychiatrist')), ('Radiologist', _('Radiologist')), ('Rheumatologist', _('Rheumatologist')),
    ('Surgeon', _('Surgeon')), ('Urologist', _('Urologist')), ('other', _('other')),)

Clinic_Type = (
    ("Hospital", _("Hospital")), ("Clinic", _("Clinic")), ("Pharmacy", _("Pharmacy")), ("Other", _("Other")),)
ThirdParty_Category = (
    ("Hospital", _("Hospital")), ("Pharmacy", _("Pharmacy")), ("LapTest", _("LapTest")), ("X-ray", _("X-ray")),
    ("Clinic", _("Clinic")),)
Employee_Role = (("Receptionist", _("Receptionist")), ("Accountant", _("Accountant")), ("Designer", _("Designer")),
                 ("Operator", _("Operator")), ("Store Keeper", _("Store Keeper")), ("None", _("None")),)
Prescription_Type = (
    ("syrup", _("syrup")), ("capsule", _("capsule")), ("tablet", _("tablet")), ("injection", _("injection")),
    ("other", _("other")),)
Prescription_Dose = (
    ("1", _("1")), ("2", _("2")), ("3", _("3")), ("4", _("4")), ("5", _("5")), ("6", _("6")), ("7", _("7")),
    ("8", _("8")), ("9", _("9")), ("10", _("10")),)
Medicine_Type = (
    ("syrup", _("syrup")), ("capsule", _("capsule")), ("tablet", _("tablet")), ("injection", _("injection")),
    ("other", _("other")),)
Medicine_Dose = (
    ("1", _("1")), ("2", _("2")), ("3", _("3")), ("4", _("4")), ("5", _("5")), ("6", _("6")), ("7", _("7")),
    ("8", _("8")), ("9", _("9")), ("10", _("10")),)
Medicine_Dose_Time = (
    ("Morning", _("Morning")), ("Afternoon", _("Afternoon")), ("Evening", _("Evening")), ("Night", _("Night")),)
Medicine_Dose_Duration = (("Days", _("Days")), ("Weeks", _("Weeks")), ("Months", _("Months")), ("Years", _("Years")),)
Medicine_Dose_Repeat = (
    ("1", _("1")), ("2", _("2")), ("3", _("3")), ("4", _("4")), ("5", _("5")), ("6", _("6")), ("7", _("7")),
    ("8", _("8")), ("9", _("9")), ("10", _("10")),)
Medicine_Unit = (("packets", _("packets")), ("tablets", _("tablets")), ("pill", _("pill")), ("bottles", _("bottles")),
                 ("boxes", _("boxes")), ('piece', _('piece')), ('sachet', _('sachet')), ('capsule', _('capsule')),
                 ('vial', _('vial')), ('ampoule', _('ampoule')), ('tube', _('tube')), ('bottle', _('bottle')),
                 ('syringe', _('syringe')), ('inhaler', _('inhaler')), ('dropper', _('dropper')), ('puff', _('puff')),
                 ('suppository', _('suppository')), ('patch', _('patch')), ('implant', _('implant')),
                 ('applicator', _('applicator')), ('other', _('other')),)

########################## CAr ############################
Transaction_Coast_Type = (
    ("Truncate", _("Truncate")), ("Acquisition", _("Acquisition")), ("Advance", _("Money Advance")),
    ("Cost", _("Cost")),)
Transaction_Operation = (
    ("Overtime", _("Overtime")), ("Acquisition", _("Acquisition")), ("Advance", _("Advance")), ("Cost", _("Cost")),
    ("Truncate", _("Truncate")), ("Custody", _("Custody")), ("Refund", _("Refund")), ("Withdraw", _("Withdraw")),
    ("Deposit", _("Deposit")), ("Transfer", _("Transfer")), ("Commission", _("Commission")),
    ("Shipping", _("Shipping")), ("Referral", _("Referral")), ("Salary", _("Salary")), ('Rent', _('Rent')),
    ('Leasing', _('Leasing')), ('Leasing Cost', _('Leasing Cost')),)
Overtime_Type = (("Truncate", _("Truncate")), ("Acquisition", _("Acquisition")), ("Cost", _("Cost")))
Car_Overtime_Type = (("Hour", _("Hour")), ("Day", _("Day")), ("Journey", _("Journey")), ("Kilometer", _("Kilometer")),
                     ("Friday", _("Friday")))
Car_Type = (("Car", _("Car")), ("Truck", _("Truck")), ("Bus", _("Bus")), ("Motorcycle", _("Motorcycle")))
Car_Garage_Status = (("In Garage", _("In Garage")), ("Out Garage", _("Out Garage")), ("Standby", _("Standby")),
                     ("Maintenance", _("Maintenance")))
Driver_Garage_Status = (("In Service", _("In Service")), ("Out Service", _("Out Service")), ("Standby", _("Standby")),
                        ("SickLeave", _("Sick Leave")), ("Vacation", _("Vacation")), ("Maintenance", _("Maintenance")))
Car_Status = (
    ("Active", _("Active")), ("Inactive", _("Inactive")), ("Maintenance", _("Maintenance")), ("Repair", _("Repair")))
Car_Insurance_Status = (("Active", _("Active")), ("Inactive", _("Inactive")), ("Expired", _("Expired")))
Car_Insurance_Type = (("Insurance", _("Insurance")), ("Maintenance", _("Maintenance")), ("Repair", _("Repair")))
Car_Insurance_Period = (("Yearly", _("Yearly")), ("Monthly", _("Monthly")), ("Daily", _("Daily")))
Car_Insurance_Period_Type = (("Year", _("Year")), ("Month", _("Month")), ("Day", _("Day")))
Car_Maintenance_Type = (("Maintenance", _("Maintenance")), ("Repair", _("Repair")))
Car_Maintenance_Status = (
    ("Active", _("Active")), ("Inactive", _("Inactive")), ("Pending", _("Pending")), ("Completed", _("Completed")))
Car_Owner_Type = (("Owner", _("Owner")), ("Contractor", _("Contractor")), ("Company", _("Company")))
Car_Owner_Status = (("Active", _("Active")), ("Inactive", _("Inactive")), ("Suspend", _("Suspend")))
contract_Owner_Type = (("Contractor", _("Contractor")), ("Company", _("Company")))
Reservation_Status = (
    ("New", _("New")), ("Accepted", _("Accepted")), ("Rejected", _("Rejected")), ("Canceled", _("Canceled")),
    ("Completed", _("Completed")))
Reservation_Type = (("Car", _("Car")), ("Driver", _("Driver")), ("Both", _("Both")))
Car_Reservation_Status = (("Active", _("Active")), ("Ended", _("Ended")), ("Canceled", _("Canceled")))
Approved_Status = (
    ("Approved", _("Approved")), ("Partial Approval", _("Partial Approval")), ("Not Approved", _("Not Approved")),
    ("Pending", _("Pending")))
Approved_Need = (("All", _("All")), ("Partial", _("Partial")), ("None", _("None")))
########################## Press ############################
Media_Type = (('Image', 'Image'), ('Video', 'Video'), ('Audio', 'Audio'), ('File', 'File'),)
Supply_Type = (('In', _("In")), ('Out', _("Out")),)
Machine_Feed = (("Paper", _("Paper")), ("Zinc", _("Zinc")), ("Plastic", _("Plastic")), ("Other", _("Other")),)
Job_Type = (("Printing", _("Printing")), ("Cutting", _("Cutting")), ("Binding", _("Binding")), ("Other", _("Other")),)
Job_Status = (
    ("New", _("New")), ("Accepted", _("Accepted")), ("Preparing", _("Preparing")), ("OnShipping", _("OnShipping")),
    ("Completed", _("Completed")), ("Canceled", _("Canceled")), ("Refund", _("Refund")), ("Rejected", _("Rejected")),
    ("Returned", _("Returned")), ("Draft", _("Draft")),)
Calculation_Method = (
    ("Unit", _("Unit")), ("Dimensions", _("Dimensions")), ("Options", _("Options")), ("Weight", _("Weight")),
    ("Area", _("Area")), ("Volume", _("Volume")), ("Quantity", _("Quantity")), ("Time", _("Time")),
    ("Other", _("Other")), (None, _("None")),)
########################## Notification  ############################
Notification_CHOICES = (("New", _("New")), ("Message", _("Message")), ("Application", _("Application")),
                        ("NewR egistration", _("New Registration")), ("New Vendor", _("NewV endor")),
                        ("Payment", _("Payment")), ("Order", _("Order")), ("Shipping", _("Shipping")),
                        ("Delivery", _("Delivery")), ("Other", _("Other")), ("Reservation", _("Reservation")),)

################### MEMBERSHIP ##############################
MEMBERSHIP_CHOICES = (

    ('Free', 'Free Membership'), ('Paid', 'Paid Membership'), ('PromoCode', 'PromoCode Membership'),
    ('NoMembership', 'No Membership'), ('Expired Membership', 'Expired Membership'), ('Default', 'Default Membership'),
    ('Admin', 'Admin Membership'), ('user', 'user Membership'),

)
PERIOD_DURATION = (
    ('Days', ('Days')), ('Week', 'Week'), ('Months', 'Months'), ('Quarter', 'Quarter'), ('Years', 'Years'),)
Subscription_Status = (
    ("New", _("New")), ("Accepted", _("Accepted")), ("Rejected", _("Rejected")), ("Canceled", _("Canceled")),
    ("Completed", _("Completed")), ("Expired", _("Expired")), ("Suspend", _("Suspend")),)
################### Blog ##############################
Service_Type = (('Service', 'Service'), ('Work', 'Work'), ('Product', 'Product'), ('Project', 'Project'),
                ('Portfolio', 'Portfolio'), ('Other', 'Other'))
Service_Status = (('Active', 'Active'), ('Waiting', 'Waiting for activation'), ('Inactive', 'Inactive'),)
Featured_Status = (('Active', 'Active'), ('Inactive', 'Inactive'),)
MultiFile_Type = (
    ('image', 'image'), ('hero', 'hero'), ('video', 'video'), ('cover', 'cover'), ('file', 'file'), ('Other', 'Other'))
Banners_Position = (
    ('Top Left', 'Top Left'), ('Top Middle', 'Top Middle'), ('Top Right', 'Top Right'), ('Middle Left', 'Middle Left'),
    ('Middle Right', 'Middle Right'), ('Bottom Left', 'Bottom Left'), ('Bottom Middle', 'Bottom Middle'),
    ('Bottom Right', 'Bottom Right'), ('Collection Sidebar', 'Collection Sidebar'),
    ('Categories Top', 'Categories Top'), ('Categories Sidebar', 'Categories Sidebar'),)

################### User ##############################
User_Position = (('Writer', 'Writer'), ('Lawyer', 'Lawyer'), ('Clients', 'Clients'), ('Co-founder', 'Co-founder'),
                 ('Developer', 'Developer'), ('Admin', 'Admin'), ('SuperAdmin', 'SuperAdmin'), ('Editor', 'Editor'),
                 ('Moderator', 'Moderator'), ('Member', 'Member'), ('Guest', 'Guest'))
Access_Level = (('Customer', 'Customer'), ('Staff', 'Staff'), ('Accountant', 'Accountant'), ('Admin', 'Admin'),
                ('SuperAdmin', 'SuperAdmin'), ('Vendor', 'Vendor'), ('Shipping', 'Shipping'),
                ('Custodian', 'Custodian'), ('Moderator', 'Moderator'), ('Member', 'Member'), ('Guest', 'Guest'),
                ('Other', 'Other'), ('Employee', 'Employee'), ('Manager', 'Manager'), ('Owner', 'Owner'),
                ('Partner', 'Partner'), ('SuperAdmin', 'SuperAdmin'), ('ThirdPartyService', 'ThirdPartyService'),
                ('Attendees', 'Attendees'),)
User_Status = (('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspend', 'Suspend'), ('Banned', 'Banned'),)

############### Clients Helper ###############
Client_Type = (
    ("Supplier", _("Supplier")), ("Client", _("Client")), ("Major", _("Major  Client")), ("walkIn", _("walkIn")),
    ("Vendor", _("Vendor")), ("Contractor", _("Contractor")), ("Company", _("Company")), ("Owner", _("Owner")),
    ("Attendees", _("Attendees")), ("Other", _("Other")),)

Employee_Type = (("Employee", _("Employee")), ("Accountant", _("Accountant")), ("Moderator", _("Moderator")),
                 ("Manager", _("Manager")), ("Owner", _("Owner")), ("Partner", _("Partner")),)
Address_Type = (('Home', 'Home'), ('Business', 'Business'),)
Employee_Overtime_Type = (
    ('Hourly', _('Hourly')), ('Daily', _('Daily')), ('Weekly', _('Weekly')), ('Monthly', _('Monthly')),)
Company_Type = (('Clinic', 'Clinic'), ('ThirdParty', 'ThirdParty'), ('Partner', 'Partner'), ('Other', 'Other'),)

############### Lawyer Helper ###############
Attorney_Type = (('single', _('single')), ('multi', _('multi')),)
Update_Type = (('decision', _('decision')), ('expert', _('expert')),)
Cases_Finish = (('متداولة', 'متداولة'), ('أرشفة', 'أرشفة'),)

Court_Name = (('المحكمة الدستورية', 'المحكمة الدستورية'), ('محكمة النقض', 'محكمة النقض'),
              ('المحكمة الإدارية العليا', 'المحكمة الإدارية العليا'), ('محكمة القضاء الإداري', 'محكمة القضاء الإداري'),
              ('المحكمة الإدارية', 'المحكمة الإدارية'), ('المحكمة التأديبية', 'المحكمة التأديبية'),
              ('هيئة مفوضي الدولة', 'هيئة مفوضي الدولة'), ('محاكم الإستئناف', 'محاكم الإستئناف'),
              ('المحاكم الإبتدائية', 'المحاكم الإبتدائية'), ('المحاكم الجزئية', 'المحاكم الجزئية'),
              ('محاكم الأسرة', 'محاكم الأسرة'), ('المحكمة الإقتصادية', 'المحكمة الإقتصادية'),
              ('محكمة القضاء العسكري', 'محكمة القضاء العسكري'), ('محاكم أمن الدولة العليا', 'محاكم أمن الدولة العليا'),

              )

Prosecution_Type = (('النيابة العامة', 'النيابة العامة'), ('النيابة العسكرية', 'النيابة العسكرية'),
                    ('النيابة الإدارية', 'النيابة الإدارية'),

                    )

Cases_Type = (
    ('مدني', 'مدني'), ('عمالي', 'عمالي'), ('أسرة', 'أسرة'), ('جنح', 'جنح'), ('جنايات', 'جنايات'), ('عسكرية', 'عسكرية'),
    ('الإدارية', 'الإدارية'),)
# Cases_Type = (
# ('مدني جزئي', 'مدني جزئي'),
# ('مدني كلي', 'مدني كلي'),
# ('مدني مستأنف', 'مدني مستأنف'),
# ('أسرة كلي', 'أسرة كلي'),
# ('أسرة مستأنف', 'أسرة مستأنف'),
# ('وراثات', 'وراثات'),
# ('أحوال شخصية', 'أحوال شخصية'),
# ('جنح جزئي', 'جنح جزئي'),
# ('جنح مستأنف', 'جنح مستأنف'),
# ('جنايات', 'جنايات'),
# ('أمن دولة', 'أمن دولة'),
# ('أمن دولة', 'أمن دولة'),
# ('عسكرية', 'عسكرية'),
# ('نقض', 'نقض'),
# ('مجلس الدولة', 'مجلس الدولة'),
# ('قضاء إداري', 'قضاء إداري'),
# ('مجلس الدولة', 'مجلس الدولة'),


Mdny_Second = (
    ('جزئي', 'جزئي'), ('كلي', 'كلي'), (' أستئناف', 'أستئناف'), (' أستئناف عالي', 'أستئناف عالي '), (' نقض', 'نقض '),)
Sr_Second = (('كلي', 'كلي'), ('حبس', 'حبس'), (' أستئناف', 'أستئناف'), ('وراثات', 'وراثات '), (' نقض', 'نقض '),)
Mly_Second = (('كلي', 'كلي'), (' أستئناف', 'أستئناف'), (' نقض', 'نقض '),)
Ldry_Second = (('محكمة القضاء الإداري', 'محكمة القضاء الإداري'), (' المحكمة الإدارية', 'المحكمة الإدارية'),
               (' المحكمة الإدارية العليا', 'المحكمة الإدارية العليا '), ('المحكمة الدستورية', 'المحكمة الدستورية'),)
Jnyt_Second = (('محكمةالجنايات', 'محكمة الجنايات'), (' محكمة النقض', 'محكمة النقض'))
JnH_Second = (('جزئي', 'جزئي'), (' أستئناف', 'أستئناف'), (' نقض', 'نقض '),)
Skry_Second = (('جنح عسكرية', 'جنح عسكرية'), ('جنايات عسكرية', 'جنايات عسكرية'), ('نقض عسكري', 'نقض عسكري'))

Mdny_Type = (('مدعي', 'مدعي'), ('مدعي عليه', 'مدعي عليه'), (' خصم متدخل هجومي', 'خصم متدخل هجومي'),
             (' خصم متدخل انضمامي', 'خصم متدخل انضمامي '), (' خصم مدخل', 'خصم مدخل'), (' مستأتف', 'مستأتف'),
             (' مستأتف ضده', 'مستأتف ضده'), (' طاعن', 'طاعن'), (' مطعون ضده', 'مطعون ضده'),

             )
Sr_Type = (
('مدعي', 'مدعي'), ('مدعي عليه', 'مدعي عليه'), (' مستأتف', 'مستأتف'), (' مستأتف ضده', 'مستأتف ضده'), (' طاعن', 'طاعن'),
(' مطعون ضده', 'مطعون ضده'),)

Mly_Type = (
('مدعي', 'مدعي'), ('مدعي عليه', 'مدعي عليه'), (' مستأتف', 'مستأتف'), (' مستأتف ضده', 'مستأتف ضده'), (' طاعن', 'طاعن'),
(' مطعون ضده', 'مطعون ضده'),)
Ldry_Type = (
('مدعي', 'مدعي'), ('مدعي عليه', 'مدعي عليه'), (' مستأتف', 'مستأتف'), (' مستأتف ضده', 'مستأتف ضده'), (' طاعن', 'طاعن'),
(' مطعون ضده', 'مطعون ضده'),)
Jnyt_Type = (('متهم', 'متهم'), ('مجني عليه', 'مجني عليه'), ('سلطة اتهام', 'سلطة اتهام'),
             (' محكوم عليه - طاعن', 'محكوم عليه - طاعن'), (' مطعون ضده', 'مطعون ضده'),)
JnH_Type = (('متهم', 'متهم'), ('مجني عليه', 'مجني عليه'), ('سلطة اتهام', 'سلطة اتهام'),
            (' محكوم عليه - طاعن', 'محكوم عليه - طاعن'), (' مطعون ضده', 'مطعون ضده'),)
Skry_Type = (('متهم', 'متهم'), ('مجني عليه', 'مجني عليه'), ('سلطة اتهام', 'سلطة اتهام'),
             (' محكوم عليه - طاعن', 'محكوم عليه - طاعن'), (' مطعون ضده', 'مطعون ضده'),)
Case_Task = (('public', 'عامة'), ('private', 'خاصة'),)
Transaction_Type = (('administrative', 'administrative'), ('cases', 'cases'), ('other', 'other'))
########################## Sport ############################

Sport_Type = (
('football', 'football'), ('basketball', 'basketball'), ('volleyball', 'volleyball'), ('tennis', 'tennis'),
('handball', 'handball'), ('swimming', 'swimming'), ('running', 'running'), ('other', 'other'),)
Sport_Status = (('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspend', 'Suspend'), ('Banned', 'Banned'),)
Sport_Level = (
('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Other', 'Other'),)
Match_Status = (('Yes', 'Yes'), ('No', 'No') )
Match_Type = (('Friendly', 'Friendly'), ('Tournament', 'Tournament'), ('League', 'League'), ('Other', 'Other'),)
Match_Result = (('Win', 'Win'), ('Lose', 'Lose'), ('Draw', 'Draw'), ('Other', 'Other'),)
Match_Round = (
('Round 1', 'Round 1'), ('Round 2', 'Round 2'), ('Round 3', 'Round 3'), ('Round 4', 'Round 4'), ('Round 5', 'Round 5'),
('Round 6', 'Round 6'), ('Round 7', 'Round 7'), ('Round 8', 'Round 8'), ('Round 9', 'Round 9'),
('Round 10', 'Round 10'), ('Round 11', 'Round 11'), ('Round 12', 'Round 12'), ('Round 13', 'Round 13'),
('Round 14', 'Round 14'), ('Round 15', 'Round 15'), ('Round 16', 'Round 16'),)
Match_Round_Type = (('Round Robin', 'Round Robin'), ('Knockout', 'Knockout'), ('Other', 'Other'),)
Match_Round_Status = (('New', 'New'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Canceled', 'Canceled'),
                      ('Completed', 'Completed'), ('Expired', 'Expired'), ('Suspend', 'Suspend'),)
Sport_Core_type = (
('1st-half', '1st Half'), ('2nd-half', '2nd Half'), ('Extra-time', 'Extra Time'), ('Penalty', 'Penalty'),
('Referee', 'Referee'), ('1st_assistant', '1st_assistant'), ('2nd_assistant', '2nd_assistant'),
('4th_official', '4th_official'), ('5th_official', '5th_official'), ('6th_official', '6th_official'), ('VAR', 'VAR'),
('Lineup', 'Lineup'), ('Substitution', 'Substitution'), ('Goal', 'Goal'), ('Yellow_card', 'Yellow Card'),
('Red_card', 'Red Card'), ('Injury', 'Injury'), ('Other', 'Other'), ('Sidelined', 'Sidelined'),
('Own Goal', 'Own Goal'), ('Missed Penalty', 'Missed Penalty'), ('Penalties', 'Penalties'),)

Sport_Stat_Type = (('Id', 'Id'), ('Sport', 'Sport'),)

Position_List = (('Setter', 'Setter'),('Outside Hitter', 'Outside Hitter'),('Middle Hitter', 'Middle Hitter'),
('Right Side Hitter', 'Right Side Hitter'),('Libero', 'Libero'),('Defensive Specialist', 'Defensive Specialist'),
('Goalkeeper', 'Goalkeeper'), ('Defender', 'Defender'), ('Midfielder', 'Midfielder'), ('Forward', 'Forward'),
('Other', 'Other'),)

Tv_Type = (('Satellite', 'Satellite'), ('Cable', 'Cable'), ('IPTV', 'IPTV'), ('Channel', 'Channel'),)
Half_List = (('1st Half', '1st Half'), ('2nd Half', '2nd Half'), ('Extra Time', 'Extra Time'), ('Penalty', 'Penalty'),)
Set_List  = (('1stSet', '1st Set'), ('2ndSet', '2nd Set'), ('3rdSet', '3rdSet'), ('4thSet', '4th Set'), ('5thSet', '5th Set'),)
Match_Statics = (('Goal', 'Goal'),('Messed Shots', 'Messed Shots'),('Shots On Target', 'Shots On Target'),('Shots Off Target', 'Shots Off Target'),
('Possession', 'Possession'),('Passes', 'Passes'),('Passes Completed', 'Passes Completed'),('Passes Failed', 'Passes Failed'),('Corner Kicks', 'Corner Kicks'),
('Offsides', 'Offsides'),('Fouls', 'Fouls'),('Yellow Cards', 'Yellow Cards'),('Red Cards', 'Red Cards'),('Injuries', 'Injuries'),('Substitutions', 'Substitutions'),
('Other', 'Other'),('Sidelined', 'Sidelined'),('Own Goal', 'Own Goal'),('Missed Penalty', 'Missed Penalty'),('Penalties', 'Penalties'),('Set', 'Set'),
('Serv', 'Serv'),('Reception', 'Reception'),('Shot', 'Shot'),('Block', 'Block'),('Attack', 'Attack'),('Defense', 'Defense'),('Spike', 'Spike'),('Dig', 'Dig'),
('Points', 'Points'),('Attacks', 'Attacks'),('Serve Points', 'Serve Points'),('Blocks', 'Blocks'),('Opponent Errors', 'Opponent Errors'),('% Attack', '% Attack'),
('% Reception', '% Reception'),('% Field Goals', '% Field Goals'),('% 3 Pointers', '% 3 Pointers'),('% Free Throws', '% Free Throws'),('Assists', 'Assists'),
('Rebounds', 'Rebounds'),('Off.Rebounds', 'Off.Rebounds'),('Def.Rebounds', 'Def.Rebounds'),('Steals', 'Steals'),('Turnovers', 'Turnovers'),
('Fast Break Points', 'Fast Break Points'),('Points Off Turnovers', 'Points Off Turnovers'),('Points In The Paint', 'Points In The Paint'),
('Personal Fouls', 'Personal Fouls'),('Second Chance Points', 'Second Chance Points'),('Flagrant Fouls', 'Flagrant Fouls'),('Technical Fouls', 'Technical Fouls'),)

Season_Order = (('1st', '1st'), ('2nd', '2nd'), ('3rd', '3rd'), ('4th', '4th'), ('5th', '5th'), ('6th', '6th'), ('7th', '7th'), ('8th', '8th'), ('9th', '9th'), ('10th', '10th'),
('11th', '11th'), ('12th', '12th'), ('13th', '13th'), ('14th', '14th'), ('15th', '15th'), ('16th', '16th'), ('17th', '17th'), ('18th', '18th'), ('19th', '19th'), ('20th', '20th'),
('21st', '21st'), ('22nd', '22nd'), ('23rd', '23rd'), ('24th', '24th'), ('25th', '25th'), ('26th', '26th'), ('27th', '27th'), ('28th', '28th'), ('29th', '29th'), ('30th', '30th'),
('31st', '31st'), ('32nd', '32nd'), ('33rd', '33rd'), ('34th', '34th'), ('35th', '35th'), ('36th', '36th'), ('37th', '37th'), ('38th', '38th'), ('39th', '39th'), ('40th', '40th'),
('41st', '41st'), ('42nd', '42nd'), ('43rd', '43rd'), ('44th', '44th'), ('45th', '45th'), ('46th', '46th'), ('47th', '47th'), ('48th', '48th'), ('49th', '49th'), ('50th', '50th'),
('51st', '51st'), ('52nd', '52nd'), ('53rd', '53rd'), ('54th', '54th'), ('55th', '55th'), ('56th', '56th'), ('57th', '57th'), ('58th', '58th'), ('59th', '59th'), ('60th', '60th'),
('61st', '61st'), ('62nd', '62nd'), )

Statics_Type = (('General', 'General'), ('Match', 'General'), )


########## Blog ##############################


COMMENT_STATUS = (('Open', 'Open'), ('Close', 'Close'),)
Article_Type = (('Article', 'Article'), ('Page', 'Page'),)


