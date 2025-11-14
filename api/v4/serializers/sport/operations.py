from api.v4.serializers.blog import *
from apps.sport.models import *


class MatchPlayerReportSerializer(serializers.ModelSerializer):
    match_id = serializers.SerializerMethodField()
    match_name = serializers.SerializerMethodField()
    team_id = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchPlayerReport
        fields = ['id', 'match', 'match_id', 'match_name','player', 'team','team_id','position',
            'set_ball', 'set_ballp', 'serve_ball', 'serve_ballp', 'cut_ball', 'cut_ballp', 'shot_ball', 'shot_ballp', 
            'score_ball', 'score_ballp','set1', 'set2', 'set3', 'set4', 'set5','vote','point_total','serve_total', 'serve_err', 'serve_ace',
            'reception_total', 'reception_err', 'reception_exc','attack_total', 'attack_err', 'attack_pts', 'attack_att','block_pts',
            'min_played','pts','reb','ast','stl','blk','fg','three_pt','ft','Offensive_Rebounds','dr','to','pf','pir','is_best_player','static_type',]

    def get_match_id(self, obj):
        return obj.match.id if obj.match else None

    def get_match_name(self, obj):
        return obj.match.name if obj.match else None
    
    def get_team_id(self, obj):
        try:
            return obj.team.id if obj.team else None
        except:
            return None
        

class PlayerStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatics
        fields = ['id', 'match', 'player', 'team', 'set_ball', 'set_ballp', 'serve_ball', 'serve_ballp', 'cut_ball',
                    'cut_ballp', 'shot_ball', 'shot_ballp', 'score_ball', 'score_ballp',]
