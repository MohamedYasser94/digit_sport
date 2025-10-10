# In api/v4/serializers/favorite.py

from rest_framework import serializers
from apps.sport.models import Leagues, Teams, Players


class FavoriteToggleSerializer(serializers.Serializer):
    """
    Optimized serializer for validating the favorite request.
    Instead of returning a full model instance, it returns the
    information needed to create the generic foreign key, which is more efficient.
    """
    type = serializers.ChoiceField(choices=['league', 'team', 'player'])
    slug = serializers.CharField(max_length=255)

    def validate(self, attrs):
        item_type = attrs.get('type')
        slug = attrs.get('slug')

        model_map = {
            'league': Leagues,
            'team': Teams,
            'player': Players
        }
        Model = model_map.get(item_type)

        try:
            # We select_only('pk') because we only need the primary key, not the whole object.
            # This is a minor but good optimization for the database query.
            instance = Model.objects.values('pk', 'name').get(slug=slug)
        except Model.DoesNotExist:
            raise serializers.ValidationError({'slug': f"No {item_type} found with the slug '{slug}'."})
        except Exception:
            # Catch any other potential errors during the query
            raise serializers.ValidationError("An error occurred while trying to find the item.")

        # Prepare the validated data for the view
        attrs['content_type'] = ContentType.objects.get_for_model(Model)
        attrs['object_id'] = instance['pk']
        # Also pass the name for use in the response message
        attrs['instance_name'] = instance['name']
        return attrs
