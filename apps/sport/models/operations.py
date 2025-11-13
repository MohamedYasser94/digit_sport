from rest_framework import serializers
from apps.sport.models.models import *
from helper.modelHelper import *

# Create your models here.


User = get_user_model()

class MatchReport(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_player_reports')
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'match report'
        verbose_name_plural = 'match reports'


    def __str__(self):
        return f'{self.match} report'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchReport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchReport, self).save(*args, **kwargs)

class MatchPlayerReport(models.Model):
    report = models.ForeignKey(MatchReport, on_delete=models.CASCADE, related_name='report_sets',null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='report_math',null=True, blank=True)
    team = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='report_team',null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='report_player',null=True, blank=True)
    position = models.IntegerField( null=True, blank=True, default=0)
    set_ball = models.IntegerField( null=True, blank=True, default=0)
    set_ballp = models.IntegerField( null=True, blank=True, default=0)
    serve_ball = models.IntegerField( null=True, blank=True, default=0)
    serve_ballp = models.IntegerField( null=True, blank=True, default=0)
    cut_ball = models.IntegerField( null=True, blank=True, default=0)
    cut_ballp = models.IntegerField( null=True, blank=True, default=0)
    shot_ball = models.IntegerField( null=True, blank=True, default=0)
    shot_ballp = models.IntegerField( null=True, blank=True, default=0)
    score_ball = models.IntegerField( null=True, blank=True, default=0)
    score_ballp = models.IntegerField( null=True, blank=True, default=0)
    set1 = models.CharField(max_length=30,   null=True, blank=True)
    set2 = models.CharField(max_length=30,   null=True, blank=True)
    set3 = models.CharField(max_length=30,   null=True, blank=True)
    set4 = models.CharField(max_length=30,   null=True, blank=True)
    set5 = models.CharField(max_length=30,   null=True, blank=True)
    vote = models.CharField(max_length=30,   null=True, blank=True)

    # Volleyball Statistics
    point_total = models.CharField(max_length=30, null=True, blank=True, default='')
    serve_total = models.CharField(max_length=30, null=True, blank=True, default='')
    serve_err = models.CharField(max_length=30, null=True, blank=True, default='')
    serve_ace = models.CharField(max_length=30, null=True, blank=True, default='')
    reception_total = models.CharField(max_length=30, null=True, blank=True, default='')
    reception_err = models.CharField(max_length=30, null=True, blank=True, default='')
    reception_exc = models.CharField(max_length=30, null=True, blank=True, default='')
    attack_total = models.CharField(max_length=30, null=True, blank=True, default='')
    attack_err = models.CharField(max_length=30, null=True, blank=True, default='')
    attack_pts = models.CharField(max_length=30, null=True, blank=True, default='')
    attack_att = models.CharField(max_length=30, null=True, blank=True, default='')
    block_pts = models.CharField(max_length=30, null=True, blank=True, default='')

    # Basketball Statistics
    min_played = models.CharField(max_length=30, null=True, blank=True, default='')
    pts = models.CharField(max_length=30, null=True, blank=True, default='')
    reb = models.CharField(max_length=30, null=True, blank=True, default='')
    ast = models.CharField(max_length=30, null=True, blank=True, default='')
    stl = models.CharField(max_length=30, null=True, blank=True, default='')
    blk = models.CharField(max_length=30, null=True, blank=True, default='')
    fg = models.CharField(max_length=30, null=True, blank=True, default='')
    three_pt = models.CharField(max_length=30, null=True, blank=True, default='')
    ft = models.CharField(max_length=30, null=True, blank=True, default='')
    Offensive_Rebounds = models.CharField(max_length=30, null=True, blank=True, default='')
    dr = models.CharField(max_length=30, null=True, blank=True, default='')
    to = models.CharField(max_length=30, null=True, blank=True, default='')
    pf = models.CharField(max_length=30, null=True, blank=True, default='')
    pir = models.CharField(max_length=30, null=True, blank=True, default='')

    static_type = models.CharField(max_length=30,choices=Statics_Type, default='General',   null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'match player report'
        verbose_name_plural = 'match player reports'


    def __str__(self):
        return f'{self.match} report'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchPlayerReport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchPlayerReport, self).save(*args, **kwargs)


class MatchPlayerReportSerializer(serializers.ModelSerializer):
    match_name = serializers.CharField(source='match.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    player_name = serializers.CharField(source='player.display_name', read_only=True)
    
    class Meta:
        model = MatchPlayerReport
        fields = [
            'id', 'match', 'match_name', 'team', 'team_name', 'player', 'player_name',
            'position', 'set_ball', 'set_ballp', 'serve_ball', 'serve_ballp',
            'cut_ball', 'cut_ballp', 'shot_ball', 'shot_ballp', 'score_ball',
            'score_ballp', 'set1', 'set2', 'set3', 'set4', 'set5', 'vote',
            'point_total', 'point_bp', 'point_wl', 'serve_total', 'serve_err',
            'serve_pts', 'reception_total', 'reception_err', 'reception_pos',
            'reception_exc', 'attack_total', 'attack_err', 'attack_pos',
            'attack_exc', 'block_pts', 'static_type', 'create_at'
        ]

class PlayerStatics(models.Model):
    report = models.ForeignKey(MatchReport, on_delete=models.CASCADE, related_name='static_sets',null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='static_math',null=True, blank=True)
    team = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='static_team',null=True, blank=True)
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='static_player',null=True, blank=True)
    position = models.IntegerField( null=True, blank=True, default=0)
    set_ball = models.IntegerField( null=True, blank=True, default=0)
    set_ballp = models.IntegerField( null=True, blank=True, default=0)
    serve_ball = models.IntegerField( null=True, blank=True, default=0)
    serve_ballp = models.IntegerField( null=True, blank=True, default=0)
    cut_ball = models.IntegerField( null=True, blank=True, default=0)
    cut_ballp = models.IntegerField( null=True, blank=True, default=0)
    shot_ball = models.IntegerField( null=True, blank=True, default=0)
    shot_ballp = models.IntegerField( null=True, blank=True, default=0)
    score_ball = models.IntegerField( null=True, blank=True, default=0)
    score_ballp = models.IntegerField( null=True, blank=True, default=0)

    set1 = models.CharField(max_length=30,   null=True, blank=True,default='')
    set2 = models.CharField(max_length=30,   null=True, blank=True,default='')
    set3 = models.CharField(max_length=30,   null=True, blank=True,default='')
    set4 = models.CharField(max_length=30,   null=True, blank=True,default='')
    set5 = models.CharField(max_length=30,   null=True, blank=True,default='')
    vote = models.CharField(max_length=30,   null=True, blank=True,default='')
    point_total = models.CharField(max_length=30,   null=True, blank=True,default='')
    point_bp = models.CharField(max_length=30,   null=True, blank=True,default='')
    point_wl = models.CharField(max_length=30,   null=True, blank=True,default='')
    serve_total = models.CharField(max_length=30,   null=True, blank=True,default='')
    serve_err = models.CharField(max_length=30,   null=True, blank=True,default='')
    serve_pts = models.CharField(max_length=30,   null=True, blank=True,default='')
    reception_total = models.CharField(max_length=30,   null=True, blank=True,default='')
    reception_err = models.CharField(max_length=30,   null=True, blank=True,default='')
    reception_pos = models.CharField(max_length=30,   null=True, blank=True,default='')
    reception_exc = models.CharField(max_length=30,   null=True, blank=True,default='')
    attack_total = models.CharField(max_length=30,   null=True, blank=True,default='')
    attack_err = models.CharField(max_length=30,   null=True, blank=True,default='')
    attack_pos = models.CharField(max_length=30,   null=True, blank=True,default='')
    attack_exc = models.CharField(max_length=30,   null=True, blank=True,default='')
    block_pts = models.CharField(max_length=30,   null=True, blank=True,default='')
    static_type = models.CharField(max_length=30,choices=Statics_Type, default='General',   null=True, blank=True)

    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'match player report'
        verbose_name_plural = 'match player reports'


    def __str__(self):
        return f'{self.match} report'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PlayerStatics-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PlayerStatics, self).save(*args, **kwargs)




