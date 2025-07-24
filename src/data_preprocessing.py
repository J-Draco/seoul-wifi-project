import json
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def preprocess_wifi_data(raw_data=None):
    """와이파이 데이터를 전처리합니다."""
    # 원시 데이터가 없으면 파일에서 로드
    if raw_data is None:
        json_files = sorted(glob.glob(str(RAW_DATA_DIR / "wifi_data_*.json")))
        if not json_files:
            print("전처리할 원시 데이터 파일이 없습니다.")
            return None, None, None

        latest_json = json_files[-1]
        print(f"최신 원시 데이터 파일을 사용합니다: {latest_json}")

        with open(latest_json, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

    # 데이터프레임 변환
    df = pd.DataFrame(raw_data)

    # 컬럼명 변경
    column_mapping = {
        'X_SWIFI_MGR_NO': 'mgr_no',
        'X_SWIFI_WRDOFC': 'inst_district',
        'X_SWIFI_MAIN_NM': 'main_nm',
        'X_SWIFI_ADRES1': 'adres1',
        'X_SWIFI_ADRES2': 'adres2',
        'X_SWIFI_INSTL_TY': 'instl_ty',
        'X_SWIFI_INSTL_MBY': 'instl_mby',
        'X_SWIFI_SVC_SE': 'svc_se',
        'X_SWIFI_CMCWR': 'cmcwr',
        'X_SWIFI_CNSTC_YEAR': 'cnstc_year',
        'X_SWIFI_INOUT_DOOR': 'inout_door',
        'X_SWIFI_REMARS3': 'remarks',
        'LAT': 'latitude',
        'LNT': 'longitude',
        'WORK_DTTM': 'work_dttm'
    }

    # 컬럼명 변경
    df.rename(columns=column_mapping, inplace=True)

    # 좌표 데이터 변환
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # 설치년도 변환
    df['cnstc_year'] = pd.to_numeric(df['cnstc_year'], errors='coerce')

    # 결측치 처리
    df = df.dropna(subset=['latitude', 'longitude'])

    # 구별 통계
    district_stats = df['inst_district'].value_counts().reset_index()
    district_stats.columns = ['district', 'count']

    # 설치유형별 통계
    installation_stats = df['instl_ty'].value_counts().reset_index()
    installation_stats.columns = ['installation_type', 'count']

    # 데이터 저장
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

    wifi_csv = PROCESSED_DATA_DIR / f"wifi_data_cleaned_{current_date}.csv"
    district_csv = PROCESSED_DATA_DIR / f"district_stats_{current_date}.csv"
    installation_csv = PROCESSED_DATA_DIR / f"installation_stats_{current_date}.csv"

    df.to_csv(wifi_csv, index=False, encoding='utf-8')
    district_stats.to_csv(district_csv, index=False, encoding='utf-8')
    installation_stats.to_csv(installation_csv, index=False, encoding='utf-8')

    print(f"전처리된 데이터 저장 완료:")
    print(f"- 와이파이 데이터: {wifi_csv}")
    print(f"- 구별 통계: {district_csv}")
    print(f"- 설치유형별 통계: {installation_csv}")

    return df, district_stats, installation_stats

def load_data():
    """처리된 데이터 파일을 로드합니다."""
    # 가장 최신 파일 찾기
    wifi_csv_files = sorted(glob.glob(str(PROCESSED_DATA_DIR / "wifi_data_cleaned_*.csv")))
    district_csv_files = sorted(glob.glob(str(PROCESSED_DATA_DIR / "district_stats_*.csv")))
    installation_csv_files = sorted(glob.glob(str(PROCESSED_DATA_DIR / "installation_stats_*.csv")))

    if not wifi_csv_files or not district_csv_files or not installation_csv_files:
        print("필요한 데이터 파일이 없습니다. 데이터 수집 및 전처리를 먼저 수행해주세요.")
        return None, None, None

    # 가장 최신 파일 선택
    wifi_csv = wifi_csv_files[-1]
    district_csv = district_csv_files[-1]
    installation_csv = installation_csv_files[-1]

    print(f"데이터 파일을 로드합니다:")
    print(f"- 와이파이 데이터: {Path(wifi_csv).name}")
    print(f"- 구별 통계: {Path(district_csv).name}")
    print(f"- 설치유형별 통계: {Path(installation_csv).name}")

    # 데이터 로드
    wifi_data = pd.read_csv(wifi_csv, encoding='utf-8')
    district_data = pd.read_csv(district_csv, encoding='utf-8')
    installation_data = pd.read_csv(installation_csv, encoding='utf-8')

    print(f"데이터 로드 완료 (와이파이 {len(wifi_data):,}개, 구 {len(district_data)}개, 설치유형 {len(installation_data)}개)")

    return wifi_data, district_data, installation_data 