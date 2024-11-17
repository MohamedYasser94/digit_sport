from datetime import timezone

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

from helper.modelHelper import *
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()


class SportCategory(MPTTModel):
    sender_model = models.ForeignKey(ContentType,related_name='sport_category_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_category_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_category_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='sport_children', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, validators=[UnicodeUsernameValidator])
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=200, choices=Active_Status,default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'category'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['name']

    class TranslatableMeta:
        fields = ['name', ]

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SportCategory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SportCategory, self).save(*args, **kwargs)


class Sport(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=200, choices=Sport_Type, default='Football', null=True, blank=True)
    category = models.ForeignKey(SportCategory, on_delete=models.CASCADE, related_name='sport_category',blank=True, null=True)
    country = models.CharField(max_length=200, choices=Country_List, default='', null=True, blank=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'sport'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['name']

    class TranslatableMeta:
        fields = ['name', ]

    def get_absolute_url(self):
        return reverse("sport_list")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Sport, self).save(*args, **kwargs)


class Leagues(models.Model):
    api_id = models.CharField(max_length=200, null=True, blank=True,unique=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_league_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_league_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_league_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=200)
    name_tr = models.CharField(max_length=200, null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_league', null=True, blank=True)
    category = models.ForeignKey(SportCategory, on_delete=models.CASCADE, related_name='category_league', null=True, blank=True)
    api_category = models.CharField(max_length=200,  default='league', null=True, blank=True)
    sub_category = models.ForeignKey(SportCategory, on_delete=models.CASCADE, related_name='sub_category_league', null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=200, choices=Country_List, default='Egypt', null=True, blank=True)
    api_country = models.CharField(max_length=200, choices=Country_List, default='Egypt', null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    short_code = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    country_image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=200,  default='league', null=True, blank=True)
    sub_type = models.CharField(max_length=200,  default='domestic', null=True, blank=True)
    currentseason = models.CharField(max_length=200,  default='2021', null=True, blank=True)

    last_played_at = models.DateTimeField(null=True, blank=True)
    next_played_at = models.DateTimeField(null=True, blank=True)
    has_jerseys = models.BooleanField(default=True)
    api_active = models.BooleanField(default=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'League-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Leagues, self).save(*args, **kwargs)


class Season(models.Model):
    api_id = models.CharField(max_length=200, null=True, blank=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_season_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_season_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_season_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_season', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_season', null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    title =models.CharField(max_length=100)
    name = models.CharField(max_length=40)
    keyword = models.TextField(null=True, blank=True)
    finished =models.BooleanField(default=False)
    pending = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)
    starting_at = models.DateField(null=True, blank=True)
    ending_at = models.DateField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.BooleanField(default=False,null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'season'  # verbose_name_plural = 'categories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Season-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Season, self).save(*args, **kwargs)


class Stages(models.Model):
    api_id = models.CharField(max_length=200, null=True, blank=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_stage_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_stage_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_stage_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_stage', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_stage', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_stage', null=True, blank=True)
    type = models.CharField(max_length=200, choices=Sport_Core_type, default='Other', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    short_name = models.CharField(max_length=200,null=True, blank=True )
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.BooleanField(default=False)
    tie_breaker_rule = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'stage'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Stages, self).save(*args, **kwargs)


class Group(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_group_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_group_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_group_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_group', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_group', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_group', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_group', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    short_name = models.CharField(max_length=200, null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True,
                                             blank=True)
    tie_breaker_rule = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'group'  # verbose_name_plural = 'categories'

    def __str__(self):
        return self.name + ' ' + self.league.name + '' +self.season.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Group, self).save(*args, **kwargs)


class Aggregate(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_aggregate_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_aggregate_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_aggregate_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_aggregate', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_aggregate', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_aggregate', null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=200, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'aggregate'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Aggregate, self).save(*args, **kwargs)


class Round(models.Model):
    api_id = models.CharField(max_length=200, null=True, blank=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_round_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_round_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_round_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_rounds', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='sport_groups', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_rounds', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_rounds', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_rounds', null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    short_name = models.CharField(max_length=200, null=True, blank=True)
    finished = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    standings_recalculated_at = models.DateTimeField(null=True, blank=True)
    games_in_current_week = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True,
                                             blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        # return f'(R-{self.name})' +  f'(D-{self.starting_at.day})' + self.league.name

        return f'(R-{self.name})' + f'(G-{self.group.name})' + f'(D-{self.starting_at.day})' + self.league.name

    class Meta:
        ordering = ('starting_at',)
        verbose_name = 'round'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Round-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Round, self).save(*args, **kwargs)


class Venues(models.Model):
    api_id = models.CharField(max_length=200, null=True, blank=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_venue_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_venue_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_venue_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=40, unique=True)
    keyword = models.TextField( blank=True, null=True)
    country = models.CharField(max_length=200, choices=Country_List, default='Egypt', null=True, blank=True)
    api_country = models.CharField(max_length=200,  null=True, blank=True)
    city = models.CharField(max_length=200, choices=Governorates_List, default='Cairo', null=True, blank=True)
    city_name = models.CharField(max_length=200,  null=True, blank=True)
    api_city = models.CharField(max_length=200,  null=True, blank=True)
    short_code = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    zipcode = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    capacity = models.CharField(max_length=100, null=True, blank=True)
    opened = models.CharField(max_length=100, null=True, blank=True)
    surface = models.CharField(max_length=100, null=True, blank=True)
    national_team = models.BooleanField(default=False)
    club_team = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'venue'  # verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Venues, self).save(*args, **kwargs)


class SportState(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_state_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_state_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_state_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    developer_name = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=200, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'sport type'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SportState, self).save(*args, **kwargs)


class Fixtures(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_fixture_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_fixture_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_fixture_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_fixture', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_fixture', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_fixture', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_fixture', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_fixture', null=True, blank=True)
    aggregate = models.ForeignKey(Aggregate, on_delete=models.CASCADE, related_name='aggregate_fixture', null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_fixture', null=True, blank=True)
    state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_fixture', null=True, blank=True)
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_fixture', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, unique=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    result_info = models.CharField(max_length=100, null=True, blank=True)
    leg = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    placeholder = models.CharField(max_length=100, null=True, blank=True)
    has_odds = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at_timestamp = models.IntegerField(null=True, blank=True)
    time_status = models.CharField(max_length=100, null=True, blank=True)
    time_status_code = models.CharField(max_length=100, null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    extra_minute = models.IntegerField(null=True, blank=True)
    extra_time = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'fixture'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Fixtures, self).save(*args, **kwargs)


class LiveScores(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_live_score_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_live_score_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_live_score_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_live_scores', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_live_scores', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_live_scores', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_live_scores', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_live_scores', null=True, blank=True)
    aggregate = models.ForeignKey(Aggregate, on_delete=models.CASCADE, related_name='aggregate_live_scores', null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_live_scores', null=True, blank=True)
    sport_state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_live_scores', null=True, blank=True)
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_live_scores', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=100, unique=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    result_info = models.CharField(max_length=100, null=True, blank=True)
    leg = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    placeholder = models.CharField(max_length=100, null=True, blank=True)
    has_odds = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at_timestamp = models.IntegerField(null=True, blank=True)
    states = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=200, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'live scores'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(LiveScores, self).save(*args, **kwargs)

class Clubs(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_club_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_club_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_club_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=100, unique=True)
    keyword = models.TextField(null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_club', null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    country_image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    founded = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'club'

    def __str__(self):
        return  self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Clubs-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Clubs, self).save(*args, **kwargs)



class Teams(models.Model):
    api_id = models.IntegerField(null=True, blank=True,default=0 )
    sender_model = models.ForeignKey(ContentType,related_name='sport_team_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_team_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_team_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=100,)
    name_tr = models.CharField(max_length=100, null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_team', null=True, blank=True)
    club = models.ForeignKey(Clubs, on_delete=models.CASCADE, related_name='clubs_team', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_team', null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    api_country = models.CharField(max_length=100, null=True, blank=True)
    venue = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_team', null=True, blank=True)
    api_venue = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    short_code = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path, default='image')
    image_path = models.URLField(blank=True, null=True,default='url')
    country_image = models.ImageField(blank=True, null=True, upload_to=get_file_path, default='other/f8567c03-9b95-461b-9190-65d9603487c8.jpg')
    url = models.URLField(blank=True, null=True)
    founded = models.CharField(max_length=100, null=True, blank=True,default='founded')
    club_color_1 = models.CharField(max_length=100, null=True, blank=True)
    club_color_2 = models.CharField(max_length=100, null=True, blank=True)
    club_color_3 = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    placeholder = models.BooleanField(default=False,null=True, blank=True)
    last_played_at = models.DateTimeField(null=True, blank=True)
    next_played_at = models.DateTimeField(null=True, blank=True)
    has_jersey = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    player_count = models.IntegerField(null=True, blank=True,default=0)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'team'  # verbose_name_plural = 'categories'

    def __str__(self):
        return f"{self.name}-{self.sport}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Teams-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Teams, self).save(*args, **kwargs)


class Statistics(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_statistics_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_statistics_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_statistics_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_statistics', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_statistics', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_statistics', null=True, blank=True)
    has_values = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)


class Standings(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_standings_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_standings_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_standings_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    participant = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='participant_standings', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_standings', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_standings', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_standings', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_standings', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_standings', null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_standings', null=True, blank=True)
    standing_rule = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'standing'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Standings, self).save(*args, **kwargs)


class LiveStandings(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_live_standings_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_live_standings_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_live_standings_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    participant = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='participant_live_standings', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_live_standings', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_live_standings', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_live_standings', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_live_standings', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_live_standings', null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_live_standings', null=True, blank=True)
    standing_rule = models.CharField(max_length=100, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'live standing'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Live-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(LiveStandings, self).save(*args, **kwargs)


class Schedules(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_schedules_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_schedules_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_schedules_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_schedules', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_schedules', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_schedules', null=True, blank=True)
    sport_state = models.ForeignKey(SportState, on_delete=models.CASCADE, related_name='state_schedules_scores', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    sort_order = models.IntegerField(null=True, blank=True)
    finished = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    is_current = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    starting_at = models.DateTimeField(null=True, blank=True)
    ending_at = models.DateTimeField(null=True, blank=True)
    game_in_current_week = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    tie_breaker_rule = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'schedule'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Schedule-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Schedules, self).save(*args, **kwargs)


class  Players(models.Model):
    api_id = models.IntegerField(null=True, blank=True)
    sender_model = models.ForeignKey(ContentType,related_name='sport_player_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_player_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_player_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    team = models.ForeignKey(Teams , on_delete=models.CASCADE, null=True, blank=True)
    common_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    short_code = models.CharField(max_length=100, null=True, blank=True)
    keyword = models.TextField(null=True,blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_player', null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    api_country = models.CharField(max_length=100, null=True, blank=True)
    api_nationality = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    city = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    api_city = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    number =  models.CharField(max_length=100, null=True, blank=True)
    api_position = models.CharField(max_length=100, null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True,
                                         blank=True)
    api_detailed_position = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100,  null=True, blank=True)
    ratings  = models.CharField(max_length=100,  null=True, blank=True,default='0')

    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    height = models.CharField(max_length=100, null=True, blank=True)
    age = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    in_team = models.CharField(max_length=200, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    creat_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'player'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Player-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Players, self).save(*args, **kwargs)



class Squads(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_squad_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_squad_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_squad_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    transfer = models.CharField(max_length=100, null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_squad', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_squad', null=True, blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True,
                                         blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    captain = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    loan = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'squad'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Squad-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Squads, self).save(*args, **kwargs)


class TVStations(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_tv_station_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_tv_station_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_tv_station_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    language = models.CharField(max_length=100, choices=Language_List, default='Arabic', null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=100, choices=Tv_Type, default='Tv', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'tv station'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TV-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TVStations, self).save(*args, **kwargs)


class Coaches(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_coach_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_coach_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_coach_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_coach', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_coach', null=True, blank=True)
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
    image_path = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    height = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'coach'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Coach-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Coaches, self).save(*args, **kwargs)


class TopScorers(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_top_scorer_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_top_scorer_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_top_scorer_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_top_scorers', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_top_scorers', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    participant_type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    participant = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'top scorer'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TopScorer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TopScorers, self).save(*args, **kwargs)



class Rivals(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_rival_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_rival_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_rival_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_rival', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_rival', null=True, blank=True)
    rival = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rival_rival', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'rival'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Rival-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Rivals, self).save(*args, **kwargs)


class Commentaries(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_commentary_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_commentary_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_commentary_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_commentary', null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    extra_minute = models.IntegerField(null=True, blank=True)
    is_goal = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    important = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'commentary'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Commentary-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Commentaries, self).save(*args, **kwargs)


class Referees(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_referee_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_referee_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_referee_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_referee', null=True, blank=True)
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
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'referee'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Referee-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Referees, self).save(*args, **kwargs)


class Transfers(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_transfer_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_transfer_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_transfer_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_transfer', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_transfer', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Sport_Stat_Type, default='Id', null=True, blank=True)
    from_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='from_team_transfer', null=True, blank=True)
    to_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='to_team_transfer', null=True, blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True,
                                         blank=True)
    date = models.DateField(null=True, blank=True)
    career_ended = models.CharField(max_length=200, choices=Public_Status, default='No', null=True, blank=True)
    free_transfer = models.CharField(max_length=200, choices=Public_Status, default='No', null=True, blank=True)
    market_value = models.CharField(max_length=100, null=True, blank=True)
    market_value_currency = models.CharField(max_length=100, null=True, blank=True)
    fee = models.CharField(max_length=100, null=True, blank=True)
    completed = models.CharField(max_length=200, choices=Public_Status, default='No', null=True, blank=True)
    amount = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'transfer'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Transfer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Transfers, self).save(*args, **kwargs)


class PreMatchOdds(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_pre_match_odd_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_pre_match_odd_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_pre_match_odd_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_pre_match_odds', null=True, blank=True)
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
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'pre match odd'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PreMatchOdd-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PreMatchOdds, self).save(*args, **kwargs)


class InPlayOdds(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_in_play_odd_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_in_play_odd_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_in_play_odd_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_in_play_odds', null=True, blank=True)
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
    total = models.CharField(max_length=100, null=True, blank=True)
    handicap = models.CharField(max_length=100, null=True, blank=True)
    latest_bookmaker_update = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'in play odd'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'InPlayOdd-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(InPlayOdds, self).save(*args, **kwargs)


class Markets(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_market_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_market_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_market_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    legacy = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    developer_name = models.CharField(max_length=200, null=True, blank=True)
    has_winning_calculations = models.CharField(max_length=200, choices=Public_Status, default='Yes', null=True,
                                                blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'market'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Market-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Markets, self).save(*args, **kwargs)


class Bookmakers(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_bookmaker_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_bookmaker_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_bookmaker_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    legacy = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'bookmaker'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Bookmaker-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Bookmakers, self).save(*args, **kwargs)


class Match(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_match_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_match_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_match_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=100, null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_match', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_match', null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_match', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_match', null=True, blank=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='round_match', null=True, blank=True)
    stage = models.ForeignKey(Stages, on_delete=models.CASCADE, related_name='stage_match', null=True, blank=True)
    fixture = models.ForeignKey(Fixtures, on_delete=models.CASCADE, related_name='fixture_match', null=True, blank=True)
    home_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match', null=True, blank=True)
    away_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_away', null=True, blank=True)
    venues = models.ForeignKey(Venues, on_delete=models.CASCADE, related_name='venue_match', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    squad = models.ForeignKey(Squads, on_delete=models.CASCADE, related_name='squad_match', null=True, blank=True)
    home_score = models.IntegerField(null=True, blank=True, default=0)
    away_score = models.IntegerField(null=True, blank=True, default=0)
    score = models.CharField(max_length=100, null=True, blank=True,default='0-0')
    start_time = models.DateTimeField(null=True, blank=True)
    current_minute = models.CharField(max_length=100, null=True, blank=True,default='0')
    current_half = models.CharField(max_length=100, choices=Half_List, default='1st Half', null=True, blank=True)
    played = models.CharField(max_length=200, choices=Match_Status, default='No', null=True, blank=True)
    is_live = models.CharField(max_length=200, choices=Match_Status, default='No', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    class Meta:
        # ordering = ('name',)
        verbose_name = 'match'  # verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Match-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Match, self).save(*args, **kwargs)

class MatchTeamPlayer(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='sport_match_team_player_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='sport_match_team_player_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='sport_match_team_player_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_team_player', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_team_player', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_match_team_player', null=True, blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    shirt_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128,unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    class Meta:

        # ordering = ('name',)
        verbose_name = 'match team player'  # verbose_name_plural = 'categories'
    def __str__(self):
        return self.player.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchTeamPlayer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchTeamPlayer, self).save(*args, **kwargs)

class MatchGoals(models.Model):

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_goal', null=True, blank=True)
    home_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_goal', null=True, blank=True)
    away_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_goal_away', null=True, blank=True)
    home_score = models.IntegerField(null=True, blank=True, default=0)
    away_score = models.IntegerField(null=True, blank=True, default=0)
    set = models.CharField(max_length=100, choices=Set_List, default='1stSet', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'match goal'

    def __str__(self):
        return self.match.name



class MatchSummary(models.Model):

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_summary', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_summary', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_match_summary', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Match_Statics, default='Messed Shots', null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    half = models.CharField(max_length=100, choices=Half_List, default='1st Half', null=True, blank=True)
    set = models.CharField(max_length=100, choices=Set_List, default='1st Set', null=True, blank=True)
    period = models.CharField(max_length=100, null=True, blank=True)
    time = models.CharField(max_length=100, null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    extra_minute = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'match summary'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchSummary-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchSummary, self).save(*args, **kwargs)

class MatchStatics(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_statics', null=True, blank=True)
    home_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_statics', null=True, blank=True)
    away_team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_statics_away', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Match_Statics, default='Messed Shots', null=True, blank=True)
    home = models.CharField(max_length=100, null=True, blank=True)
    away = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'match statics'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchStatics-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchStatics, self).save(*args, **kwargs)


class MatchTeamLineups(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_lineups', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_match_lineups', null=True, blank=True)
    plan = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('name',)
        verbose_name = 'match lineups'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchLineups-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchTeamLineups, self).save(*args, **kwargs)


class MatchTeamLineupsPlayer(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_lineups_player', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_lineups_player', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='player_lineups_summary', null=True,
                               blank=True)
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    captain = models.CharField(max_length=200, choices=Public_Status, default='No', null=True, blank=True)
    shirt_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128,unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('name',)
        verbose_name = 'match lineups player'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchLineupsPlayer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchTeamLineupsPlayer, self).save(*args, **kwargs)


class MatchPlayerSummary(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_summary', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='match_player_summary', null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='match_player_summary', null=True, blank=True)
    type = models.CharField(max_length=100, choices=Match_Statics, default='Messed Shots', null=True, blank=True)
    percentage = models.CharField(max_length=100, null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('name',)
        verbose_name = 'match player summary'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchPlayerSummary-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchPlayerSummary, self).save(*args, **kwargs)

class LeagueSeasonTable(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='season_table', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league_table', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_table', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_table', null=True, blank=True)
    order = models.CharField(max_length=100, choices=Season_Order, default='NotOrder', null=True, blank=True)
    sort = models.IntegerField(null=True, blank=True,default=0)
    description = models.TextField(null=True, blank=True)
    form = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.CharField(max_length=128, null=True, blank=True, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('name',)
        verbose_name = 'season table'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'LeagueSeasonTable-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(LeagueSeasonTable, self).save(*args, **kwargs)


class TeamSeasonTable(models.Model):
    table = models.ForeignKey(LeagueSeasonTable,on_delete=models.CASCADE, related_name='league_table', null=True, blank=True)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE, related_name='league', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_table', null=True, blank=True)
    order = models.CharField(max_length=100,choices=Season_Order, default='NotOrder' ,null=True, blank=True)
    position = models.IntegerField(null=True, blank=True,default=0)
    points = models.IntegerField(null=True, blank=True,default=0)
    played = models.IntegerField(null=True, blank=True,default=0)
    win = models.IntegerField(null=True, blank=True,default=0)
    draw = models.IntegerField(null=True, blank=True,default=0)
    lose = models.IntegerField(null=True, blank=True,default=0)
    remaining = models.IntegerField(null=True, blank=True,default=0)
    goals_for = models.IntegerField(null=True, blank=True,default=0)
    goals_against = models.IntegerField(null=True, blank=True,default=0)
    goals_difference = models.IntegerField(null=True, blank=True,default=0)
    goals_for_run = models.IntegerField(null=True, blank=True, default=0)
    goals_against_run = models.IntegerField(null=True, blank=True, default=0)
    goals_difference_run = models.IntegerField(null=True, blank=True, default=0)

    percentage = models.CharField(max_length=100, null=True, blank=True,default=0)
    description = models.TextField(null=True, blank=True)
    form = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.CharField(max_length=128, null=True, blank=True, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        # ordering = ('name',)
        verbose_name = 'season table'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TeamSeasonTable-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TeamSeasonTable, self).save(*args, **kwargs)
