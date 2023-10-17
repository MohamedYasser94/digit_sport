from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from helper.modelHelper import Active_Status, Attendees_History_Type, Public_Status, Country_List, Governorates_List, \
    Clinic_Category, Sport_Core_type, Sport_Stat_Type, Gander_type, Position_List, Language_List, Tv_Type
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'EventCategory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Category, self).save(*args, **kwargs)

class SportCategories(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='sport_children', on_delete=models.CASCADE)
    title = models.CharField(max_length=20,validators=[UnicodeUsernameValidator])
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'CAT{get_random_string(5).upper()}'
            self.slug = slugify(self.title)
        super(SportCategories, self).save(*args, **kwargs)


class Sport(models.Model):
    title = models.CharField(max_length=40, unique=True)
    category = models.ForeignKey(SportCategories, on_delete=models.CASCADE, related_name='sport_category')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'sport'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("sport_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Sport, self).save(*args, **kwargs)

class Leagues(models.Model):
    name = models.CharField(max_length=40, unique=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_league')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_league')
    country = models.CharField(max_length=20, choices=Country_List, default='Egypt', null=True, blank=True)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    last_played_at = models.DateTimeField(null=True, blank=True)
    next_played_at = models.DateTimeField(null=True, blank=True)
    has_jersey = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'league'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("league_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'League-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Leagues, self).save(*args, **kwargs)


class Season(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_season')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_season')
    tie_breaker_rule = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    name = models.CharField(max_length=40, unique=True)
    finished =  models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    pending = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'season'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Season, self).save(*args, **kwargs)

class Stages(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_stage')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_stage')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_stage')
    type = models.CharField(max_length=200, choices=Sport_Core_type, default='Other', null=True, blank=True)
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=200, unique=True)
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'stage'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Stages, self).save(*args, **kwargs)

class Group(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_group')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_group')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_group')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_group')
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=200, unique=True)
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'group'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Group, self).save(*args, **kwargs)


class Aggregate(models.Model):

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_aggregate')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_aggregate')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_aggregate')
    state = models.CharField(max_length=100,  null=True, blank=True)
    code = models.CharField(max_length=100,  null=True, blank=True)
    type = models.CharField(max_length=20, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'aggregate'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Aggregate, self).save(*args, **kwargs)



class Round(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_round')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_round')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_round')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_round')
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=200, unique=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'round'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Round, self).save(*args, **kwargs)


class Venues(models.Model):
    country = models.CharField(max_length=20, choices=Country_List, default='Egypt', null=True, blank=True)
    city = models.CharField(max_length=20, choices=Governorates_List, default='Cairo', null=True, blank=True)
    name = models.CharField(max_length=40, unique=True)
    short_code = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=100,  null=True, blank=True)
    address = models.CharField(max_length=200,  null=True, blank=True)
    zipcode = models.CharField(max_length=100,  null=True, blank=True)
    latitude = models.CharField(max_length=100,  null=True, blank=True)
    longitude = models.CharField(max_length=100,  null=True, blank=True)
    capacity = models.CharField(max_length=100,  null=True, blank=True)
    opened = models.CharField(max_length=100,  null=True, blank=True)
    surface = models.CharField(max_length=100,  null=True, blank=True)
    national_team = models.CharField(max_length=100,  null=True, blank=True)
    club_team = models.CharField(max_length=100,  null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'venue'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Venues, self).save(*args, **kwargs)

class SportState(models.Model):
    name = models.CharField(max_length=100,  null=True, blank=True)
    short_name = models.CharField(max_length=100,  null=True, blank=True)
    developer_name = models.CharField(max_length=100,  null=True, blank=True)
    state = models.CharField(max_length=100,  null=True, blank=True)
    code = models.CharField(max_length=100,  null=True, blank=True)
    type = models.CharField(max_length=20, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'sport type'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SportState, self).save(*args, **kwargs)

class Fixtures(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_fixture')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_fixture')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_fixture')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_fixture')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_fixture')
    aggregate = models.ForeignKey(Aggregate, on_delete=models.CASCADE, related_name='aggregate_fixture')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_fixture')
    state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_fixture')
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_fixture')
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, unique=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    result_info = models.CharField(max_length=100,  null=True, blank=True)
    leg = models.CharField(max_length=100,  null=True, blank=True)
    details = models.TextField( null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    placeholder = models.CharField(max_length=100,  null=True, blank=True)
    has_odds = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at_timestamp = models.IntegerField(null=True, blank=True)
    time_status = models.CharField(max_length=100,  null=True, blank=True)
    time_status_code = models.CharField(max_length=100,  null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    extra_minute = models.IntegerField(null=True, blank=True)
    extra_time = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100,  null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'fixture'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Fixtures, self).save(*args, **kwargs)


class LiveScores(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_live_scores')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_live_scores')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_live_scores')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_live_scores')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_live_scores')
    aggregate = models.ForeignKey(Aggregate, on_delete=models.CASCADE, related_name='aggregate_live_scores')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_live_scores')
    sport_state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_live_scores')
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_live_scores')
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, unique=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    result_info = models.CharField(max_length=100,  null=True, blank=True)
    leg = models.CharField(max_length=100,  null=True, blank=True)
    details = models.TextField( null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    placeholder = models.CharField(max_length=100,  null=True, blank=True)
    has_odds = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at_timestamp = models.IntegerField(null=True, blank=True)
    states = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'live scores'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(LiveScores, self).save(*args, **kwargs)




class Teams(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_team')
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_team')
    gender =models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    short_code = models.CharField(max_length=100, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    founded = models.CharField(max_length=100, null=True, blank=True)
    club_color_1 = models.CharField(max_length=100, null=True, blank=True)
    club_color_2 = models.CharField(max_length=100, null=True, blank=True)
    club_color_3 = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    placeholder = models.CharField(max_length=100, null=True, blank=True)
    last_played_at = models.DateTimeField(null=True, blank=True)
    next_played_at = models.DateTimeField(null=True, blank=True)
    has_jersey = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'team'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Teams, self).save(*args, **kwargs)


class Statistics(models.Model):
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_statistics')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_statistics')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_statistics')
    has_values = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)


class Standings(models.Model):
    participant = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='participant_standings')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_standings')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_standings')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_standings')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_standings')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_standings')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_standings')
    standing_rule = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'standing'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Standings, self).save(*args, **kwargs)


class LiveStandings(models.Model):
    participant = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='participant_live_standings')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_live_standings')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_live_standings')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_live_standings')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_live_standings')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_live_standings')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_live_standings')
    standing_rule = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'live standing'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Live-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(LiveStandings, self).save(*args, **kwargs)


class Schedules(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_schedule')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_schedule')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_schedule')
    sport_state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_live_scores')
    name = models.CharField(max_length=100, unique=True)
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    game_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'schedule'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Schedule-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Schedules, self).save(*args, **kwargs)


class Players(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_player')
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    nationality = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    city = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    common_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    height = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'player'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Player-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Players, self).save(*args, **kwargs)


class News(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    url = models.URLField(max_length=200, null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'news'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'News-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(News, self).save(*args, **kwargs)


class Seasons(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_season')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_season')
    name = models.CharField(max_length=100, null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=100, null=True, blank=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    pending = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'seasons'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Season-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Seasons, self).save(*args, **kwargs)


class Squads(models.Model):
    transfer = models.CharField(max_length=100, null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_squad')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_squad')
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    captain = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    loan = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'squad'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Squad-{get_random_string(5).upper()}'
            self.code = code
        super(Squads, self).save(*args, **kwargs)

class TVStations(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    language = models.CharField(max_length=100, choices=Language_List, default='Arabic', null=True, blank=True)
    url = models.URLField(max_length=450, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=100,choices=Tv_Type,default='Tv', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'tv station'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'TV-{get_random_string(5).upper()}'
            self.code = code
        super(TVStations, self).save(*args, **kwargs)



class Coaches(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_coach')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_coach')
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    nationality = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    city = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    common_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    height = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'coach'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Coach-{get_random_string(5).upper()}'
            self.code = code
        super(Coaches, self).save(*args, **kwargs)


class TopScorers(models.Model):
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_top_scorers')
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_top_scorers')
    type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    participant_type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    participant = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'top scorer'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'TopScorer-{get_random_string(5).upper()}'
            self.code = code
        super(TopScorers, self).save(*args, **kwargs)



class Rounds(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_round')
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_round')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_round')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_round')
    name = models.CharField(max_length=100, null=True, blank=True)
    finished = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'round'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Round-{get_random_string(5).upper()}'
            self.code = code
        super(Rounds, self).save(*args, **kwargs)


class Rivals(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_rival')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_rival')
    rival = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rival_rival')
    code= models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'rival'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Rival-{get_random_string(5).upper()}'
            self.code = code
        super(Rivals, self).save(*args, **kwargs)


class Commentaries(models.Model):
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_commentary')
    comment = models.TextField(null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    extra_minute = models.IntegerField(null=True, blank=True)
    is_goal = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    important = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'commentary'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Commentary-{get_random_string(5).upper()}'
            self.code = code
        super(Commentaries, self).save(*args, **kwargs)



class Referees(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_referee')
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    city = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    common_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    height = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'referee'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Referee-{get_random_string(5).upper()}'
            self.code = code
        super(Referees, self).save(*args, **kwargs)


class Transfers(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_transfer')
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_transfer')
    type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    from_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='from_team_transfer')
    to_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='to_team_transfer')
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    career_ended = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    free_transfer = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    market_value = models.CharField(max_length=100, null=True, blank=True)
    market_value_currency = models.CharField(max_length=100, null=True, blank=True)
    fee = models.CharField(max_length=100, null=True, blank=True)
    completed = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    amount = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('title',)
        verbose_name = 'transfer'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'Transfer-{get_random_string(5).upper()}'
            self.code = code
        super(Transfers, self).save(*args, **kwargs)



class PreMatchOdds(models.Model):
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_pre_match_odds')
    market = models.CharField(max_length=100, null=True, blank=True)
    bookmaker = models.CharField(max_length=100, null=True, blank=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    values = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True)
    market_description = models.CharField(max_length=100, null=True, blank=True)
    probability = models.CharField(max_length=100, null=True, blank=True)
    dp3 = models.CharField(max_length=100, null=True, blank=True)
    fractional = models.CharField(max_length=100, null=True, blank=True)
    american = models.CharField(max_length=100, null=True, blank=True)
    participants = models.CharField(max_length=100, null=True, blank=True)
    original_label = models.CharField(max_length=100, null=True, blank=True)
    latest_bookmaker_update = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('title',)
        verbose_name = 'pre match odd'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'PreMatchOdd-{get_random_string(5).upper()}'
            self.code = code
        super(PreMatchOdds, self).save(*args, **kwargs)


class InPlayOdds(models.Model):
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_in_play_odds')
    market = models.CharField(max_length=100, null=True, blank=True)
    bookmaker = models.CharField(max_length=100, null=True, blank=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    values = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True)
    market_description = models.CharField(max_length=100, null=True, blank=True)
    probability = models.CharField(max_length=100, null=True, blank=True)
    dp3 = models.CharField(max_length=100, null=True, blank=True)
    fractional = models.CharField(max_length=100, null=True, blank=True)
    american = models.CharField(max_length=100, null=True, blank=True)
    participants = models.CharField(max_length=100, null=True, blank=True)
    winning = models.CharField(max_length=100, null=True, blank=True)
    suspended = models.CharField(max_length=100, null=True, blank=True)
    stopped = models.CharField(max_length=100, null=True, blank=True)
    total   = models.CharField(max_length=100, null=True, blank=True)
    handicap = models.CharField(max_length=100, null=True, blank=True)
    latest_bookmaker_update = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'in play odd'
        # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code:
            code = f'InPlayOdd-{get_random_string(5).upper()}'
            self.code = code
        super(InPlayOdds, self).save(*args, **kwargs)