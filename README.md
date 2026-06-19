# Simple Weather & Time Agent

Google **ADK (Agent Development Kit)** 프레임워크를 기반으로 설계된 간단한 **날씨 및 시간 조회 AI 에이전트**입니다. 이 에이전트는 Vertex AI Agent Engine에 배포되어 작동하며, 공개 API를 통해 전 세계 도시의 날씨 및 현재 시간 정보를 제공합니다.

---

## 🚀 주요 기능
* **실시간 날씨 정보 조회**: Open-Meteo API를 연동하여 전 세계 도시의 현재 기온, 습도, 풍속 등의 날씨 정보를 가져옵니다.
* **실시간 세계 시간 조회**: TimeAPI를 사용하여 지정된 IANA 시간대(Timezone)의 현재 날짜와 시각을 가져옵니다.
* **다국어 및 도시명 매핑**: 사용자 질의("서울", "뉴욕")에 맞춰 Gemini LLM이 적절한 영문 도시명이나 IANA 시간대 식별자로 파라미터를 자동 변환하여 도구를 호출합니다.

---

## 📁 디렉터리 구조
```
simple_agent/
├── README.md           # 실행 및 배포 설명서
├── pyproject.toml      # uv 의존성 설정 파일
├── .env                # 로컬 환경 변수 설정 파일 (기본 생성 필요)
├── __init__.py         # 패키지 진입점
├── agent.py            # 메인 에이전트 및 도구(Tool) 정의
└── agent_runtime.py    # Vertex AI Agent Engine 배포 스크립트
```

---

## ⚙️ 환경 설정 및 배포 방법

### 1. Agent Platform API 활성화
Google Cloud Console에 접속하여 **Agent Platform** 메뉴로 이동한 뒤, 화면 상단에 있는 **Enable API** 버튼을 클릭하여 에이전트 구동에 필요한 API들을 활성화해주세요.

### 2. 코드 다운로드 (Git Clone)
GitHub에서 프로젝트 저장소를 클론합니다:
```bash
git clone git@github.com:kiwonlee/simple_agent.git
cd simple_agent
```

### 3. 가상환경 구성 (`uv` 사용)
[uv](https://github.com/astral-sh/uv)는 초고속 Python 패키지 인스톨러 및 프로젝트 관리자입니다. `uv`가 설치되어 있지 않다면 설치한 후 아래 명령을 수행하세요:

```bash
# 가상환경 생성 및 활성화
uv venv
source .venv/bin/activate

# 의존성 패키지 동기화 및 가용화
uv sync
```

### 4. 환경 변수 설정 (`.env`)
`.env.template` 파일을 복사하여 `.env` 파일을 생성하고, `sed` 명령어를 이용해 실제 GCP 프로젝트 ID와 GCS 버킷 URI 값을 설정합니다:

```bash
export PROJECT_ID=""
export GCS_BUCKET=""  # gs://xxxx
```

```bash
# .env.template 복사하여 .env 생성
cp .env.template .env

# sed를 활용한 환경변수 값 일괄 할당 (실제 값으로 치환하여 사용하세요)
sed -i "s/YOUR_GOOGLE_CLOUD_PROJECT/${PROJECT_ID}/g" .env
sed -i "s|YOUR_STAGING_BUCKET_URI|${GCS_BUCKET}|g" .env
```

`.env` 파일이 실제 값으로 올바르게 채워졌는지 확인합니다:


### 5. GCS 스테이징 버킷 생성
Vertex AI Agent Engine 배포 시 에이전트 소스코드 등을 저장할 스테이징 버킷이 필요합니다. GCS 버킷이 아직 없다면 아래와 같이 생성합니다:

```bash
gcloud storage buckets create ${GCS_BUCKET} --location=us-central1
```


### 6. Vertex AI Agent Engine에 배포
`agent_runtime.py` 스크립트를 실행하면 ADK로 정의된 에이전트가 패키징되어 GCP 클라우드 환경(Agent Runtime)에 자동으로 빌드 및 배포됩니다:

```bash
uv run agent_runtime.py
```


배포가 성공적으로 완료되면 터미널 출력 하단에 생성된 **Agent Identity (서비스 어카운트 주소)** 및 해당 계정에 부여해야 하는 **IAM 권한 부여 명령어(gcloud)** 리스트가 출력됩니다. 출력되는 명령어 가이드에 따라 서비스 계정에 필요한 GCP 권한 권한을 부여해 주어야 에이전트가 정상적으로 구동됩니다.
