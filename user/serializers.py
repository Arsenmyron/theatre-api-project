from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    message = _("User account is disabled.")
                    raise serializers.ValidationError(message, code="disabled")

            else:
                message = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(message, code="login")
        else:
            message = _("Must include email and password.")
            raise serializers.ValidationError(message, code="authorization")

        attrs["user"] = user
        return attrs


class UserFullNameSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("full_name",)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
