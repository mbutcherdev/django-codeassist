# Turn models into JSON data/object

from rest_framework.serializers import ModelSerializer
from base.models import Room

# Limiting the output for any api requests
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = 'id', 'name', 'description', 'topic'
