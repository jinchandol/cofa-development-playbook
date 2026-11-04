#!/bin/sh
# 과제 README.md가 있는 폴더에서 sh <플레이북 경로>/install.sh 실행.
# 과제 AGENTS.md에 참조 블록만 추가한다. 원본/설정 복사·이동·삭제 없음.
set -eu

COFA_KIT_ROOT=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
COFA_TASK_ROOT=$(pwd -P)
COFA_AGENT_FILE="$COFA_TASK_ROOT/AGENTS.md"
COFA_BEGIN='<!-- cofa-development-playbook:begin -->'
COFA_END='<!-- cofa-development-playbook:end -->'

if [ "$COFA_KIT_ROOT" = "$COFA_TASK_ROOT" ] || [ ! -f "$COFA_TASK_ROOT/README.md" ]; then
  printf '%s\n' '과제 README.md가 있는 폴더에서 실행하세요. 플레이북 폴더에서는 설치하지 않습니다.' >&2
  exit 1
fi
for COFA_SOURCE in AGENTS.md PROMPTS.md templates/CONTRACT.md templates/DECISIONS.md; do
  if [ ! -f "$COFA_KIT_ROOT/$COFA_SOURCE" ]; then
    printf '플레이북 파일이 없습니다: %s\n' "$COFA_SOURCE" >&2
    exit 1
  fi
done
if [ -L "$COFA_AGENT_FILE" ] || { [ -e "$COFA_AGENT_FILE" ] && [ ! -f "$COFA_AGENT_FILE" ]; }; then
  printf '%s\n' 'AGENTS.md가 일반 파일이 아니어서 변경하지 않았습니다.' >&2
  exit 1
fi

COFA_KIT_REF=$COFA_KIT_ROOT
if command -v cygpath >/dev/null 2>&1; then
  COFA_KIT_REF=$(cygpath -m "$COFA_KIT_ROOT")
fi
COFA_BLOCK=$(cat <<EOF
$COFA_BEGIN
## COFA 플레이북 참고

과제 원본 README.md·기존 AGENTS.md·공식 지침을 우선한다.
플레이북 경로: $COFA_KIT_REF
작업 전에 $COFA_KIT_REF/AGENTS.md를 읽고 지침을 적용한다.
플레이북 안의 PROMPTS.md·templates/ 경로는 위 플레이북 기준이다.
과제 README.md·데이터·결과물 경로는 과제 작업 폴더 기준이다.
시작 요청과 Reviewer 전달문은 $COFA_KIT_REF/PROMPTS.md를 따른다.
$COFA_END
EOF
)
# 이전 버전의 완전한 참조 블록도 기존 내용을 보존하며 인식한다.
COFA_LEGACY_BLOCK=$(printf '%s\n' "$COFA_BLOCK" | sed 's|PROMPTS.md·templates/ 경로|PROMPTS.md·templates/·practice/ 경로|')
if [ -f "$COFA_AGENT_FILE" ]; then
  if grep -Fq "$COFA_BEGIN" "$COFA_AGENT_FILE" || grep -Fq "$COFA_END" "$COFA_AGENT_FILE"; then
    if COFA_INSTALLED=$(awk -v begin="$COFA_BEGIN" -v end="$COFA_END" '
      { sub(/\r$/, "") }
      $0 == begin { starts++; if (inside || ends) bad=1; inside=1 }
      inside { print }
      $0 == end { ends++; if (!inside) bad=1; inside=0 }
      END { if (starts != 1 || ends != 1 || inside || bad) exit 1 }
    ' "$COFA_AGENT_FILE") && { [ "$COFA_INSTALLED" = "$COFA_BLOCK" ] || [ "$COFA_INSTALLED" = "$COFA_LEGACY_BLOCK" ]; }; then
      printf '%s\n' '이미 같은 플레이북이 연결되어 있습니다. 변경 없음.'
      exit 0
    fi
    printf '%s\n' '기존 참조 블록이 불완전하거나 다른 경로를 사용합니다. AGENTS.md를 변경하지 않았습니다.' >&2
    exit 1
  fi
fi

printf '\n\n%s\n' "$COFA_BLOCK" >>"$COFA_AGENT_FILE"

printf '%s\n' '연결 완료: 과제 AGENTS.md 끝에 참조 블록을 추가했습니다.'
printf '%s\n' '과제 폴더에서 Codex에 AGENTS.md를 읽고 PROMPTS.md의 시작 요청대로 진행하라고 지시하세요.'
