from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["userId", "firstName", "lastName", "email", "password", "phone"]
        extra_kwargs = {
            "password": {"write_only": True},
            "userId": {"read_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            firstName=validated_data["firstName"],
            lastName=validated_data["lastName"],
            password=validated_data["password"],
            phone=validated_data.get("phone"),
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_userId(self, value):
        if User.objects.filter(userId=value).exists():
            raise serializers.ValidationError("A user with this ID already exists.")
        return value


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["orgId", "name", "description"]
        extra_kwargs = {"orgId": {"read_only": True}}
