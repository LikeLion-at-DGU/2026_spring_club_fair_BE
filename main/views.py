from collections import defaultdict
from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *


@api_view(["GET"])
def booths_list(request):
    day = request.GET.get("day")
    if not day:
        return Response(
            {"code": "INVALID_DAY", "message": "day는 YYYY-MM-DD 형식의 필수 파라미터입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 전체 부스 가져와서 날짜 dict 구성
    all_booths = Booth.objects.select_related("schedule")

    dates_dict = defaultdict(set)  # 부스별 전체 날짜 dict

    for b in all_booths:
        key = (
            b.name,
            b.location_id,
            b.booth_type,
            b.division_id,
        )
        dates_dict[key].add(str(b.schedule.date))

    # day 필터
    qs = Booth.objects.select_related("division", "location", "schedule").prefetch_related("images")
    qs = qs.filter(schedule__date=day)

    location_id = request.GET.get("location_id")
    if location_id:
        qs = qs.filter(location_id=location_id)

    division_id = request.GET.get("division_id")
    if division_id:
        qs = qs.filter(division_id=division_id)

    booth_type = request.GET.get("booth_type")
    if booth_type:
        qs = qs.filter(booth_type=booth_type)

    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    qs = qs.order_by("loc_num")  # loc_num 오름차순 정렬

    # 카드 단위 그룹핑
    grouped = defaultdict(list)

    for booth in qs:
        key = (
            booth.name,
            booth.location_id,
            booth.booth_type,
            booth.division_id,
        )
        grouped[key].append(booth)

    results = []

    for key, booths in grouped.items():
        # 대표 row: loc_num 최소
        representative = min(booths, key=lambda b: b.loc_num)

        # 전체 운영 날짜 (위에서 만든 dict 사용)
        dates = sorted(dates_dict.get(key, []))

        serializer = BoothListSerializer(
            representative, context={"request": request}
        )
        data = serializer.data

        data["dates"] = dates

        results.append(data)

    return Response({"count": len(results), "results": results})


@api_view(["GET"])
def booth_detail(request, booth_id: int):
    try:
        booth = (
            Booth.objects.select_related("division", "location", "schedule")
            .prefetch_related("images")
            .get(id=booth_id)
        )
    except Booth.DoesNotExist:
        return Response(
            {"code": "BOOTH_NOT_FOUND", "message": "해당 booth_id의 부스를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 푸드트럭 타입 분기
    if booth.booth_type == Booth.BoothType.FOODTRUCK:
        data = FoodTruckDetailSerializer(booth, context={"request": request}).data
        return Response(data)

    data = BoothDetailSerializer(booth, context={"request": request}).data
    return Response(data)


@api_view(["GET"])
def timetable_list(request):
    day = request.GET.get("day")
    if not day:
        return Response(
            {"code": "INVALID_DAY", "message": "day는 YYYY-MM-DD 형식의 필수 파라미터입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 공연은 만해광장만 -> location_name으로 고정 검색
    try:
        manhae = Location.objects.get(name="만해광장")
    except Location.DoesNotExist:
        return Response(
            {"code": "LOCATION_NOT_FOUND", "message": "만해광장 Location 데이터가 없습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    qs = (
        TimeTable.objects.select_related("schedule", "location")
        .filter(schedule__date=day, location=manhae)
        .order_by("start_time")
    )

    items = TimeTableItemSerializer(qs, many=True, context={"request": request}).data

    results = [
        {
            "location_id": manhae.id,
            "location_name": manhae.name,
            "items": items,
        }
    ]

    return Response({"day": day, "results": results})