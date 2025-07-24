import json
import requests
import xmltodict
from datetime import datetime
from tqdm import tqdm
from pathlib import Path
from src.config import RAW_DATA_DIR, api_key_value

def collect_wifi_data(api_key=None):
    """서울시 공공 와이파이 API에서 데이터를 수집합니다."""
    global api_key_value

    # 입력된 API 키가 있으면 사용
    if api_key:
        api_key_value = api_key

    # API 설정
    BASE_URL = 'http://openapi.seoul.go.kr:8088'
    SERVICE = 'TbPublicWifiInfo'
    START_INDEX = 1
    END_INDEX = 1000

    # 필수 필드 정의
    REQUIRED_FIELDS = [
        'X_SWIFI_MGR_NO', 'X_SWIFI_WRDOFC', 'X_SWIFI_MAIN_NM',
        'X_SWIFI_ADRES1', 'X_SWIFI_INSTL_TY', 'X_SWIFI_INSTL_MBY',
        'LAT', 'LNT'
    ]

    # API 키 확인
    if not api_key_value:
        print("API 키가 제공되지 않았습니다. 기존 데이터를 사용합니다.")
        return None

    def get_wifi_data(start_idx, end_idx):
        """API에서 데이터 페이지를 가져옵니다."""
        url = f"{BASE_URL}/{api_key_value}/xml/{SERVICE}/{start_idx}/{end_idx}"
        # API 호출 진행
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data_dict = xmltodict.parse(response.text)

            if 'RESULT' in data_dict:
                result = data_dict['RESULT']
                if 'CODE' in result and 'MESSAGE' in result:
                    raise Exception(f"API 오류: {result['CODE']} - {result['MESSAGE']}")

            return data_dict
        except Exception as e:
            print(f"데이터 가져오기 실패: {e}")
            return None

    # 전체 데이터 수집
    all_data = []
    current_index = START_INDEX
    total_count = None

    # 첫 번째 API 호출로 전체 데이터 수 확인
    initial_data = get_wifi_data(START_INDEX, START_INDEX + END_INDEX - 1)
    if initial_data and SERVICE in initial_data:
        total_count = int(initial_data[SERVICE]['list_total_count'])
        print(f"\n전체 데이터 수: {total_count:,}개")

        # tqdm 진행률 바 초기화
        progress_bar = tqdm(total=total_count, desc="데이터 수집 중",
                          bar_format="{desc}: {percentage:3.1f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")

        # 첫 번째 데이터 처리
        if 'row' in initial_data[SERVICE]:
            rows = initial_data[SERVICE]['row']
            if isinstance(rows, dict):
                rows = [rows]
            for row in rows:
                missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
                if not missing_fields:
                    all_data.append(row)
            progress_bar.update(len(rows))

        current_index += END_INDEX

        # 나머지 데이터 수집
        while current_index <= total_count:
            data = get_wifi_data(current_index, min(current_index + END_INDEX - 1, total_count))

            if not data or SERVICE not in data or 'row' not in data[SERVICE]:
                break

            rows = data[SERVICE]['row']
            if isinstance(rows, dict):
                rows = [rows]

            # 데이터 검증 및 추가
            valid_rows = 0
            for row in rows:
                missing_fields = [field for field in REQUIRED_FIELDS if field not in row]
                if not missing_fields:
                    all_data.append(row)
                    valid_rows += 1

            progress_bar.update(valid_rows)
            current_index += END_INDEX

        progress_bar.close()

    # 데이터 저장
    if all_data:
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wifi_data_{current_date}.json"
        filepath = RAW_DATA_DIR / filename

        print(f"\n데이터를 저장하는 중... ({len(all_data)}개 항목)")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"데이터 저장 완료: {filepath}")
        return all_data
    else:
        print("수집된 데이터가 없습니다.")
        return None 