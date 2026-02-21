from rest_framework import serializers
from .models import Booth, BoothImage


class BoothImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BoothImage
        fields = ["order", "image_url"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class BoothListSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source="id", read_only=True)
    division_name = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    location_name = serializers.CharField(source="location.name", read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = [
            "booth_id",
            "name",
            "booth_type",
            "division_name",
            "dates",
            "location_name",
            "loc_num",
            "logo_url",
        ]

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

    def get_division_name(self, obj):
        return obj.division.name if obj.division else None

    def get_dates(self, obj):
        # day 필수 API라서 기본은 해당 day만 포함
        return [str(obj.schedule.date)]

'''
    def get_thumbnail_url(self, obj):
        first_img = obj.images.first()  # order=0
        if not first_img or not first_img.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(first_img.image.url) if request else first_img.image.url
'''

class BoothDetailSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source="id", read_only=True)
    division_name = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    location_name = serializers.CharField(source="location.name", read_only=True)

    event = serializers.SerializerMethodField()
    instagram = serializers.SerializerMethodField()
    images = BoothImageSerializer(many=True, read_only=True)

    class Meta:
        model = Booth
        fields = [
            "booth_id",
            "name",
            "booth_type",
            "division_name",
            "dates",
            "location_name",
            "loc_num",
            "short_description",
            "description",
            "event",
            "recruit_start",
            "recruit_end",
            "recruit_detail",
            "instagram",
            "images",
        ]

    def get_division_name(self, obj):
        return obj.division.name if obj.division else None

    def get_dates(self, obj):
        return [str(obj.schedule.date)]

    def get_event(self, obj):
        if not obj.event:
            return []
        return [line.strip() for line in obj.event.splitlines() if line.strip()]

    def get_instagram(self, obj):
        if not obj.instagram_handle:
            return None
        handle = obj.instagram_handle.strip()
        if not handle.startswith("@"):
            handle = "@" + handle
        return {"handle": handle, "url": f"https://instagram.com/{handle.lstrip('@')}"}