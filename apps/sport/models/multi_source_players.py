from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from slugify import slugify
from helper.modelHelper import *
from helper.viewHelper import get_file_path

User = get_user_model()

class DataSource(models.Model):
    """
    Represents different data sources for player information
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority for conflict resolution")
    is_active = models.BooleanField(default=True)
    api_base_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MultiSourcePlayers(models.Model):
    """
    Enhanced Players model supporting multiple data sources
    """
    # Generic Foreign Keys (keeping existing structure)
    sender_model = models.ForeignKey(ContentType, related_name='multi_player_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='multi_player_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='multi_player_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')

    # Multiple API IDs for different sources
    sportmonks_api_id = models.IntegerField(null=True, blank=True, db_index=True, help_text="Sportmonks API ID")
    transfermarkt_id = models.CharField(max_length=100, null=True, blank=True, db_index=True, help_text="Transfer Market ID")
    transfermarkt_code = models.CharField(max_length=100, null=True, blank=True, help_text="Transfer Market code from URL")
    manual_entry_id = models.CharField(max_length=100, null=True, blank=True, help_text="Manual entry reference ID")
    
    # Additional source IDs (JSON field for flexibility)
    source_ids = models.JSONField(default=dict, blank=True, help_text="Additional API IDs from other sources")
    
    # Core player information (maintaining existing fields)
    team = models.ForeignKey('Teams', on_delete=models.CASCADE, null=True, blank=True)
    league = models.ManyToManyField('Leagues', related_name='multi_league_player', blank=True)
    sport = models.ForeignKey('Sport', on_delete=models.CASCADE, related_name='multi_sport_player', null=True, blank=True)
    
    # Name fields with source tracking
    common_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True, help_text="Primary display name")
    display_name = models.CharField(max_length=100, null=True, blank=True)
    name_in_home_country = models.CharField(max_length=100, null=True, blank=True)
    
    # Basic information
    short_code = models.CharField(max_length=100, null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    
    # Location information
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    country_image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    api_country = models.CharField(max_length=100, null=True, blank=True)
    api_nationality = models.CharField(max_length=100, null=True, blank=True)
    nationality = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    citizenship = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    api_city = models.CharField(max_length=100, null=True, blank=True)
    place_of_birth_country = models.CharField(max_length=100, null=True, blank=True)
    place_of_birth_city = models.CharField(max_length=100, null=True, blank=True)
    birthplace = models.CharField(max_length=100, null=True, blank=True)
    
    # Position information
    position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    api_position = models.CharField(max_length=100, null=True, blank=True)
    detailed_position = models.CharField(max_length=100, choices=Position_List, default='Goalkeeper', null=True, blank=True)
    api_detailed_position = models.CharField(max_length=100, null=True, blank=True)
    foot = models.CharField(max_length=20, null=True, blank=True, help_text="Preferred foot (Left/Right/Both)")
    
    # Physical attributes
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Transfer Market or other source image URL")
    url = models.URLField(blank=True, null=True)
    height = models.CharField(max_length=100, null=True, blank=True)
    age = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    date_of_birth = models.CharField(max_length=100, null=True, blank=True, help_text="Original birth date string from source")
    gender = models.CharField(max_length=100, choices=Gander_type, default='Male', null=True, blank=True)
    
    # Career information
    type = models.CharField(max_length=100, null=True, blank=True)
    ratings = models.CharField(max_length=100, null=True, blank=True, default='0')
    in_team = models.CharField(max_length=100, choices=Public_Status, default='No', null=True, blank=True)
    
    # Contract and club information
    joined = models.CharField(max_length=100, null=True, blank=True, help_text="Date joined current club")
    contract_expires = models.CharField(max_length=100, null=True, blank=True)
    contract_extension_date = models.CharField(max_length=100, null=True, blank=True)
    
    # Transfer Market specific fields
    current_market_value = models.CharField(max_length=100, null=True, blank=True, help_text="Current market value with currency")
    highest_market_value = models.CharField(max_length=100, null=True, blank=True, help_text="Highest market value achieved")
    market_value_currency = models.CharField(max_length=10, null=True, blank=True, help_text="Currency code (EUR, USD, etc.)")
    market_value_numeric = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Numeric value for sorting/filtering")
    market_value_history = models.JSONField(default=list, blank=True, help_text="Historical market value data")
    market_value_last_updated = models.DateTimeField(null=True, blank=True)
    
    # Agent and commercial information
    player_agent_name = models.CharField(max_length=200, null=True, blank=True)
    player_agent_href = models.URLField(null=True, blank=True)
    outfitter = models.CharField(max_length=100, null=True, blank=True, help_text="Equipment sponsor")
    social_media = models.JSONField(default=list, blank=True, help_text="Social media links")
    
    # Current club information
    current_club_href = models.URLField(null=True, blank=True)
    current_club_name = models.CharField(max_length=200, null=True, blank=True)
    
    # Data source tracking
    primary_data_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='primary_players', help_text="Primary source for this player")
    data_sources = models.ManyToManyField(DataSource, through='PlayerDataSourceInfo', blank=True)
    
    # Conflict resolution
    name_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='name_source_players')
    image_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='image_source_players')
    market_value_source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='value_source_players')
    
    # System fields
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Multi-Source Player'
        verbose_name_plural = 'Multi-Source Players'
        indexes = [
            models.Index(fields=['sportmonks_api_id']),
            models.Index(fields=['transfermarkt_id']),
            models.Index(fields=['name']),
            models.Index(fields=['market_value_numeric']),
        ]

    def __str__(self):
        return f"{self.name or self.display_name or 'Unknown Player'}"

    def get_primary_id(self):
        """Return the primary ID based on Flutter app dependency (Sportmonks or system ID)"""
        if self.sportmonks_api_id:
            return f"sportmonks_{self.sportmonks_api_id}"
        return f"system_{self.pk}"

    def get_image(self):
        """Get the best available image based on source priority"""
        if self.image:
            try:
                return self.image.url
            except:
                pass
        if self.image_path:
            return self.image_path
        if self.image_url:
            return self.image_url
        return None

    def get_country_image(self):
        """Get country image"""
        try:
            return self.country_image.url if self.country_image else None
        except:
            return None

    def get_market_value_display(self):
        """Get formatted market value for display"""
        if self.current_market_value:
            return self.current_market_value
        elif self.market_value_numeric and self.market_value_currency:
            return f"{self.market_value_numeric} {self.market_value_currency}"
        return "Not available"

    def update_from_source(self, source, data, user=None):
        """Update player data from a specific source"""
        # Get or create data source info
        source_info, created = PlayerDataSourceInfo.objects.get_or_create(
            player=self,
            data_source=source,
            defaults={'last_updated': datetime.now()}
        )
        
        # Update fields based on source priority and conflicts
        self._update_with_conflict_resolution(source, data)
        
        # Update source info
        source_info.last_updated = datetime.now()
        source_info.last_updated_by = user
        source_info.raw_data = data
        source_info.save()
        
        # Set primary source if not set or if this source has higher priority
        if not self.primary_data_source or source.priority > self.primary_data_source.priority:
            self.primary_data_source = source
        
        self.save()

    def _update_with_conflict_resolution(self, source, data):
        """Update fields with conflict resolution based on source priority"""
        # Define field mappings for different sources
        source_field_mappings = {
            'sportmonks': {
                'sportmonks_api_id': 'id',
                'common_name': 'common_name',
                'first_name': 'firstname',
                'last_name': 'lastname',
                'name': 'display_name',
                'height': 'height',
                'weight': 'weight',
                'birthdate': 'date_of_birth',
                'gender': 'gender',
                'api_country': 'country_id',
                'api_nationality': 'nationality_id',
                'api_city': 'city_id',
                'api_position': 'position_id',
                'api_detailed_position': 'detailed_position_id',
                'type': 'type_id',
                'image_path': 'image_path',
            },
            'transfermarkt': {
                'transfermarkt_id': 'id',
                'transfermarkt_code': 'code',
                'name': 'name',
                'last_name': 'last_name',
                'number': 'number',
                'name_in_home_country': 'name_in_home_country',
                'date_of_birth': 'date_of_birth',
                'place_of_birth_country': 'place_of_birth.country',
                'place_of_birth_city': 'place_of_birth.city',
                'age': 'age',
                'height': 'height',
                'citizenship': 'citizenship',
                'position': 'position',
                'foot': 'foot',
                'current_market_value': 'current_market_value',
                'highest_market_value': 'highest_market_value',
                'market_value_history': 'market_value_history',
                'joined': 'joined',
                'contract_expires': 'contract_expires',
                'contract_extension_date': 'day_of_last_contract_extension',
                'outfitter': 'outfitter',
                'social_media': 'social_media',
                'image_url': 'image_url',
                'player_agent_name': 'player_agent.name',
                'player_agent_href': 'player_agent.href',
                'current_club_href': 'current_club.href',
            }
        }
        
        # Get field mapping for this source
        field_mapping = source_field_mappings.get(source.slug, {})
        
        for model_field, data_field in field_mapping.items():
            if hasattr(self, model_field):
                value = self._get_nested_value(data, data_field)
                if value is not None:
                    # Check if we should update this field based on source priority
                    if self._should_update_field(model_field, source):
                        setattr(self, model_field, value)
                        # Track the source for important fields
                        if model_field == 'name' and not self.name_source:
                            self.name_source = source
                        elif 'image' in model_field and not self.image_source:
                            self.image_source = source
                        elif 'market_value' in model_field and not self.market_value_source:
                            self.market_value_source = source

    def _get_nested_value(self, data, field_path):
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def _should_update_field(self, field_name, source):
        """Determine if a field should be updated based on source priority"""
        current_value = getattr(self, field_name)
        
        # If field is empty, always update
        if not current_value:
            return True
        
        # Check source-specific priorities for important fields
        source_field_map = {
            'name': 'name_source',
            'image_path': 'image_source',
            'image_url': 'image_source',
            'current_market_value': 'market_value_source'
        }
        
        if field_name in source_field_map:
            current_source_field = source_field_map[field_name]
            current_source = getattr(self, current_source_field)
            
            if current_source and source.priority <= current_source.priority:
                return False
        
        # Default: update if new source has higher priority than primary source
        if self.primary_data_source and source.priority <= self.primary_data_source.priority:
            return False
            
        return True

    def save(self, *args, **kwargs):
        # Generate unique code and slug
        if not self.code:
            base_code = f'MultiPlayer-{get_random_string(8).upper()}'
            self.code = base_code
            # Ensure uniqueness
            counter = 1
            while MultiSourcePlayers.objects.filter(code=self.code).exists():
                self.code = f'{base_code}-{counter}'
                counter += 1
        
        # Generate slug from name and ID
        if not self.slug:
            if self.name and self.sportmonks_api_id:
                self.slug = slugify(f"{self.name}-{self.sportmonks_api_id}")
            elif self.name:
                base_slug = slugify(self.name)
                slug_candidate = base_slug
                counter = 1
                while MultiSourcePlayers.objects.filter(slug=slug_candidate).exists():
                    slug_candidate = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug_candidate
            else:
                self.slug = slugify(self.code)
        
        # Parse numeric market value for sorting/filtering
        if self.current_market_value and not self.market_value_numeric:
            self._parse_market_value()
        
        super().save(*args, **kwargs)

    def _parse_market_value(self):
        """Parse market value string to numeric value and currency"""
        import re
        
        if not self.current_market_value:
            return
        
        # Remove common prefixes and suffixes
        value_str = self.current_market_value.strip()
        
        # Extract numeric value and currency using regex
        # Patterns like "€50.00m", "$25.5M", "£30m", "€1.2bn"
        pattern = r'([€$£¥])?([\d,.]+)([kmb])?'
        match = re.search(pattern, value_str.lower())
        
        if match:
            currency_symbol, number_str, multiplier = match.groups()
            
            # Convert currency symbol to code
            currency_map = {'€': 'EUR', '$': 'USD', '£': 'GBP', '¥': 'JPY'}
            if currency_symbol and not self.market_value_currency:
                self.market_value_currency = currency_map.get(currency_symbol, 'EUR')
            
            # Convert number string to float
            try:
                number = float(number_str.replace(',', ''))
                
                # Apply multiplier
                if multiplier == 'k':
                    number *= 1000
                elif multiplier == 'm':
                    number *= 1000000
                elif multiplier == 'b':
                    number *= 1000000000
                
                self.market_value_numeric = number
                
            except (ValueError, TypeError):
                pass


class PlayerDataSourceInfo(models.Model):
    """
    Tracks information about data sources for each player
    """
    player = models.ForeignKey(MultiSourcePlayers, on_delete=models.CASCADE, related_name='source_info')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    raw_data = models.JSONField(default=dict, blank=True, help_text="Raw data from this source")
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('player', 'data_source')
        verbose_name = 'Player Data Source Info'
        verbose_name_plural = 'Player Data Source Infos'
    
    def __str__(self):
        return f"{self.player.name} - {self.data_source.name}"


class PlayerDataConflict(models.Model):
    """
    Tracks data conflicts between different sources for manual resolution
    """
    player = models.ForeignKey(MultiSourcePlayers, on_delete=models.CASCADE, related_name='conflicts')
    field_name = models.CharField(max_length=100)
    source_1 = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='conflict_source_1')
    value_1 = models.TextField()
    source_2 = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='conflict_source_2')
    value_2 = models.TextField()
    resolved = models.BooleanField(default=False)
    resolution_choice = models.CharField(max_length=20, choices=[
        ('source_1', 'Use Source 1'),
        ('source_2', 'Use Source 2'), 
        ('manual', 'Manual Value'),
        ('ignore', 'Ignore Conflict')
    ], null=True, blank=True)
    manual_value = models.TextField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Player Data Conflict'
        verbose_name_plural = 'Player Data Conflicts'
        unique_together = ('player', 'field_name', 'source_1', 'source_2')
    
    def __str__(self):
        return f"Conflict: {self.player.name} - {self.field_name}"
