#!/bin/sh
# 과제 README.md가 있는 폴더에서 sh <COFA Kit 경로>/install.sh 실행.
# 과제 AGENTS.md를 새로 생성한다. 이미 작성한 파일에는 참조 블록만 추가한다.
set -eu

COFA_KIT_ROOT=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
COFA_TASK_ROOT=$(pwd -P)
COFA_AGENT_FILE="$COFA_TASK_ROOT/AGENTS.md"
COFA_BEGIN='<!-- cofa-development-playbook:begin -->'
COFA_END='<!-- cofa-development-playbook:end -->'

if [ "$COFA_KIT_ROOT" = "$COFA_TASK_ROOT" ] || [ ! -f "$COFA_TASK_ROOT/README.md" ]; then
  printf '%s\n' '과제 README.md가 있는 폴더에서 실행하세요. COFA Kit 폴더에서는 설치하지 않습니다.' >&2
  exit 1
fi
for COFA_SOURCE in AGENTS.md PROMPTS.md templates/CONTRACT.md templates/DECISIONS.md; do
  if [ ! -f "$COFA_KIT_ROOT/$COFA_SOURCE" ]; then
    printf 'COFA Kit 파일이 없습니다: %s\n' "$COFA_SOURCE" >&2
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
## COFA Kit 참고

과제 원본 README.md·공식 지침을 우선한다.
COFA Kit 경로: $COFA_KIT_REF
작업 전에 $COFA_KIT_REF/AGENTS.md를 읽고 지침을 적용한다.
COFA Kit 안의 PROMPTS.md·templates/ 경로는 위 COFA Kit 기준이다.
과제 README.md·데이터·결과물 경로는 과제 작업 폴더 기준이다.
시작 요청과 Reviewer 전달문은 $COFA_KIT_REF/PROMPTS.md를 따른다.
$COFA_END
EOF
)
# 이전 명칭의 완전한 참조 블록은 기존 내용을 보존하며 인식한다.
COFA_LEGACY_BLOCK=$(cat <<EOF
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
COFA_LEGACY_PRACTICE_BLOCK=$(printf '%s\n' "$COFA_LEGACY_BLOCK" | sed 's|^플레이북 안의 PROMPTS.md·templates/ 경로는 위 플레이북 기준이다\.$|플레이북 안의 PROMPTS.md·templates/·practice/ 경로는 위 플레이북 기준이다.|')
if [ -f "$COFA_AGENT_FILE" ]; then
  if grep -Fq "$COFA_BEGIN" "$COFA_AGENT_FILE" || grep -Fq "$COFA_END" "$COFA_AGENT_FILE"; then
    if COFA_INSTALLED=$(awk -v begin="$COFA_BEGIN" -v end="$COFA_END" '
      { sub(/\r$/, "") }
      $0 == begin { starts++; if (inside || ends) bad=1; inside=1 }
      inside { print }
      $0 == end { ends++; if (!inside) bad=1; inside=0 }
      END { if (starts != 1 || ends != 1 || inside || bad) exit 1 }
    ' "$COFA_AGENT_FILE") && { [ "$COFA_INSTALLED" = "$COFA_BLOCK" ] || [ "$COFA_INSTALLED" = "$COFA_LEGACY_BLOCK" ] || [ "$COFA_INSTALLED" = "$COFA_LEGACY_PRACTICE_BLOCK" ]; }; then
      printf '%s\n' '이미 같은 COFA Kit이 연결되어 있습니다. 변경 없음.'
      exit 0
    fi
    printf '%s\n' '기존 참조 블록이 불완전하거나 다른 경로를 사용합니다. AGENTS.md를 변경하지 않았습니다.' >&2
    exit 1
  fi
fi

if [ -f "$COFA_AGENT_FILE" ]; then
  printf '\n\n%s\n' "$COFA_BLOCK" >>"$COFA_AGENT_FILE"
else
  (set -C; printf '# 과제 작업 지침\n\n%s\n' "$COFA_BLOCK" >"$COFA_AGENT_FILE")
fi

printf '%s\n' '준비 완료: 과제 AGENTS.md에 COFA Kit 지침을 연결했습니다.'
printf '%s\n' '과제 폴더에서 Codex에 AGENTS.md를 읽고 PROMPTS.md의 시작 요청대로 진행하라고 지시하세요.'
