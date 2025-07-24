import os
import sys
import subprocess
import warnings
from pathlib import Path
import matplotlib.pyplot as plt

# 경고 메시지 무시
warnings.filterwarnings('ignore')

# 프로젝트 루트 설정
PROJECT_ROOT = Path(os.getcwd())

# 한글 폰트 설정
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'  # 기본 한글 폰트
except:
    print("한글 폰트 설정에 실패했습니다. 시스템에 '맑은 고딕' 폰트가 설치되어 있는지 확인하세요.")

# 시각화 설정
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.grid'] = True
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.unicode_minus'] = False

# 경로 설정
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
VIZ_DIR = RESULTS_DIR / "visualizations"

# 디렉토리 생성
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR, VIZ_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# API 키 저장용 전역 변수
api_key_value = None 