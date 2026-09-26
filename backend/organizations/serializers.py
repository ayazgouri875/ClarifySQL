from rest_framework import serializers
from .models import Organization
from accounts.models import User

class OrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "role", "created_at"]
        read_only_fields = ["id", "created_at"]

class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "member_count", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def get_member_count(self, obj):
        return obj.users.count()
