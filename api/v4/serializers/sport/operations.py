from api.v3.serializers.blog import *
from apps.sport.models import *


class MatchPlayerReportSerializer(serializers.ModelSerializer):
    match_id = serializers.SerializerMethodField()
    match_name = serializers.SerializerMethodField()
    class Meta:
        model = MatchPlayerReport
        fields = ['id', 'match','match_id' ,'match_name',
                  'player', 'team', 'set_ball', 'set_ballp', 'serve_ball', 'serve_ballp', 'cut_ball', 'cut_ballp', 'shot_ball', 'shot_ballp', 'score_ball', 'score_ballp',
                 ]

    def get_match_id(self, obj):
        return obj.match.id

    def get_match_name(self, obj):
        return obj.match.name

class PlayerStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatics
        fields = ['id', 'match', 'player', 'team', 'set_ball', 'set_ballp', 'serve_ball', 'serve_ballp', 'cut_ball',
                  'cut_ballp', 'shot_ball', 'shot_ballp', 'score_ball', 'score_ballp',
                  ]
