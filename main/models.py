from django.db import models


class Schedule(models.Model):
    """진행일 (DAY1/DAY2)"""

    date = models.DateField(unique=True)

    def __str__(self):
        return str(self.date)


class Location(models.Model):
    """위치 (만해광장/팔정도)"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    """동아리 분과"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Booth(models.Model):
    """부스(동아리/푸드트럭)"""

    class BoothType(models.TextChoices):
        CLUB = "CLUB", "CLUB"
        FOODTRUCK = "FOODTRUCK", "FOODTRUCK"

    name = models.CharField(max_length=100)  # 동아리/푸드트럭 이름
    booth_type = models.CharField(
        max_length=20, 
        choices=BoothType.choices, 
        default=BoothType.CLUB,
        )

    # 푸드트럭은 division = null
    division = models.ForeignKey(
        Division, on_delete=models.SET_NULL, null=True, blank=True, related_name="booths"
    )

    schedule = models.ForeignKey(
        Schedule, on_delete=models.PROTECT, related_name="booths"
    )
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="booths"
    )

    # 푸드트럭도 loc_num 임의로 가짐
    loc_num = models.PositiveIntegerField()

    short_description = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")

    # 이벤트 & 메뉴: DB에는 줄바꿈 텍스트로 저장 (응답에서 split해서 배열로 내려줄 예정)
    event = models.TextField(blank=True, default="")
    menu = models.TextField(blank=True, default="")

    recruit_start = models.DateField(null=True, blank=True)
    recruit_end = models.DateField(null=True, blank=True)
    recruit_detail = models.CharField(max_length=200, null=True, blank=True)

    # 서버가 handle에서 @ 제거한 값으로 url 만들 예정
    instagram_handle = models.CharField(max_length=31, null=True, blank=True)
    
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 같은 날짜/같은 위치에서 번호 중복 방지
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "location", "loc_num"],
                name="unique_booth_locnum_per_day_location",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.schedule.date})"


class BoothImage(models.Model):
    booth = models.ForeignKey(
        Booth, on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to="booths/")

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["booth", "order"],
                name="unique_booth_image_order",
            )
        ]

    def __str__(self):
        return f"{self.booth.name} - {self.order}"


class TimeTable(models.Model):
    """공연 타임테이블 (만해광장만)"""

    schedule = models.ForeignKey(
        Schedule, on_delete=models.PROTECT, related_name="timetables"
    )
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="timetables"
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    team_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    # 부스 있는 공연팀 연결용
    booth = models.ForeignKey(
        Booth,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetables",
    )

    # 부스 없는 공연팀 fallback 이미지 (활동사진 1장)
    image = models.ImageField(upload_to="timetable/", null=True, blank=True)

    class Meta:
        ordering = ["start_time"]   # 시간순 기본 정렬

    def __str__(self):
        return f"{self.team_name} ({self.schedule.date})"