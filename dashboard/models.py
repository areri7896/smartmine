from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import CASCADE


User = get_user_model()


# class WithdrawStatusTextChoices(models.TextChoices):
#     PENDING = "Processing"
#     COMPLETED = "Completed"
#     CANCELLED = "Cancelled"
#     FAILED = "Failed" 


class EmailSender(models.Model):
    receivers = models.ManyToManyField(User)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email to {self.receivers.count()} users - {self.subject}"

    def send_emails(self):
        for user in self.receivers.all():
            if user.email:
                send_mail(
                    subject=self.subject,
                    message=self.message,
                    from_email='ssmartmine@gmail.com',  # Change to your address
                    recipient_list=[user.email],
                    fail_silently=False,
                )

    def save(self, *args, **kwargs):
        # Determine if this is a new instance
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save the instance first to get a PK

        # If it's a new instance, send emails
        if is_new:
            self.send_emails()
    
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Investment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("paid", "Paid Out"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey('InvestmentPlan', on_delete=models.CASCADE, null=True)

    db_start_date = models.DateTimeField(null=True, blank=True)
    db_end_date = models.DateTimeField(null=True, blank=True)

    profit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_payout = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    # Daily profit tracking
    days_paid = models.IntegerField(default=0)
    total_days = models.IntegerField(default=0)
    last_profit_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Transaction(models.Model):

    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('investment', 'Investment'),
        ('trade', 'Trade'),
        ('exchange', 'Exchange'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="wallet_transactions")

    # Main transaction info
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")

    # Wallet balance impact
    balance_before = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    balance_after = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    # Optional external/internal reference
    reference_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    # Status of transaction
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="success")

    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['reference_id']),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | {self.amount} {self.currency}"


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
        ("Alpha Return CFD", "Alpha Return CFD"),
        ("Rapid Growth CFD", "Rapid Growth CFD"),
        ("CryptoFortress_CFD", "CryptoFortress_CFD"),
        ("AI-Powered_Profit_CFD", "AI-Powered_Profit_CFD"),
        ("Freedom_Fund_CFD", "Freedom_Fund_CFD"),
        ("Lagacy_Builder_CFD", "Lagacy_Builder_CFD"),
        ("Platimum_Wealth_CFD", "Platimum_Wealth_CFD"),
        ("SmartReturns_Algorithm", "SmartReturns_Algorithm"),
        ("Compounding_Fortune_CFD", "Compounding_Fortune_CFD"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length = 1000, null=True)
    daily_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Stored as 2.30 for 2.3%
    cycle_days = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.price} USDT"
    
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# class Investment(models.Model):
#     STATUS_CHOICES = [
#         ("active", "Active"),
#         ("completed", "Completed"),
#     ]

#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
#     plan = models.ForeignKey('InvestmentPlan', on_delete=models.CASCADE, null=True, blank=True)
#     start_date = models.DateTimeField(auto_now_add=True, null=True)
#     db_end_date = models.DateTimeField(null=True, blank=True)  # Renamed to avoid conflict
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     duration_minutes = models.IntegerField(default=60)  # Consider using if needed
#     is_completed = models.BooleanField(default=False)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

#     def __str__(self):
#         plan_name = self.plan.name if self.plan else 'No Plan'
#         return f"Investment {self.start_date.strftime('%Y-%m-%d %H:%M')} - {plan_name}"

#     @property
#     def end_date(self):
#         """Calculate the end date based on the plan's cycle days."""
#         if self.plan and self.start_date:
#             return self.start_date + timedelta(days=self.plan.cycle_days)
        

#     @property
#     def time_remaining(self):
#         """Calculate the time remaining until the investment ends."""
#         if self.end_date:
#             remaining = self.end_date - timezone.now()
#             return max(timedelta(0), remaining)
#         return timedelta(0)

#     def process_completion(self):
#         """Process the investment completion if the end date has been reached."""
#         if self.is_completed or not self.end_date or not self.user or not self.plan:
#             return  # Skip if already completed or required fields are missing

#         if timezone.now() >= self.end_date:
#             self.is_completed = True
#             self.status = "completed"

#             # Calculate profit using Decimal for precision
#             plan_price = Decimal(str(self.plan.price))
#             interest = Decimal(str(self.plan.daily_interest_rate))
#             profit = plan_price * (interest / Decimal('100'))

#             # Add to user's balance
#             try:
#                 wallet.user = self.user.profile
#                 wallet.balance += plan_price + profit
#                 wallet.save()
#             except AttributeError:
#                 # Handle missing profile gracefully
#                 pass

#             self.db_end_date = self.end_date  # Store the calculated end date
#             self.save()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default='0.00')
    balance_usd = models.CharField(max_length=20, default='0.00', null=True, blank=True)  # Assuming this is a string for USD balance

    def __str__(self):
            """Return the user's full name, or username if full name is not available."""
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            return full_name if full_name else self.user.username


    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = 0  # Set a default value
        if self.balance < 0:
            raise ValueError("Balance cannot be negative")
        super().save(*args, **kwargs)

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
    