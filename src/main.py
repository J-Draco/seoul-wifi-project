import argparse
from src.data_collection import collect_wifi_data
from src.data_preprocessing import preprocess_wifi_data, load_data
from src.visualization import (
    visualize_district_distribution,
    visualize_installation_distribution,
    visualize_installation_patterns,
    visualize_temporal_patterns,
    create_wifi_map
)
from src.config import VIZ_DIR, api_key_value

def run_data_collection(api_key=None):
    """데이터 수집 단계를 실행합니다."""
    print("\n" + "="*50)
    print("1. 데이터 수집 단계 실행")
    print("="*50)

    if api_key:
        print(f"API 키를 사용하여 데이터 수집을 시작합니다.")
        raw_data = collect_wifi_data(api_key)
    else:
        print("API 키가 제공되지 않았습니다.")
        raw_data = collect_wifi_data(None)

    if raw_data:
        print(f"데이터 수집 완료: {len(raw_data):,}개 항목")
        return raw_data
    else:
        print("데이터 수집을 건너뛰고 기존 데이터를 사용합니다.")
        return None

def run_data_preprocessing(raw_data=None):
    """데이터 전처리 단계를 실행합니다."""
    print("\n" + "="*50)
    print("2. 데이터 전처리 단계 실행")
    print("="*50)

    wifi_data, district_data, installation_data = preprocess_wifi_data(raw_data)

    if wifi_data is not None:
        print(f"데이터 전처리 완료: {len(wifi_data):,}개 항목")
        return wifi_data, district_data, installation_data
    else:
        print("기존 전처리 데이터를 로드합니다.")
        return load_data()

def run_basic_analysis(wifi_data, district_data, installation_data):
    """기본 분석 단계를 실행합니다."""
    print("\n" + "="*50)
    print("3. 기본 분석 단계 실행")
    print("="*50)

    if wifi_data is None or district_data is None or installation_data is None:
        print("필요한 데이터가 없습니다. 데이터 로드를 먼저 수행해주세요.")
        return None

    # 1. 구별 분포 시각화
    district_vis_path = visualize_district_distribution(district_data)

    # 2. 설치유형 분포 시각화
    installation_dist_path = visualize_installation_distribution(installation_data)

    # 3. 설치 패턴 분석
    installation_patterns_path = visualize_installation_patterns(wifi_data)

    print(f"\n기본 분석 완료. 생성된 시각화 파일:")
    print(f"- 구별 분포: {district_vis_path}")
    print(f"- 설치유형 분포: {installation_dist_path}")
    print(f"- 설치 패턴: {installation_patterns_path}")

    return True

def run_advanced_analysis(wifi_data):
    """고급 분석 단계를 실행합니다."""
    print("\n" + "="*50)
    print("4. 고급 분석 단계 실행")
    print("="*50)

    if wifi_data is None:
        print("필요한 데이터가 없습니다. 데이터 로드를 먼저 수행해주세요.")
        return None

    # 시간적 패턴 분석
    temporal_path, yearly_stats = visualize_temporal_patterns(wifi_data)

    print(f"\n고급 분석 완료. 생성된 시각화 파일:")
    print(f"- 시간적 패턴: {temporal_path}")

    return True

def run_map_visualization(wifi_data):
    """지도 시각화 단계를 실행합니다."""
    print("\n" + "="*50)
    print("5. 지도 시각화 단계 실행")
    print("="*50)

    if wifi_data is None:
        print("필요한 데이터가 없습니다. 데이터 로드를 먼저 수행해주세요.")
        return None

    # 지도 시각화
    map_path = create_wifi_map(wifi_data)

    print(f"\n지도 시각화 완료. 생성된 시각화 파일:")
    print(f"- 와이파이 지도: {map_path}")

    return True

def main(api_key=None, run_all=True, collect=False, preprocess=False, basic=True, advanced=True, maps=True):
    """통합 실행 함수: 모든 분석 단계를 순차적으로 실행합니다."""
    print("\n" + "="*50)
    print("서울시 공공 와이파이 데이터 분석 시작")
    print("="*50)

    raw_data = None
    wifi_data = None
    district_data = None
    installation_data = None

    # 데이터 수집 (선택적)
    if run_all or collect:
        raw_data = run_data_collection(api_key)

    # 데이터 전처리 (선택적)
    if run_all or preprocess:
        wifi_data, district_data, installation_data = run_data_preprocessing(raw_data)
    else:
        # 데이터 로드
        print("\n기존 데이터를 로드합니다...")
        wifi_data, district_data, installation_data = load_data()

    # 분석 실행
    if wifi_data is not None:
        # 기본 분석
        if run_all or basic:
            run_basic_analysis(wifi_data, district_data, installation_data)

        # 고급 분석
        if run_all or advanced:
            run_advanced_analysis(wifi_data)

        # 지도 시각화
        if run_all or maps:
            run_map_visualization(wifi_data)

        # 최종 요약
        print("\n" + "="*50)
        print("모든 분석이 완료되었습니다.")
        print(f"결과물은 {VIZ_DIR} 디렉토리에 저장되었습니다.")
        print("="*50)
    else:
        print("\n오류: 데이터를 로드할 수 없습니다. 프로그램을 종료합니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="서울시 공공 와이파이 데이터 분석")
    parser.add_argument("--api-key", type=str, help="서울 열린데이터 광장 API 키")
    parser.add_argument("--collect", action="store_true", help="데이터 수집 단계 실행")
    parser.add_argument("--preprocess", action="store_true", help="데이터 전처리 단계 실행")
    parser.add_argument("--basic", action="store_true", help="기본 분석 단계 실행")
    parser.add_argument("--advanced", action="store_true", help="고급 분석 단계 실행")
    parser.add_argument("--maps", action="store_true", help="지도 시각화 단계 실행")
    parser.add_argument("--all", action="store_true", help="모든 단계 실행")

    args = parser.parse_args()

    # 아무 인자도 주어지지 않았으면 --all로 간주
    if not any([args.collect, args.preprocess, args.basic, args.advanced, args.maps, args.all]):
        args.all = True

    main(
        api_key=args.api_key,
        run_all=args.all,
        collect=args.collect,
        preprocess=args.preprocess,
        basic=args.basic,
        advanced=args.advanced,
        maps=args.maps
    ) 