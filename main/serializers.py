from rest_framework import serializers
from .models import Booth, BoothImage, TimeTable


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
    has_detail = serializers.SerializerMethodField()

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
            "has_detail",
        ]

    def get_has_detail(self, obj):
        return True

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

    def get_division_name(self, obj):
        return obj.division.name if obj.division else None

    def get_dates(self, obj):
        if hasattr(obj, "merged_dates"):
            return obj.merged_dates
        
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
        qs = Booth.objects.filter(
            name=obj.name,
            location=obj.location,
            booth_type=obj.booth_type,
            division=obj.division,
        ).values_list("schedule__date", flat=True).distinct()

        return sorted([str(d) for d in qs])

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
    

class FoodTruckDetailSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source="id", read_only=True)
    division_name = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    location_name = serializers.CharField(source="location.name", read_only=True)

    menu = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

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
            "menu",
            "image_url",
        ]

    def get_division_name(self, obj):
        return obj.division.name if obj.division else None

    def get_dates(self, obj):
        qs = Booth.objects.filter(
            name=obj.name,
            location=obj.location,
            booth_type=obj.booth_type,
            division=obj.division,
        ).values_list("schedule__date", flat=True).distinct()

        return sorted([str(d) for d in qs])

    def get_menu(self, obj):
        if not obj.menu:
            return []

        result = []
        for line in obj.menu.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) >= 2:
                name = " ".join(parts[:-1])
                price = parts[-1]
            else:
                name = line
                price = None

            result.append({
                "name": name,
                "price": price
            })

        return result

    def get_image_url(self, obj):
        # 항상 null
        return None
    

class TimeTableItemSerializer(serializers.ModelSerializer):
    timetable_id = serializers.IntegerField(source="id", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = [
            "timetable_id",
            "start_time",
            "end_time",
            "team_name",
            "category",
            "image_url",
        ]

    def get_image_url(self, obj):
        """
        우선순위 정리
        1) Booth.name == TimeTable.team_name 매칭 후, BoothImage 첫 번째(order=0)
        2) 없으면 TimeTable.image fallback
        3) 없으면 null
        """
        request = self.context.get("request")

        # 1) Booth 매칭되면: 활동사진 첫 번째 이미지
        booth = (
            Booth.objects.select_related("schedule")
            .prefetch_related("images")
            .filter(name=obj.team_name, schedule=obj.schedule)
            .first()
        )
        if booth:
            first_img = booth.images.first()
            if first_img and first_img.image:
                return request.build_absolute_uri(first_img.image.url) if request else first_img.image.url

        # 2) fallback: TimeTable.image
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url

        return None