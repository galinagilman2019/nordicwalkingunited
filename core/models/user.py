from django_countries.fields import LazyTypedChoiceField
from django.contrib.auth import models as auth_models
#from django.contrib.auth.models import Group
from django.db import models
from django_countries import countries
from core.models.managers.user import UserManager
from core.slack_client import invite_user_to_slack
from django.core.validators import FileExtensionValidator
from django_resized import ResizedImageField
AGERANGE = (
    (0, 'Under 18'),
    (18, '18-24'),
    (25, '25-34'),
    (35, '35-44'),
    (45, '45-54'),
    (55, '55-64'),
    (65, '65 or over'),
)

class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_blacklisted = models.BooleanField(default=False)
    avatar = ResizedImageField(
        size=[200,200],
        default='avatar.png',
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ],
    )

    username = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100,verbose_name='First Name', null=True)
    #country_user = models.CharField(max_length=200,null=True)
    country_user = models.CharField(max_length=200,verbose_name='Country', choices=countries, blank=True)

    bio = models.TextField(max_length=200,null=True, blank=True)
    address = models.CharField(max_length=30,verbose_name='Zip Code',blank=True)
    age_range = models.IntegerField(choices=AGERANGE,verbose_name='Age', default=0)
# NEW FIELDS:
    rules_accepted = models.BooleanField(default=False)
    rules_accepted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    #USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['username']
    class Meta:
        ordering = ['avatar']
        verbose_name = "Organizer"
        verbose_name_plural = "Organizers"
    def save(self, *args, **kwargs):
        if not self.name and self.first_name:
            self.name = f"{self.first_name} "
        super().save(*args, **kwargs)
    def invite_to_slack(self):
        invite_user_to_slack(self.email, self.first_name)

    def generate_password(self):
        password = User.objects.make_random_password()
        self.set_password(password)
        self.save()
        return password
        #

        #
    def add_to_organizers_group(self):
        try:
            group = group.objects.get(name="Organizers")
        except group.DoesNotExist:
            return

        self.groups.add(group)

    def __str__(self):
        status = "- (Organizer is Blacklisted)" if self.is_blacklisted else ""

        if not self.first_name and not self.last_name:
            return f"{self.email} {status}"
        return f"{self.get_full_name()} ({self.email}) {status}"

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
