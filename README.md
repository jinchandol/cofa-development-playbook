# COFA Development Playbook

180분 내 요구사항 구현, 데이터 검증, 판단 근거 설명을 연습하는 개인용 플레이북.
SK하이닉스 또는 시험 주관사의 공식 자료가 아니다. 시험 조건은 사용자 제공 가정이며 실제 공지·README·도구/자료 반입 규정이 우선한다.
모든 모의 데이터와 업무 규칙은 합성이다. 실제 문제·회사 데이터·개인정보는 포함하지 않는다.

## 시작

1. 실제 과제 README와 데이터만 읽고 [PROMPTS.md](PROMPTS.md)의 Analyze & Interview를 실행한다.
2. [CONTRACT 템플릿](templates/CONTRACT.md), [CONTROL 템플릿](templates/CONTROL.md)을 과제 폴더로 복사한다.
3. 최소 계약을 확정하면 Build → Independent Review → Deliver & Explain 순서로 진행한다.
4. AI 없이 6문항에 각각 5분 동안 답한다. 서술형 연습 30분은 개발 180분과 별도로 둔다.

우선순위: **필수 기능 > 데이터 정확성 > 실행 검증 > 판단 근거 > 도구 편의성**.
새 Skill·MCP·설치 스크립트·병렬 에이전트는 기본 구성에 필요하지 않다.

## 180분 운영 예시

| 구간 | 작업 | 다음 단계로 넘어가는 조건 |
|---|---|---|
| 0–30분 | README/데이터 분석, 핵심 현업 질문 | 필수 기능의 최소 계약, 불확실성/차단 항목 식별 |
| 30–120분 | 가장 작은 전체 흐름 → 필수 기능 | 실행 가능, 요구사항별 자체 테스트 |
| 120–155분 | 검토·반례·수정·재검증 | P0/P1 해소 또는 미해결 근거 공개 |
| 155–180분 | 실행/제출 점검, 설명 연습 | 파일·명령·결과·한계 일치 |

시간표는 권장 상한이다. 분석 완벽주의로 구현을 지연하지 않는다. 답이 없으면 영향 없는 기능부터 구현하고, 업무 정책은 미확정으로 유지한다.
P0: 실행 불가/원본 훼손/광범위 데이터 손상. P1: 필수 기능 오답·데이터 누락·계약 위반. P2: 핵심 기능을 막지 않는 사용성 문제.

## 모의 과제 실행

Python 3.10 이상과 브라우저만 필요하다. 패키지 설치 없음.

```powershell
cd practice/route-service
python app.py --port 8765
# 브라우저에서 http://127.0.0.1:8765
```

다른 터미널에서:

```powershell
cd practice/route-service
python profile_data.py
python -m unittest discover -s tests -v
python -m unittest discover -s reviewer -p "test_*.py" -v
python evaluator/score.py
```

독립 연습을 하려면 처음에는 **practice/route-service/README.md와 data/만** 읽는다.
`evaluator/`, 이미 작성된 `CONTRACT.md`, `CONTROL.md`, `rehearsal/`, 구현 및 테스트는 첫 분석 전에 열지 않는다.
평가자는 `evaluator/RULES.md`로 질문에 답하고, 분석자가 제출한 질문/탐지 목록을 정답과 대조한다.
폴더 분리는 접근 통제가 아니다. 블라인드 연습은 별도 사본에서 evaluator/와 해설·구현을 제거해 진행한다.
현재 포함된 완성 예시는 해설용이며 시간제한 실험의 성적이 아니다.

## 파일 안내

```text
README.md / AGENTS.md / PROMPTS.md
templates/CONTRACT.md / CONTROL.md
practice/route-service/
  README.md                 # 응시자 문제
  data/*.csv                # 수정 금지 합성 원본
  app.py / domain.py        # 표준 라이브러리 서버·업무 로직
  profile_data.py            # 스키마/관계/손실 검사
  web/index.html / app.js / style.css
  tests/test_service.py      # Developer 실행 검증
  reviewer/test_adversarial.py # 별도 기준의 반례
  CONTRACT.md / CONTROL.md   # 리허설 결과 계약·판단
  rehearsal/                # ANALYSIS/INTERVIEW/REVIEW/REPORT.md,
                            # baseline/evidence/score.json, verify.py, cli_smoke.py
  evaluator/                # RULES.md, defects.json, score.py (초기 분석 금지)
```

실제 실행 결과·검출률·현재 한계는 [CONTROL](practice/route-service/CONTROL.md)과 [리허설 보고](practice/route-service/rehearsal/REPORT.md)에 기록한다.
`.gitattributes`는 체크아웃 환경에 따라 CSV 줄바꿈과 기준 해시가 달라지는 것을 방지한다.

## 제출 전

- README의 필수 기능과 AC를 실제 결과에 연결했는가?
- 원본 해시와 조인/격리/중복제거 전후 행 수를 확인했는가?
- 업무 답변의 근거와 미확정을 구분했는가?
- 실행한 테스트만 통과로 기록했는가? Reviewer 분리 여부가 정확한가?
- 개발자가 WHAT / WHY / HOW / VERIFY와 남은 한계를 설명할 수 있는가?
- 실제 시험의 AGENTS.md 제출 요구·AI 허용 범위·반입 규정을 확인했는가?
