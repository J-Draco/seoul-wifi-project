import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import folium
from folium import plugins
from src.config import VIZ_DIR

def visualize_district_distribution(district_data):
    """구별 와이파이 설치 현황 시각화"""
    plt.figure(figsize=(12, 6))

    # 데이터 정렬
    sorted_data = district_data.sort_values('count', ascending=False).copy()

    # 막대 그래프 생성
    bars = plt.bar(range(len(sorted_data)), sorted_data['count'], color='skyblue')

    # 제목과 레이블 설정
    plt.title('서울시 구별 공공 와이파이 설치 현황', pad=20, size=16)
    plt.xlabel('자치구', size=12)
    plt.ylabel('설치 수', size=12)

    # 상위 5개 구에 대한 강조
    for i in range(5):
        bars[i].set_color('royalblue')

    plt.xticks(range(len(sorted_data)),
              sorted_data['district'],
              rotation=45,
              ha='right')

    # 값 레이블 추가
    for i, v in enumerate(sorted_data['count']):
        plt.text(i, v, format(v, ','), ha='center', va='bottom')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 결과 저장
    output_path = VIZ_DIR / "district_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"구별 분포 시각화 완료: {output_path}")
    return output_path

def visualize_installation_distribution(installation_data):
    """설치 유형별 분포 시각화"""
    plt.figure(figsize=(14, 7))

    # 데이터 정렬
    sorted_data = installation_data.sort_values('count', ascending=False).copy()

    # 상위 10개만 선택
    top_data = sorted_data.head(10)

    # 막대 그래프 생성
    plt.barh(range(len(top_data)), top_data['count'], color='lightgreen')

    # 제목과 레이블 설정
    plt.title('설치 유형별 와이파이 분포 (상위 10개)', pad=20, size=16)
    plt.xlabel('설치 수', size=12)
    plt.ylabel('설치 유형', size=12)

    plt.yticks(range(len(top_data)), top_data['installation_type'])

    # 값 레이블 추가
    for i, v in enumerate(top_data['count']):
        plt.text(v, i, format(v, ','), va='center')

    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 결과 저장
    output_path = VIZ_DIR / "installation_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"설치유형 분포 시각화 완료: {output_path}")
    return output_path

def visualize_installation_patterns(wifi_data):
    """설치 유형과 지역 특성의 상관관계 분석"""
    # 구별, 설치유형별 교차분석
    cross_table = pd.crosstab(wifi_data['inst_district'], wifi_data['instl_ty'])

    # 빈도가 높은 설치유형만 선택 (상위 8개)
    top_types = wifi_data['instl_ty'].value_counts().head(8).index
    cross_table_filtered = cross_table[top_types]

    # 히트맵 시각화
    plt.figure(figsize=(16, 10))
    sns.heatmap(cross_table_filtered, annot=True, fmt='d', cmap='YlOrRd', linewidths=0.5)
    plt.title('구별 주요 설치유형 분포 현황', size=18)
    plt.xlabel('설치유형', size=14)
    plt.ylabel('자치구', size=14)

    # 결과 저장
    output_path = VIZ_DIR / 'installation_patterns.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"설치 패턴 시각화 완료: {output_path}")
    return output_path

def visualize_temporal_patterns(wifi_data):
    """시간대별 설치 패턴 분석"""
    # 결측값 제거
    valid_years = wifi_data.dropna(subset=['cnstc_year'])

    # 데이터 타입 변환 및 연도별 설치 현황
    valid_years['cnstc_year'] = valid_years['cnstc_year'].astype(int)
    yearly_inst = valid_years['cnstc_year'].value_counts().sort_index()

    # 이상치 제거 (2000년 이전 데이터 필터링)
    yearly_inst = yearly_inst[yearly_inst.index >= 2000]

    # 연도별 누적 설치 수 계산
    cumulative_inst = yearly_inst.cumsum()

    # 시각화
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 연도별 설치 수
    bars = ax1.bar(yearly_inst.index.astype(str), yearly_inst.values, color='skyblue')
    ax1.set_title('연도별 공공 와이파이 설치 현황', size=16)
    ax1.set_ylabel('설치 수', size=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # 최대값 강조
    max_year = yearly_inst.idxmax()
    max_idx = list(yearly_inst.index).index(max_year)
    bars[max_idx].set_color('royalblue')
    ax1.text(max_idx, yearly_inst.max(), f'{yearly_inst.max():,}개',
             ha='center', va='bottom', fontweight='bold')

    # 누적 설치 수
    ax2.plot(cumulative_inst.index.astype(str), cumulative_inst.values,
             marker='o', linestyle='-', color='forestgreen')
    ax2.set_title('연도별 누적 설치 현황', size=16)
    ax2.set_xlabel('설치년도', size=12)
    ax2.set_ylabel('누적 설치 수', size=12)
    ax2.grid(linestyle='--', alpha=0.7)

    # x축 레이블 설정
    plt.xticks(rotation=45)

    plt.tight_layout()

    # 결과 저장
    output_path = VIZ_DIR / 'temporal_patterns.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"시간적 패턴 시각화 완료: {output_path}")
    return output_path, yearly_inst

def create_wifi_map(wifi_data, sample_ratio=0.1):
    """기본 와이파이 지도 시각화"""
    print("기본 지도 시각화 생성 중...")

    # 서울 중심 좌표
    SEOUL_CENTER = [37.5665, 126.9780]

    # 기본 지도 생성
    m = folium.Map(
        location=SEOUL_CENTER,
        zoom_start=11,
        tiles='CartoDB positron'
    )

    # 클러스터 마커 추가
    marker_cluster = plugins.MarkerCluster().add_to(m)

    # 데이터 샘플링 (너무 많은 마커를 표시하면 성능 저하)
    sample_size = int(len(wifi_data) * sample_ratio)
    sampled_data = wifi_data.sample(n=sample_size, random_state=42)

    print(f"전체 {len(wifi_data):,}개 중 {sample_size:,}개 데이터 샘플링")

    # 마커 추가
    for idx, row in sampled_data.iterrows():
        popup_html = f"""
        <div style="width: 200px">
            <b>{row['main_nm']}</b><br>
            주소: {row['adres1']}<br>
            설치유형: {row['instl_ty']}<br>
            설치년도: {row.get('cnstc_year', '정보없음')}
        </div>
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['main_nm']
        ).add_to(marker_cluster)

    # 결과 저장
    output_path = VIZ_DIR / "wifi_map.html"
    m.save(str(output_path))

    print(f"기본 지도 시각화 완료: {output_path}")
    return output_path 