from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# sports/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

# Use Django's built-in JSONField for flexibility.
# For older Django versions, you might need to install a library.
from django.db.models import JSONField
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from apps.sport.models import Sport
from helper.modelHelper import Active_Status, Public_Status, Country_List, Governorates_List, Sport_Core_type, \
    Sport_Stat_Type, Gander_type, Position_List, Language_List, Tv_Type, Sport_Type, Match_Status
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()





class MonkCountry(models.Model):

    api_id = models.IntegerField(null=True, blank=True)
    continent = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    name_ar = models.CharField(max_length=100, null=True, blank=True)
    official_name = models.CharField(max_length=100, null=True, blank=True)
    fifa_name = models.CharField(max_length=100, null=True, blank=True)
    iso2 = models.CharField(max_length=100, null=True, blank=True)
    iso3 = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    image_path = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    borders = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MonkCountry-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MonkCountry, self).save(*args, **kwargs)

class MonkLeague(models.Model):
    """
    A generic model for a league or competition in any sport.
    """
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='leagues')
    name = models.CharField(_("League Name"), max_length=100)
    logo_url = models.URLField(_("Logo URL"), max_length=100, null=True, blank=True)

    # Source Data Management
    # This is crucial for tracking where the data came from.
    source_api = models.CharField(_("Source API"), max_length=50, db_index=True,
                                  help_text=_("e.g., 'sportmonks', 'internal_backend'"))
    source_id = models.CharField(_("Source ID"), max_length=100, db_index=True,
                                 help_text=_("The ID from the source API"))

    # Custom data fields for your employees
    custom_translation_name = models.CharField(_("Custom Translation Name"), max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("League")
        verbose_name_plural = _("Leagues")
        # Ensure that each league from a specific source is unique.
        unique_together = ('source_api', 'source_id')

    def __str__(self):
        return f"{self.name} ({self.sport.name})"


class MonkTeam(models.Model):
    """
    A generic model for a team in any sport.
    """
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(_("Team Name"), max_length=100)
    logo_url = models.URLField(_("Logo URL"), max_length=100, null=True, blank=True)

    # Source Data Management
    source_api = models.CharField(_("Source API"), max_length=50, db_index=True)
    source_id = models.CharField(_("Source ID"), max_length=100, db_index=True)

    # Custom data fields for your employees
    custom_translation_name = models.CharField(_("Custom Translation Name"), max_length=100, null=True, blank=True)
    custom_image_url = models.URLField(_("Custom Image URL"), max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        unique_together = ('source_api', 'source_id')

    def __str__(self):
        return f"{self.name} ({self.sport.name})"


class MonkMatch(models.Model):
    """
    A generic model for a match/fixture between two teams in any sport.
    """
    league = models.ForeignKey(MonkLeague, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(MonkTeam, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(MonkTeam, on_delete=models.CASCADE, related_name='away_matches')

    match_time = models.DateTimeField(_("Match Start Time"))
    status = models.CharField(_("Match Status"), max_length=50, help_text=_("e.g., NS, LIVE, FT, POST"))

    # Scores can be integers for most sports.
    home_score = models.IntegerField(_("Home Score"), null=True, blank=True)
    away_score = models.IntegerField(_("Away Score"), null=True, blank=True)

    # Use JSONField for flexible, sport-specific data
    events_data = JSONField(_("Events Data"), null=True, blank=True, help_text=_("Goals, cards, substitutions, etc."))
    statistics_data = JSONField(_("Statistics Data"), null=True, blank=True, help_text=_("Possession, shots, etc."))

    # Source Data Management
    source_api = models.CharField(_("Source API"), max_length=50, db_index=True)
    source_id = models.CharField(_("Source ID"), max_length=100, db_index=True)

    # Custom data fields for your employees
    custom_translation_name = models.CharField(_("Custom Translation Name"), max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("Match")
        verbose_name_plural = _("Matches")
        unique_together = ('source_api', 'source_id')
        ordering = ['match_time']

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} at {self.match_time.strftime('%Y-%m-%d %H:%M')}"

