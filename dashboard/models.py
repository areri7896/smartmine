from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


# class WithdrawStatusTextChoices(models.TextChoices):
#     PENDING = "Processing"
#     COMPLETED = "Completed"
#     CANCELLED = "Cancelled"
#     FAILED = "Failed" 

class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_completed = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    # status = models.CharField(max_length=20, choices=WithdrawStatusTextChoices, default="PENDING")

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     if self.is_completed:
    #         self.is_cancelled = False
    #     else:
    #         self.is_cancelled = True
    #     super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

class Depo_Verification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_completed = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    profile_pic = models.ImageField(default='user/profile_pics/32x32.png', upload_to = 'user/profile_pics')
    username = models.CharField(max_length=100, default='')
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    dob = models.DateField(null=True, blank=True)
    show_terms_modal = models.BooleanField(default=True)
    COUNTRY_CHOICES = [
      ("AD", "Andorra (+376)"),
      ("AE", "United Arab Emirates (+971)"),
      ("AF", "Afghanistan (+93)"),
      ("AG", "Antigua and Barbuda (+1268)"),
      ("AI", "Anguilla (+1264)"),
      ("AL", "Albania (+355)"),
      ("AM", "Armenia (+374)"),
      ("AO", "Angola (+244)"),
      ("AQ", "Antarctica (+672)"),
      ("AR", "Argentina (+54)"),
      ("AS", "American Samoa (+1684)"),
      ("AT", "Austria (+43)"),
      ("AU", "Australia (+61)"),
      ("AW", "Aruba (+297)"),
      ("AX", "Åland Islands (+358)"),
      ("AZ", "Azerbaijan (+994)"),
      ("BA", "Bosnia and Herzegovina (+387)"),
      ("BB", "Barbados (+1246)"),
      ("BD", "Bangladesh (+880)"),
      ("BE", "Belgium (+32)"),
      ("BF", "Burkina Faso (+226)"),
      ("BG", "Bulgaria (+359)"),
      ("BH", "Bahrain (+973)"),
      ("BI", "Burundi (+257)"),
      ("BJ", "Benin (+229)"),
      ("BL", "Saint Barthélemy (+590)"),
      ("BM", "Bermuda (+1441)"),
      ("BN", "Brunei (+673)"),
      ("BO", "Bolivia (+591)"),
      ("BQ", "Bonaire, Sint Eustatius and Saba (+599)"),
      ("BR", "Brazil (+55)"),
      ("BS", "Bahamas (+1242)"),
      ("BT", "Bhutan (+975)"),
      ("BV", "Bouvet Island (+47)"),
      ("BW", "Botswana (+267)"),
      ("BY", "Belarus (+375)"),
      ("BZ", "Belize (+501)"),
      ("CA", "Canada (+1)"),
      ("CC", "Cocos (Keeling) Islands (+61)"),
      ("CD", "Congo (+243)"),
      ("CF", "Central African Republic (+236)"),
      ("CG", "Congo (+242)"),
      ("CH", "Switzerland (+41)"),
      ("CI", "Côte d'Ivoire (+225)"),
      ("CK", "Cook Islands (+682)"),
      ("CL", "Chile (+56)"),
      ("CM", "Cameroon (+237)"),
      ("CN", "China (+86)"),
      ("CO", "Colombia (+57)"),
      ("CR", "Costa Rica (+506)"),
      ("CU", "Cuba (+53)"),
      ("CV", "Cape Verde (+238)"),
      ("CW", "Curaçao (+599)"),
      ("CX", "Christmas Island (+61)"),
      ("CY", "Cyprus (+357)"),
      ("CZ", "Czechia (+420)"),
      ("DE", "Germany (+49)"),
      ("DJ", "Djibouti (+253)"),
      ("DK", "Denmark (+45)"),
      ("DM", "Dominica (+1767)"),
      ("DO", "Dominican Republic (+1809)"),
      ("DZ", "Algeria (+213)"),
      ("EC", "Ecuador (+593)"),
      ("EE", "Estonia (+372)"),
      ("EG", "Egypt (+20)"),
      ("EH", "Western Sahara (+212)"),
      ("ER", "Eritrea (+291)"),
      ("ES", "Spain (+34)"),
      ("ET", "Ethiopia (+251)"),
      ("FI", "Finland (+358)"),
      ("FJ", "Fiji (+679)"),
      ("FK", "Falkland Islands (+500)"),
      ("FM", "Micronesia (+691)"),
      ("FO", "Faroe Islands (+298)"),
      ("FR", "France (+33)"),
      ("GA", "Gabon (+241)"),
      ("GB", "United Kingdom (+44)"),
      ("GD", "Grenada (+1473)"),
      ("GE", "Georgia (+995)"),
      ("GF", "French Guiana (+594)"),
      ("GG", "Guernsey (+44)"),
      ("GH", "Ghana (+233)"),
      ("GI", "Gibraltar (+350)"),
      ("GL", "Greenland (+299)"),
      ("GM", "Gambia (+220)"),
      ("GN", "Guinea (+224)"),
      ("GP", "Guadeloupe (+590)"),
      ("GQ", "Equatorial Guinea (+240)"),
      ("GR", "Greece (+30)"),
      ("GS", "South Georgia and the South Sandwich Islands (+500)"),
      ("GT", "Guatemala (+502)"),
      ("GU", "Guam (+1671)"),
      ("GW", "Guinea-Bissau (+245)"),
      ("GY", "Guyana (+592)"),
      ("HK", "Hong Kong (+852)"),
      ("HM", "Heard Island and McDonald Islands (+672)"),
      ("HN", "Honduras (+504)"),
      ("HR", "Croatia (+385)"),
      ("HT", "Haiti (+509)"),
      ("HU", "Hungary (+36)"),
      ("ID", "Indonesia (+62)"),
      ("IE", "Ireland (+353)"),
      ("IL", "Israel (+972)"),
      ("IM", "Isle of Man (+44)"),
      ("IN", "India (+91)"),
      ("IO", "British Indian Ocean Territory (+246)"),
      ("IQ", "Iraq (+964)"),
      ("IR", "Iran (+98)"),
      ("IS", "Iceland (+354)"),
      ("IT", "Italy (+39)"),
      ("JE", "Jersey (+44)"),
      ("JM", "Jamaica (+1876)"),
      ("JO", "Jordan (+962)"),
      ("JP", "Japan (+81)"),
      ("KE", "Kenya (+254)"),
      ("KG", "Kyrgyzstan (+996)"),
      ("KH", "Cambodia (+855)"),
      ("KI", "Kiribati (+686)"),
      ("KM", "Comoros (+269)"),
      ("KN", "Saint Kitts and Nevis (+1869)"),
      ("KP", "North Korea (+850)"),
      ("KR", "South Korea (+82)"),
      ("KW", "Kuwait (+965)"),
      ("KY", "Cayman Islands (+1345)"),
      ("KZ", "Kazakhstan (+7)"),
      ("LA", "Laos (+856)"),
      ("LB", "Lebanon (+961)"),
      ("LC", "Saint Lucia (+1758)"),
      ("LI", "Liechtenstein (+423)"),
      ("LK", "Sri Lanka (+94)"),
      ("LR", "Liberia (+231)"),
      ("LS", "Lesotho (+266)"),
      ("LT", "Lithuania (+370)"),
      ("LU", "Luxembourg (+352)"),
      ("LV", "Latvia (+371)"),
      ("LY", "Libya (+218)"),
      ("MA", "Morocco (+212)"),
      ("MC", "Monaco (+377)"),
      ("MD", "Moldova (+373)"),
      ("ME", "Montenegro (+382)"),
      ("MF", "Saint Martin (+590)"),
      ("MG", "Madagascar (+261)"),
      ("MH", "Marshall Islands (+692)"),
      ("MK", "North Macedonia (+389)"),
      ("ML", "Mali (+223)"),
      ("MM", "Myanmar (+95)"),
      ("MN", "Mongolia (+976)"),
      ("MO", "Macao (+853)"),
      ("MP", "Northern Mariana Islands (+1670)"),
      ("MQ", "Martinique (+596)"),
      ("MR", "Mauritania (+222)"),
      ("MS", "Montserrat (+1664)"),
      ("MT", "Malta (+356)"),
      ("MU", "Mauritius (+230)"),
      ("MV", "Maldives (+960)"),
      ("MW", "Malawi (+265)"),
      ("MX", "Mexico (+52)"),
      ("MY", "Malaysia (+60)"),
      ("MZ", "Mozambique (+258)"),
      ("NA", "Namibia (+264)"),
      ("NC", "New Caledonia (+687)"),
      ("NE", "Niger (+227)"),
      ("NF", "Norfolk Island (+672)"),
      ("NG", "Nigeria (+234)"),
      ("NI", "Nicaragua (+505)"),
      ("NL", "Netherlands (+31)"),
      ("NO", "Norway (+47)"),
      ("NP", "Nepal (+977)"),
      ("NR", "Nauru (+674)"),
      ("NU", "Niue (+683)"),
      ("NZ", "New Zealand (+64)"),
      ("OM", "Oman (+968)"),
      ("PA", "Panama (+507)"),
      ("PE", "Peru (+51)"),
      ("PF", "French Polynesia (+689)"),
      ("PG", "Papua New Guinea (+675)"),
      ("PH", "Philippines (+63)"),
      ("PK", "Pakistan (+92)"),
      ("PL", "Poland (+48)"),
      ("PM", "Saint Pierre and Miquelon (+508)"),
      ("PN", "Pitcairn (+872)"),
      ("PR", "Puerto Rico (+1939)"),
      ("PS", "Palestine (+970)"),
      ("PT", "Portugal (+351)"),
      ("PW", "Palau (+680)"),
      ("PY", "Paraguay (+595)"),
      ("QA", "Qatar (+974)"),
      ("RE", "Réunion (+262)"),
      ("RO", "Romania (+40)"),
      ("RS", "Serbia (+381)"),
      ("RU", "Russia (+7)"),
      ("RW", "Rwanda (+250)"),
      ("SA", "Saudi Arabia (+966)"),
      ("SB", "Solomon Islands (+677)"),
      ("SC", "Seychelles (+248)"),
      ("SD", "Sudan (+249)"),
      ("SE", "Sweden (+46)"),
      ("SG", "Singapore (+65)"),
      ("SH", "Saint Helena (+290)"),
      ("SI", "Slovenia (+386)"),
      ("SJ", "Svalbard and Jan Mayen (+47)"),
      ("SK", "Slovakia (+421)"),
      ("SL", "Sierra Leone (+232)"),
      ("SM", "San Marino (+378)"),
      ("SN", "Senegal (+221)"),
      ("SO", "Somalia (+252)"),
      ("SR", "Suriname (+597)"),
      ("SS", "South Sudan (+211)"),
      ("ST", "Sao Tome and Principe (+239)"),
      ("SV", "El Salvador (+503)"),
      ("SX", "Sint Maarten (+1721)"),
      ("SY", "Syria (+963)"),
      ("SZ", "Eswatini (+268)"),
      ("TC", "Turks and Caicos Islands (+1649)"),
      ("TD", "Chad (+235)"),
      ("TF", "French Southern Territories (+262)"),
      ("TG", "Togo (+228)"),
      ("TH", "Thailand (+66)"),
      ("TJ", "Tajikistan (+992)"),
      ("TK", "Tokelau (+690)"),
      ("TL", "Timor-Leste (+670)"),
      ("TM", "Turkmenistan (+993)"),
      ("TN", "Tunisia (+216)"),
      ("TO", "Tonga (+676)"),
      ("TR", "Turkey (+90)"),
      ("TT", "Trinidad and Tobago (+1868)"),
      ("TV", "Tuvalu (+688)"),
      ("TW", "Taiwan (+886)"),
      ("TZ", "Tanzania (+255)"),
      ("UA", "Ukraine (+380)"),
      ("UG", "Uganda (+256)"),
      ("UM", "U.S. Minor Outlying Islands (+1)"),
      ("US", "United States (+1)"),
      ("UY", "Uruguay (+598)"),
      ("UZ", "Uzbekistan (+998)"),
      ("VA", "Vatican City (+39)"),
      ("VC", "Saint Vincent and the Grenadines (+1784)"),
      ("VE", "Venezuela (+58)"),
      ("VG", "British Virgin Islands (+1284)"),
      ("VI", "U.S. Virgin Islands (+1340)"),
      ("VN", "Vietnam (+84)"),
      ("VU", "Vanuatu (+678)"),
      ("WF", "Wallis and Futuna (+681)"),
      ("WS", "Samoa (+685)"),
      ("XK", "Kosovo (+383)"),
      ("YE", "Yemen (+967)"),
      ("YT", "Mayotte (+262)"),
      ("ZA", "South Africa (+27)"),
      ("ZM", "Zambia (+260)"),
      ("ZW", "Zimbabwe (+263)"),
    ]
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default="KE")
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
# Create your models here.
class Kline(models.Model):
    pair = models.CharField(max_length=30, default= 'BTCUSDC')
    open_time = models.DateTimeField()
    close_time = models.DateTimeField()
    open_amount = models.DecimalField(decimal_places=50, max_digits=200)
    high = models.DecimalField(decimal_places=50, max_digits=200)
    low = models.DecimalField(decimal_places=50, max_digits=200)
    close_amount = models.DecimalField(decimal_places=50, max_digits=200)


class MpesaCallback(models.Model):
    merchant_request_id = models.CharField(max_length=255, unique=True)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    response_code = models.CharField(max_length=10)
    response_description = models.TextField()
    result_code = models.CharField(max_length=10)
    result_desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant_request_id} - {self.result_desc}"

# class InvestmentPlan(models.Model):
#     user = 
#     name = models.Charfield(max_length = 50)
#     daily_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
#     available_balance = models.DecimalField(max_digits=5, decimal_places=2)
#     purchase_limit = models.CharField(max_length = 100, default="no restrictions")
#     purchase_quantity = models.IntegerField(default=1)
#     rate = 
#     cycle_days = 
#     price = 


class InvestmentPlan(models.Model):
    PLAN_CHOICES = [
        ("AMATUER", "AMATUER"),
        ("BEGINNER", "BEGINNER"),
        ("INTERMIDIATE", "INTERMIDIATE"),
        ("LEGENDARY", "LEGENDARY"),
        ("PRO", "PRO"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length = 100, null=True)
    daily_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Stored as 2.30 for 2.3%
    cycle_days = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.price} USDT"
    
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

class Investment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey('InvestmentPlan', on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    db_end_date = models.DateTimeField(null=True, blank=True)  # Renamed to avoid conflict
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    duration_minutes = models.IntegerField(default=60)  # Consider using if needed
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    def __str__(self):
        plan_name = self.plan.name if self.plan else 'No Plan'
        return f"Investment {self.start_date.strftime('%Y-%m-%d %H:%M')} - {plan_name}"

    @property
    def end_date(self):
        """Calculate the end date based on the plan's cycle days."""
        if self.plan and self.start_date:
            return self.start_date + timedelta(days=self.plan.cycle_days)
        return None

    @property
    def time_remaining(self):
        """Calculate the time remaining until the investment ends."""
        if self.end_date:
            remaining = self.end_date - timezone.now()
            return max(timedelta(0), remaining)
        return timedelta(0)

    def process_completion(self):
        """Process the investment completion if the end date has been reached."""
        if self.is_completed or not self.end_date or not self.user or not self.plan:
            return  # Skip if already completed or required fields are missing

        if timezone.now() >= self.end_date:
            self.is_completed = True
            self.status = "completed"

            # Calculate profit using Decimal for precision
            plan_price = Decimal(str(self.plan.price))
            interest = Decimal(str(self.plan.daily_interest_rate))
            profit = plan_price * (interest / Decimal('100'))

            # Add to user's balance
            try:
                profile = self.user.profile
                profile.balance += plan_price + profit
                profile.save()
            except AttributeError:
                # Handle missing profile gracefully
                pass

            self.db_end_date = self.end_date  # Store the calculated end date
            self.save()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default='0.00')

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

    def deposit(self, amount):
        """Increase wallet balance by the deposit amount."""
        self.balance += amount
        self.save()


class DepositTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.status})"


class MpesaResponse(models.Model):
    merchant_request_id = models.CharField(max_length=255)
    checkout_request_id = models.CharField(max_length=255)
    response_code = models.CharField(max_length=10)
    response_description = models.TextField()
    customer_message = models.TextField()

    def __str__(self):
        return self.merchant_request_id



'''
[
  {
    code: "AD",
    name: "Andorra",
    dialCode: "+376",
    flag: "🇦🇩",
  },
  {
    code: "AE",
    name: "United Arab Emirates",
    dialCode: "+971",
    flag: "🇦🇪",
  },
  {
    code: "AF",
    name: "Afghanistan",
    dialCode: "+93",
    flag: "🇦🇫",
  },
  {
    code: "AG",
    name: "Antigua and Barbuda",
    dialCode: "+1268",
    flag: "🇦🇬",
  },
  {
    code: "AI",
    name: "Anguilla",
    dialCode: "+1264",
    flag: "🇦🇮",
  },
  {
    code: "AL",
    name: "Albania",
    dialCode: "+355",
    flag: "🇦🇱",
  },
  {
    code: "AM",
    name: "Armenia",
    dialCode: "+374",
    flag: "🇦🇲",
  },
  {
    code: "AO",
    name: "Angola",
    dialCode: "+244",
    flag: "🇦🇴",
  },
  {
    code: "AQ",
    name: "Antarctica",
    dialCode: "+672",
    flag: "🇦🇶",
  },
  {
    code: "AR",
    name: "Argentina",
    dialCode: "+54",
    flag: "🇦🇷",
  },
  {
    code: "AS",
    name: "American Samoa",
    dialCode: "+1684",
    flag: "🇦🇸",
  },
  {
    code: "AT",
    name: "Austria",
    dialCode: "+43",
    flag: "🇦🇹",
  },
  {
    code: "AU",
    name: "Australia",
    dialCode: "+61",
    flag: "🇦🇺",
  },
  {
    code: "AW",
    name: "Aruba",
    dialCode: "+297",
    flag: "🇦🇼",
  },
  {
    code: "AX",
    name: "Åland Islands",
    dialCode: "+358",
    flag: "🇦🇽",
  },
  {
    code: "AZ",
    name: "Azerbaijan",
    dialCode: "+994",
    flag: "🇦🇿",
  },
  {
    code: "BA",
    name: "Bosnia and Herzegovina",
    dialCode: "+387",
    flag: "🇧🇦",
  },
  {
    code: "BB",
    name: "Barbados",
    dialCode: "+1246",
    flag: "🇧🇧",
  },
  {
    code: "BD",
    name: "Bangladesh",
    dialCode: "+880",
    flag: "🇧🇩",
  },
  {
    code: "BE",
    name: "Belgium",
    dialCode: "+32",
    flag: "🇧🇪",
  },
  {
    code: "BF",
    name: "Burkina Faso",
    dialCode: "+226",
    flag: "🇧🇫",
  },
  {
    code: "BG",
    name: "Bulgaria",
    dialCode: "+359",
    flag: "🇧🇬",
  },
  {
    code: "BH",
    name: "Bahrain",
    dialCode: "+973",
    flag: "🇧🇭",
  },
  {
    code: "BI",
    name: "Burundi",
    dialCode: "+257",
    flag: "🇧🇮",
  },
  {
    code: "BJ",
    name: "Benin",
    dialCode: "+229",
    flag: "🇧🇯",
  },
  {
    code: "BL",
    name: "Saint Barthélemy",
    dialCode: "+590",
    flag: "🇧🇱",
  },
  {
    code: "BM",
    name: "Bermuda",
    dialCode: "+1441",
    flag: "🇧🇲",
  },
  {
    code: "BN",
    name: "Brunei",
    dialCode: "+673",
    flag: "🇧🇳",
  },
  {
    code: "BO",
    name: "Bolivia",
    dialCode: "+591",
    flag: "🇧🇴",
  },
  {
    code: "BQ",
    name: "Bonaire, Sint Eustatius and Saba",
    dialCode: "+599",
    flag: "🇧🇶",
  },
  {
    code: "BR",
    name: "Brazil",
    dialCode: "+55",
    flag: "🇧🇷",
  },
  {
    code: "BS",
    name: "Bahamas",
    dialCode: "+1242",
    flag: "🇧🇸",
  },
  {
    code: "BT",
    name: "Bhutan",
    dialCode: "+975",
    flag: "🇧🇹",
  },
  {
    code: "BV",
    name: "Bouvet Island",
    dialCode: "+47",
    flag: "🇧🇻",
  },
  {
    code: "BW",
    name: "Botswana",
    dialCode: "+267",
    flag: "🇧🇼",
  },
  {
    code: "BY",
    name: "Belarus",
    dialCode: "+375",
    flag: "🇧🇾",
  },
  {
    code: "BZ",
    name: "Belize",
    dialCode: "+501",
    flag: "🇧🇿",
  },
  {
    code: "CA",
    name: "Canada",
    dialCode: "+1",
    flag: "🇨🇦",
  },
  {
    code: "CC",
    name: "Cocos (Keeling) Islands",
    dialCode: "+61",
    flag: "🇨🇨",
  },
  {
    code: "CD",
    name: "Congo",
    dialCode: "+243",
    flag: "🇨🇩",
  },
  {
    code: "CF",
    name: "Central African Republic",
    dialCode: "+236",
    flag: "🇨🇫",
  },
  {
    code: "CG",
    name: "Congo",
    dialCode: "+242",
    flag: "🇨🇬",
  },
  {
    code: "CH",
    name: "Switzerland",
    dialCode: "+41",
    flag: "🇨🇭",
  },
  {
    code: "CI",
    name: "Côte d'Ivoire",
    dialCode: "+225",
    flag: "🇨🇮",
  },
  {
    code: "CK",
    name: "Cook Islands",
    dialCode: "+682",
    flag: "🇨🇰",
  },
  {
    code: "CL",
    name: "Chile",
    dialCode: "+56",
    flag: "🇨🇱",
  },
  {
    code: "CM",
    name: "Cameroon",
    dialCode: "+237",
    flag: "🇨🇲",
  },
  {
    code: "CN",
    name: "China",
    dialCode: "+86",
    flag: "🇨🇳",
  },
  {
    code: "CO",
    name: "Colombia",
    dialCode: "+57",
    flag: "🇨🇴",
  },
  {
    code: "CR",
    name: "Costa Rica",
    dialCode: "+506",
    flag: "🇨🇷",
  },
  {
    code: "CU",
    name: "Cuba",
    dialCode: "+53",
    flag: "🇨🇺",
  },
  {
    code: "CV",
    name: "Cape Verde",
    dialCode: "+238",
    flag: "🇨🇻",
  },
  {
    code: "CW",
    name: "Curaçao",
    dialCode: "+599",
    flag: "🇨🇼",
  },
  {
    code: "CX",
    name: "Christmas Island",
    dialCode: "+61",
    flag: "🇨🇽",
  },
  {
    code: "CY",
    name: "Cyprus",
    dialCode: "+357",
    flag: "🇨🇾",
  },
  {
    code: "CZ",
    name: "Czechia",
    dialCode: "+420",
    flag: "🇨🇿",
  },
  {
    code: "DE",
    name: "Germany",
    dialCode: "+49",
    flag: "🇩🇪",
  },
  {
    code: "DJ",
    name: "Djibouti",
    dialCode: "+253",
    flag: "🇩🇯",
  },
  {
    code: "DK",
    name: "Denmark",
    dialCode: "+45",
    flag: "🇩🇰",
  },
  {
    code: "DM",
    name: "Dominica",
    dialCode: "+1767",
    flag: "🇩🇲",
  },
  {
    code: "DO",
    name: "Dominican Republic",
    dialCode: "+1809",
    flag: "🇩🇴",
  },
  {
    code: "DZ",
    name: "Algeria",
    dialCode: "+213",
    flag: "🇩🇿",
  },
  {
    code: "EC",
    name: "Ecuador",
    dialCode: "+593",
    flag: "🇪🇨",
  },
  {
    code: "EE",
    name: "Estonia",
    dialCode: "+372",
    flag: "🇪🇪",
  },
  {
    code: "EG",
    name: "Egypt",
    dialCode: "+20",
    flag: "🇪🇬",
  },
  {
    code: "EH",
    name: "Western Sahara",
    dialCode: "+212",
    flag: "🇪🇭",
  },
  {
    code: "ER",
    name: "Eritrea",
    dialCode: "+291",
    flag: "🇪🇷",
  },
  {
    code: "ES",
    name: "Spain",
    dialCode: "+34",
    flag: "🇪🇸",
  },
  {
    code: "ET",
    name: "Ethiopia",
    dialCode: "+251",
    flag: "🇪🇹",
  },
  {
    code: "FI",
    name: "Finland",
    dialCode: "+358",
    flag: "🇫🇮",
  },
  {
    code: "FJ",
    name: "Fiji",
    dialCode: "+679",
    flag: "🇫🇯",
  },
  {
    code: "FK",
    name: "Falkland Islands",
    dialCode: "+500",
    flag: "🇫🇰",
  },
  {
    code: "FM",
    name: "Micronesia",
    dialCode: "+691",
    flag: "🇫🇲",
  },
  {
    code: "FO",
    name: "Faroe Islands",
    dialCode: "+298",
    flag: "🇫🇴",
  },
  {
    code: "FR",
    name: "France",
    dialCode: "+33",
    flag: "🇫🇷",
  },
  {
    code: "GA",
    name: "Gabon",
    dialCode: "+241",
    flag: "🇬🇦",
  },
  {
    code: "GB",
    name: "United Kingdom",
    dialCode: "+44",
    flag: "🇬🇧",
  },
  {
    code: "GD",
    name: "Grenada",
    dialCode: "+1473",
    flag: "🇬🇩",
  },
  {
    code: "GE",
    name: "Georgia",
    dialCode: "+995",
    flag: "🇬🇪",
  },
  {
    code: "GF",
    name: "French Guiana",
    dialCode: "+594",
    flag: "🇬🇫",
  },
  {
    code: "GG",
    name: "Guernsey",
    dialCode: "+44",
    flag: "🇬🇬",
  },
  {
    code: "GH",
    name: "Ghana",
    dialCode: "+233",
    flag: "🇬🇭",
  },
  {
    code: "GI",
    name: "Gibraltar",
    dialCode: "+350",
    flag: "🇬🇮",
  },
  {
    code: "GL",
    name: "Greenland",
    dialCode: "+299",
    flag: "🇬🇱",
  },
  {
    code: "GM",
    name: "Gambia",
    dialCode: "+220",
    flag: "🇬🇲",
  },
  {
    code: "GN",
    name: "Guinea",
    dialCode: "+224",
    flag: "🇬🇳",
  },
  {
    code: "GP",
    name: "Guadeloupe",
    dialCode: "+590",
    flag: "🇬🇵",
  },
  {
    code: "GQ",
    name: "Equatorial Guinea",
    dialCode: "+240",
    flag: "🇬🇶",
  },
  {
    code: "GR",
    name: "Greece",
    dialCode: "+30",
    flag: "🇬🇷",
  },
  {
    code: "GS",
    name: "South Georgia and the South Sandwich Islands",
    dialCode: "+500",
    flag: "🇬🇸",
  },
  {
    code: "GT",
    name: "Guatemala",
    dialCode: "+502",
    flag: "🇬🇹",
  },
  {
    code: "GU",
    name: "Guam",
    dialCode: "+1671",
    flag: "🇬🇺",
  },
  {
    code: "GW",
    name: "Guinea-Bissau",
    dialCode: "+245",
    flag: "🇬🇼",
  },
  {
    code: "GY",
    name: "Guyana",
    dialCode: "+592",
    flag: "🇬🇾",
  },
  {
    code: "HK",
    name: "Hong Kong",
    dialCode: "+852",
    flag: "🇭🇰",
  },
  {
    code: "HM",
    name: "Heard Island and McDonald Islands",
    dialCode: "+672",
    flag: "🇭🇲",
  },
  {
    code: "HN",
    name: "Honduras",
    dialCode: "+504",
    flag: "🇭🇳",
  },
  {
    code: "HR",
    name: "Croatia",
    dialCode: "+385",
    flag: "🇭🇷",
  },
  {
    code: "HT",
    name: "Haiti",
    dialCode: "+509",
    flag: "🇭🇹",
  },
  {
    code: "HU",
    name: "Hungary",
    dialCode: "+36",
    flag: "🇭🇺",
  },
  {
    code: "ID",
    name: "Indonesia",
    dialCode: "+62",
    flag: "🇮🇩",
  },
  {
    code: "IE",
    name: "Ireland",
    dialCode: "+353",
    flag: "🇮🇪",
  },
  {
    code: "IL",
    name: "Israel",
    dialCode: "+972",
    flag: "🇮🇱",
  },
  {
    code: "IM",
    name: "Isle of Man",
    dialCode: "+44",
    flag: "🇮🇲",
  },
  {
    code: "IN",
    name: "India",
    dialCode: "+91",
    flag: "🇮🇳",
  },
  {
    code: "IO",
    name: "British Indian Ocean Territory",
    dialCode: "+246",
    flag: "🇮🇴",
  },
  {
    code: "IQ",
    name: "Iraq",
    dialCode: "+964",
    flag: "🇮🇶",
  },
  {
    code: "IR",
    name: "Iran",
    dialCode: "+98",
    flag: "🇮🇷",
  },
  {
    code: "IS",
    name: "Iceland",
    dialCode: "+354",
    flag: "🇮🇸",
  },
  {
    code: "IT",
    name: "Italy",
    dialCode: "+39",
    flag: "🇮🇹",
  },
  {
    code: "JE",
    name: "Jersey",
    dialCode: "+44",
    flag: "🇯🇪",
  },
  {
    code: "JM",
    name: "Jamaica",
    dialCode: "+1876",
    flag: "🇯🇲",
  },
  {
    code: "JO",
    name: "Jordan",
    dialCode: "+962",
    flag: "🇯🇴",
  },
  {
    code: "JP",
    name: "Japan",
    dialCode: "+81",
    flag: "🇯🇵",
  },
  {
    code: "KE",
    name: "Kenya",
    dialCode: "+254",
    flag: "🇰🇪",
  },
  {
    code: "KG",
    name: "Kyrgyzstan",
    dialCode: "+996",
    flag: "🇰🇬",
  },
  {
    code: "KH",
    name: "Cambodia",
    dialCode: "+855",
    flag: "🇰🇭",
  },
  {
    code: "KI",
    name: "Kiribati",
    dialCode: "+686",
    flag: "🇰🇮",
  },
  {
    code: "KM",
    name: "Comoros",
    dialCode: "+269",
    flag: "🇰🇲",
  },
  {
    code: "KN",
    name: "Saint Kitts and Nevis",
    dialCode: "+1869",
    flag: "🇰🇳",
  },
  {
    code: "KP",
    name: "North Korea",
    dialCode: "+850",
    flag: "🇰🇵",
  },
  {
    code: "KR",
    name: "South Korea",
    dialCode: "+82",
    flag: "🇰🇷",
  },
  {
    code: "KW",
    name: "Kuwait",
    dialCode: "+965",
    flag: "🇰🇼",
  },
  {
    code: "KY",
    name: "Cayman Islands",
    dialCode: "+1345",
    flag: "🇰🇾",
  },
  {
    code: "KZ",
    name: "Kazakhstan",
    dialCode: "+7",
    flag: "🇰🇿",
  },
  {
    code: "LA",
    name: "Laos",
    dialCode: "+856",
    flag: "🇱🇦",
  },
  {
    code: "LB",
    name: "Lebanon",
    dialCode: "+961",
    flag: "🇱🇧",
  },
  {
    code: "LC",
    name: "Saint Lucia",
    dialCode: "+1758",
    flag: "🇱🇨",
  },
  {
    code: "LI",
    name: "Liechtenstein",
    dialCode: "+423",
    flag: "🇱🇮",
  },
  {
    code: "LK",
    name: "Sri Lanka",
    dialCode: "+94",
    flag: "🇱🇰",
  },
  {
    code: "LR",
    name: "Liberia",
    dialCode: "+231",
    flag: "🇱🇷",
  },
  {
    code: "LS",
    name: "Lesotho",
    dialCode: "+266",
    flag: "🇱🇸",
  },
  {
    code: "LT",
    name: "Lithuania",
    dialCode: "+370",
    flag: "🇱🇹",
  },
  {
    code: "LU",
    name: "Luxembourg",
    dialCode: "+352",
    flag: "🇱🇺",
  },
  {
    code: "LV",
    name: "Latvia",
    dialCode: "+371",
    flag: "🇱🇻",
  },
  {
    code: "LY",
    name: "Libya",
    dialCode: "+218",
    flag: "🇱🇾",
  },
  {
    code: "MA",
    name: "Morocco",
    dialCode: "+212",
    flag: "🇲🇦",
  },
  {
    code: "MC",
    name: "Monaco",
    dialCode: "+377",
    flag: "🇲🇨",
  },
  {
    code: "MD",
    name: "Moldova",
    dialCode: "+373",
    flag: "🇲🇩",
  },
  {
    code: "ME",
    name: "Montenegro",
    dialCode: "+382",
    flag: "🇲🇪",
  },
  {
    code: "MF",
    name: "Saint Martin",
    dialCode: "+590",
    flag: "🇲🇫",
  },
  {
    code: "MG",
    name: "Madagascar",
    dialCode: "+261",
    flag: "🇲🇬",
  },
  {
    code: "MH",
    name: "Marshall Islands",
    dialCode: "+692",
    flag: "🇲🇭",
  },
  {
    code: "MK",
    name: "North Macedonia",
    dialCode: "+389",
    flag: "🇲🇰",
  },
  {
    code: "ML",
    name: "Mali",
    dialCode: "+223",
    flag: "🇲🇱",
  },
  {
    code: "MM",
    name: "Myanmar",
    dialCode: "+95",
    flag: "🇲🇲",
  },
  {
    code: "MN",
    name: "Mongolia",
    dialCode: "+976",
    flag: "🇲🇳",
  },
  {
    code: "MO",
    name: "Macao",
    dialCode: "+853",
    flag: "🇲🇴",
  },
  {
    code: "MP",
    name: "Northern Mariana Islands",
    dialCode: "+1670",
    flag: "🇲🇵",
  },
  {
    code: "MQ",
    name: "Martinique",
    dialCode: "+596",
    flag: "🇲🇶",
  },
  {
    code: "MR",
    name: "Mauritania",
    dialCode: "+222",
    flag: "🇲🇷",
  },
  {
    code: "MS",
    name: "Montserrat",
    dialCode: "+1664",
    flag: "🇲🇸",
  },
  {
    code: "MT",
    name: "Malta",
    dialCode: "+356",
    flag: "🇲🇹",
  },
  {
    code: "MU",
    name: "Mauritius",
    dialCode: "+230",
    flag: "🇲🇺",
  },
  {
    code: "MV",
    name: "Maldives",
    dialCode: "+960",
    flag: "🇲🇻",
  },
  {
    code: "MW",
    name: "Malawi",
    dialCode: "+265",
    flag: "🇲🇼",
  },
  {
    code: "MX",
    name: "Mexico",
    dialCode: "+52",
    flag: "🇲🇽",
  },
  {
    code: "MY",
    name: "Malaysia",
    dialCode: "+60",
    flag: "🇲🇾",
  },
  {
    code: "MZ",
    name: "Mozambique",
    dialCode: "+258",
    flag: "🇲🇿",
  },
  {
    code: "NA",
    name: "Namibia",
    dialCode: "+264",
    flag: "🇳🇦",
  },
  {
    code: "NC",
    name: "New Caledonia",
    dialCode: "+687",
    flag: "🇳🇨",
  },
  {
    code: "NE",
    name: "Niger",
    dialCode: "+227",
    flag: "🇳🇪",
  },
  {
    code: "NF",
    name: "Norfolk Island",
    dialCode: "+672",
    flag: "🇳🇫",
  },
  {
    code: "NG",
    name: "Nigeria",
    dialCode: "+234",
    flag: "🇳🇬",
  },
  {
    code: "NI",
    name: "Nicaragua",
    dialCode: "+505",
    flag: "🇳🇮",
  },
  {
    code: "NL",
    name: "Netherlands",
    dialCode: "+31",
    flag: "🇳🇱",
  },
  {
    code: "NO",
    name: "Norway",
    dialCode: "+47",
    flag: "🇳🇴",
  },
  {
    code: "NP",
    name: "Nepal",
    dialCode: "+977",
    flag: "🇳🇵",
  },
  {
    code: "NR",
    name: "Nauru",
    dialCode: "+674",
    flag: "🇳🇷",
  },
  {
    code: "NU",
    name: "Niue",
    dialCode: "+683",
    flag: "🇳🇺",
  },
  {
    code: "NZ",
    name: "New Zealand",
    dialCode: "+64",
    flag: "🇳🇿",
  },
  {
    code: "OM",
    name: "Oman",
    dialCode: "+968",
    flag: "🇴🇲",
  },
  {
    code: "PA",
    name: "Panama",
    dialCode: "+507",
    flag: "🇵🇦",
  },
  {
    code: "PE",
    name: "Peru",
    dialCode: "+51",
    flag: "🇵🇪",
  },
  {
    code: "PF",
    name: "French Polynesia",
    dialCode: "+689",
    flag: "🇵🇫",
  },
  {
    code: "PG",
    name: "Papua New Guinea",
    dialCode: "+675",
    flag: "🇵🇬",
  },
  {
    code: "PH",
    name: "Philippines",
    dialCode: "+63",
    flag: "🇵🇭",
  },
  {
    code: "PK",
    name: "Pakistan",
    dialCode: "+92",
    flag: "🇵🇰",
  },
  {
    code: "PL",
    name: "Poland",
    dialCode: "+48",
    flag: "🇵🇱",
  },
  {
    code: "PM",
    name: "Saint Pierre and Miquelon",
    dialCode: "+508",
    flag: "🇵🇲",
  },
  {
    code: "PN",
    name: "Pitcairn",
    dialCode: "+872",
    flag: "🇵🇳",
  },
  {
    code: "PR",
    name: "Puerto Rico",
    dialCode: "+1939",
    flag: "🇵🇷",
  },
  {
    code: "PS",
    name: "Palestine",
    dialCode: "+970",
    flag: "🇵🇸",
  },
  {
    code: "PT",
    name: "Portugal",
    dialCode: "+351",
    flag: "🇵🇹",
  },
  {
    code: "PW",
    name: "Palau",
    dialCode: "+680",
    flag: "🇵🇼",
  },
  {
    code: "PY",
    name: "Paraguay",
    dialCode: "+595",
    flag: "🇵🇾",
  },
  {
    code: "QA",
    name: "Qatar",
    dialCode: "+974",
    flag: "🇶🇦",
  },
  {
    code: "RE",
    name: "Réunion",
    dialCode: "+262",
    flag: "🇷🇪",
  },
  {
    code: "RO",
    name: "Romania",
    dialCode: "+40",
    flag: "🇷🇴",
  },
  {
    code: "RS",
    name: "Serbia",
    dialCode: "+381",
    flag: "🇷🇸",
  },
  {
    code: "RU",
    name: "Russia",
    dialCode: "+7",
    flag: "🇷🇺",
  },
  {
    code: "RW",
    name: "Rwanda",
    dialCode: "+250",
    flag: "🇷🇼",
  },
  {
    code: "SA",
    name: "Saudi Arabia",
    dialCode: "+966",
    flag: "🇸🇦",
  },
  {
    code: "SB",
    name: "Solomon Islands",
    dialCode: "+677",
    flag: "🇸🇧",
  },
  {
    code: "SC",
    name: "Seychelles",
    dialCode: "+248",
    flag: "🇸🇨",
  },
  {
    code: "SD",
    name: "Sudan",
    dialCode: "+249",
    flag: "🇸🇩",
  },
  {
    code: "SE",
    name: "Sweden",
    dialCode: "+46",
    flag: "🇸🇪",
  },
  {
    code: "SG",
    name: "Singapore",
    dialCode: "+65",
    flag: "🇸🇬",
  },
  {
    code: "SH",
    name: "Saint Helena",
    dialCode: "+290",
    flag: "🇸🇭",
  },
  {
    code: "SI",
    name: "Slovenia",
    dialCode: "+386",
    flag: "🇸🇮",
  },
  {
    code: "SJ",
    name: "Svalbard and Jan Mayen",
    dialCode: "+47",
    flag: "🇸🇯",
  },
  {
    code: "SK",
    name: "Slovakia",
    dialCode: "+421",
    flag: "🇸🇰",
  },
  {
    code: "SL",
    name: "Sierra Leone",
    dialCode: "+232",
    flag: "🇸🇱",
  },
  {
    code: "SM",
    name: "San Marino",
    dialCode: "+378",
    flag: "🇸🇲",
  },
  {
    code: "SN",
    name: "Senegal",
    dialCode: "+221",
    flag: "🇸🇳",
  },
  {
    code: "SO",
    name: "Somalia",
    dialCode: "+252",
    flag: "🇸🇴",
  },
  {
    code: "SR",
    name: "Suriname",
    dialCode: "+597",
    flag: "🇸🇷",
  },
  {
    code: "SS",
    name: "South Sudan",
    dialCode: "+211",
    flag: "🇸🇸",
  },
  {
    code: "ST",
    name: "Sao Tome and Principe",
    dialCode: "+239",
    flag: "🇸🇹",
  },
  {
    code: "SV",
    name: "El Salvador",
    dialCode: "+503",
    flag: "🇸🇻",
  },
  {
    code: "SX",
    name: "Sint Maarten",
    dialCode: "+1721",
    flag: "🇸🇽",
  },
  {
    code: "SY",
    name: "Syria",
    dialCode: "+963",
    flag: "🇸🇾",
  },
  {
    code: "SZ",
    name: "Eswatini",
    dialCode: "+268",
    flag: "🇸🇿",
  },
  {
    code: "TC",
    name: "Turks and Caicos Islands",
    dialCode: "+1649",
    flag: "🇹🇨",
  },
  {
    code: "TD",
    name: "Chad",
    dialCode: "+235",
    flag: "🇹🇩",
  },
  {
    code: "TF",
    name: "French Southern Territories",
    dialCode: "+262",
    flag: "🇹🇫",
  },
  {
    code: "TG",
    name: "Togo",
    dialCode: "+228",
    flag: "🇹🇬",
  },
  {
    code: "TH",
    name: "Thailand",
    dialCode: "+66",
    flag: "🇹🇭",
  },
  {
    code: "TJ",
    name: "Tajikistan",
    dialCode: "+992",
    flag: "🇹🇯",
  },
  {
    code: "TK",
    name: "Tokelau",
    dialCode: "+690",
    flag: "🇹🇰",
  },
  {
    code: "TL",
    name: "Timor-Leste",
    dialCode: "+670",
    flag: "🇹🇱",
  },
  {
    code: "TM",
    name: "Turkmenistan",
    dialCode: "+993",
    flag: "🇹🇲",
  },
  {
    code: "TN",
    name: "Tunisia",
    dialCode: "+216",
    flag: "🇹🇳",
  },
  {
    code: "TO",
    name: "Tonga",
    dialCode: "+676",
    flag: "🇹🇴",
  },
  {
    code: "TR",
    name: "Turkey",
    dialCode: "+90",
    flag: "🇹🇷",
  },
  {
    code: "TT",
    name: "Trinidad and Tobago",
    dialCode: "+1868",
    flag: "🇹🇹",
  },
  {
    code: "TV",
    name: "Tuvalu",
    dialCode: "+688",
    flag: "🇹🇻",
  },
  {
    code: "TW",
    name: "Taiwan",
    dialCode: "+886",
    flag: "🇹🇼",
  },
  {
    code: "TZ",
    name: "Tanzania",
    dialCode: "+255",
    flag: "🇹🇿",
  },
  {
    code: "UA",
    name: "Ukraine",
    dialCode: "+380",
    flag: "🇺🇦",
  },
  {
    code: "UG",
    name: "Uganda",
    dialCode: "+256",
    flag: "🇺🇬",
  },
  {
    code: "UM",
    name: "U.S. Minor Outlying Islands",
    dialCode: "+1",
    flag: "🇺🇲",
  },
  {
    code: "US",
    name: "United States",
    dialCode: "+1",
    flag: "🇺🇸",
  },
  {
    code: "UY",
    name: "Uruguay",
    dialCode: "+598",
    flag: "🇺🇾",
  },
  {
    code: "UZ",
    name: "Uzbekistan",
    dialCode: "+998",
    flag: "🇺🇿",
  },
  {
    code: "VA",
    name: "Vatican City",
    dialCode: "+39",
    flag: "🇻🇦",
  },
  {
    code: "VC",
    name: "Saint Vincent and the Grenadines",
    dialCode: "+1784",
    flag: "🇻🇨",
  },
  {
    code: "VE",
    name: "Venezuela",
    dialCode: "+58",
    flag: "🇻🇪",
  },
  {
    code: "VG",
    name: "British Virgin Islands",
    dialCode: "+1284",
    flag: "🇻🇬",
  },
  {
    code: "VI",
    name: "U.S. Virgin Islands",
    dialCode: "+1340",
    flag: "🇻🇮",
  },
  {
    code: "VN",
    name: "Vietnam",
    dialCode: "+84",
    flag: "🇻🇳",
  },
  {
    code: "VU",
    name: "Vanuatu",
    dialCode: "+678",
    flag: "🇻🇺",
  },
  {
    code: "WF",
    name: "Wallis and Futuna",
    dialCode: "+681",
    flag: "🇼🇫",
  },
  {
    code: "WS",
    name: "Samoa",
    dialCode: "+685",
    flag: "🇼🇸",
  },
  {
    code: "XK",
    name: "Kosovo",
    dialCode: "+383",
    flag: "🇽🇰",
  },
  {
    code: "YE",
    name: "Yemen",
    dialCode: "+967",
    flag: "🇾🇪",
  },
  {
    code: "YT",
    name: "Mayotte",
    dialCode: "+262",
    flag: "🇾🇹",
  },
  {
    code: "ZA",
    name: "South Africa",
    dialCode: "+27",
    flag: "🇿🇦",
  },
  {
    code: "ZM",
    name: "Zambia",
    dialCode: "+260",
    flag: "🇿🇲",
  },
  {
    code: "ZW",
    name: "Zimbabwe",
    dialCode: "+263",
    flag: "🇿🇼",
  },
];'

'''