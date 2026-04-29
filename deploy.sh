#!/bin/bash
# 🏫 JPCampus deployment helper script (simple 3-mode)

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-starful-258005}"
SITE_DOMAIN="${SITE_DOMAIN:-https://jpcampus.net}"
COMMIT_MSG="update: auto-generated campus contents & data $(date '+%Y-%m-%d %H:%M')"

MODE="full"
DO_GIT=false
DO_CLOUD_DEPLOY=false

print_step() { echo ""; echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${BOLD}${CYAN}  $1${NC}"; echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }
print_ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
print_warn() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }
print_err()  { echo -e "${RED}  ❌ $1${NC}"; }
print_info() { echo -e "  ℹ️  $1"; }

usage() {
    cat <<'EOF'
Usage: ./deploy.sh [MODE] [OPTIONS]

Modes (default: full)
  --full           Generate content + build data + SEO guard
  --content-only   Generate content + build data only
  --deploy-only    Trigger Cloud Build deploy only

Options
  --with-git       Commit and push generated changes
  --with-deploy    Trigger deploy after selected mode
  --help           Show this help

Environment overrides
  GCP_PROJECT_ID   Default: starful-258005
  SITE_DOMAIN      Default: https://jpcampus.net
EOF
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        print_err "Missing required command: $1"
        exit 1
    fi
}

check_env() {
    print_step "STEP 0  |  환경 체크"
    [ ! -f ".env" ] && { print_err ".env 파일이 없습니다."; exit 1; }
    print_ok ".env 확인"
}

generate_content() {
    print_step "STEP A  |  콘텐츠 생성"
    if [ -f "scripts/2.generate_ai_guides.py" ]; then
        python3 scripts/2.generate_ai_guides.py
    else
        print_warn "scripts/2.generate_ai_guides.py 없음, 건너뜀"
    fi

    if [ -f "scripts/3.create_korean_content.py" ]; then
        python3 scripts/3.create_korean_content.py
    else
        print_warn "scripts/3.create_korean_content.py 없음, 건너뜀"
    fi

    if [ -f "scripts/auto_generate_featured.py" ]; then
        python3 scripts/auto_generate_featured.py
    else
        print_warn "scripts/auto_generate_featured.py 없음, 건너뜀"
    fi

    print_ok "콘텐츠 생성 완료"
}

build_data() {
    print_step "STEP B  |  데이터 빌드"
    python3 scripts/build_data.py
    print_ok "JSON/sitemap 빌드 완료"
}

run_seo_guard() {
    print_step "STEP C  |  SEO 가드 검사"
    python3 scripts/seo_guard.py
    print_ok "SEO 가드 통과"
}

git_push_changes() {
    print_step "STEP D  |  GitHub Push"
    git add .
    if ! git diff-index --quiet HEAD --; then
        git commit -m "$COMMIT_MSG"
        git push origin main
        print_ok "GitHub push 완료"
    else
        print_warn "변경 사항 없음"
    fi
}

deploy_cloud_run() {
    print_step "STEP E  |  Cloud Build 배포"
    set -a
    source ".env"
    set +a

    if [ -n "${GOOGLE_MAPS_API_KEY:-}" ]; then
        gcloud builds submit \
          --config=cloudbuild.yaml \
          --project "$GCP_PROJECT_ID" \
          --substitutions="_GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}"
    else
        print_warn "GOOGLE_MAPS_API_KEY 없음, substitutions 없이 배포 진행"
        gcloud builds submit --config=cloudbuild.yaml --project "$GCP_PROJECT_ID"
    fi
    print_ok "Cloud Build 배포 완료"
}

for arg in "$@"; do
    case "$arg" in
        --full) MODE="full" ;;
        --content-only) MODE="content-only" ;;
        --deploy-only) MODE="deploy-only" ;;
        --with-git) DO_GIT=true ;;
        --with-deploy) DO_CLOUD_DEPLOY=true ;;
        --help|-h) usage; exit 0 ;;
        *)
            print_err "Unknown argument: $arg"
            usage
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"
START_TIME=$SECONDS
if [ -t 1 ]; then clear; fi

print_info "Mode: $MODE"
print_info "Site: $SITE_DOMAIN"
print_info "Project: $GCP_PROJECT_ID"

check_env
require_cmd python3
require_cmd gcloud

case "$MODE" in
    full)
        generate_content
        build_data
        run_seo_guard
        ;;
    content-only)
        generate_content
        build_data
        ;;
    deploy-only)
        DO_CLOUD_DEPLOY=true
        ;;
esac

if [ "$DO_GIT" = true ]; then
    require_cmd git
    git_push_changes
fi

if [ "$DO_CLOUD_DEPLOY" = true ]; then
    deploy_cloud_run
fi

ELAPSED=$((SECONDS - START_TIME))
print_step "DONE  |  완료 요약"
echo -e "${BOLD}${GREEN}  🎉 JPCampus 작업 완료${NC}"
echo -e "  ⏱️  총 소요 시간  : $(( ELAPSED / 60 ))분 $(( ELAPSED % 60 ))초"
echo -e "  🌐 사이트 주소   : ${SITE_DOMAIN}"

if [[ "$OSTYPE" == "darwin"* ]] && [[ "${AUTO_REGISTER_RUN:-0}" != "1" ]]; then
    osascript -e 'display notification "JPCampus 배포 스크립트 완료" with title "Deploy"' 2>/dev/null || true
fi
