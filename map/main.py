from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
from geopy.distance import geodesic

app = FastAPI()

# 병원 데이터를 이미 로드한 상태로 가정합니다.
hospitals = pd.read_json('../data/merged_file_junrang_index_db.json')
hospitals['latitude'] = hospitals['latitude'].astype(float)
hospitals['longitude'] = hospitals['longitude'].astype(float)

@app.get("/nearby_hospitals/")
async def get_nearby_hospitals(
    latitude: float = Query(..., description="사용자의 위도"),
    longitude: float = Query(..., description="사용자의 경도"),
    radius: Optional[float] = Query(5.0, description="검색 반경 (킬로미터)")
):
    user_location = (latitude, longitude)

    # 중복된 병원 이름을 처리하여 유일한 병원만을 남기는 작업
    unique_hospitals = {}
    for _, hospital in hospitals.iterrows():
        name = hospital["name"]
        location = (hospital["latitude"], hospital["longitude"])
        distance = geodesic(user_location, location).kilometers

        # 이름이 없거나 기존 거리보다 현재 거리가 더 가까우면서 반경 내에 있는 경우에 업데이트
        if (name not in unique_hospitals or distance < unique_hospitals[name]["distance"]) and distance <= radius:
            unique_hospitals[name] = {"name": name, "distance": distance, "latitude": hospital["latitude"], "longitude": hospital["longitude"]}

    return {"nearby_hospitals": list(unique_hospitals.values())}
