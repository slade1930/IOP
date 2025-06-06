from rest_framework import serializers
from .models import Simplex


class SimplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simplex
        fields = "__all__"
