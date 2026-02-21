from collections import defaultdict
from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Booth
from .serializers import BoothListSerializer, BoothDetailSerializer


@api_view(["GET"])
def booths_list(request):
    day = request.GET.get("day")
    if not day:
        return Response(
            {"code": "INVALID_DAY", "message": "day는 YYYY-MM-DD 형식의 필수 파라미터입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

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

    # loc_num 오름차순 정렬
    qs = qs.order_by("loc_num")

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

    for booths in grouped.values():
        # 현재 day 기준 row (대표 row)
        representative = booths[0]

        # 해당 name의 전체 날짜 조회
        all_dates = (
            Booth.objects.filter(
                name=representative.name,
                location=representative.location,
                booth_type=representative.booth_type,
                division=representative.division,
            )
            .values_list("schedule__date", flat=True)
            .distinct()
        )

        dates = sorted([str(d) for d in all_dates])

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

    data = BoothDetailSerializer(booth, context={"request": request}).data
    return Response(data)