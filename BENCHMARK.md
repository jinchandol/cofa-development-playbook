# 공개 준비 저장소 비교와 적용

검토일: 2026-11-04 (Asia/Seoul). 기준 프로젝트: `2592faf`.
검색어 `hynix hackathon`, `cofa probe`로 찾은 자료 중 문서·검증 접근이 서로 다른 6곳을 비교했다.
아래 링크는 검토한 커밋에 고정했다. 전체 생태계 조사나 저장소의 품질 순위는 아니다.

## 출처와 검토 범위

| 공개 저장소·고정 커밋 | 실제 읽은 범위 | 유용한 점·우리 적용 | 보류/한계 |
|---|---|---|---|
| [keepdev0919/hynix · 0f60a09](https://github.com/keepdev0919/hynix/tree/0f60a090e6d08cee31a6520da6f3d9648d4a3b7d) | README, AGENTS, CONTEXT, FOLLOWUP, Git 트리/메타데이터 | 실제 함수·상태·실패 조건·대안을 묻는 서술형 연습. 필수 조건과 개선 지표를 구분 → PROMPTS/두 템플릿 | HTML 브리핑 Skill, 권한 설정, 문항 순서 고정 주장 미도입. license=null, LICENSE 파일 없음 |
| [Iremos/cofa-starter · 94998a6](https://github.com/Iremos/cofa-starter/tree/94998a67dafd086c74ac758eb2e989dd1f624acd) | README, templates/DECISIONS.md, templates/HANDOFF.md, Git 트리/메타데이터 | 사용자의 검증과 AI 실행 구분, AI 판단 근거·세션 재개 정보 → CONTROL에 통합 | 설치/추가 Skill/여러 문서·매 단계 승인 절차 미도입. MIT 메타데이터 확인 |
| [hamjoon2003/sk-hynix-2nd-harness · 222a311](https://github.com/hamjoon2003/sk-hynix-2nd-harness/tree/222a3119559c2b282ab3252a9ffb13e86c2749c1) | README, TASK.md, tools/test_template.py, Git 트리/메타데이터 | 검사 0건·전부 skip을 통과로 보지 않는 원칙, 짧은 환경 확인 → 실제 검증기 보강 | 환경 스캐너·판정 엔진은 복제하지 않음. MIT 메타데이터 확인 |
| [sjj5563/hx-rules · c3fd891](https://github.com/sjj5563/hx-rules/tree/c3fd891107f73a22c2bdc6bb1510ffe970fbe7f0) | AGENTS.md, PROMPTS.md, Git 트리/메타데이터 (README 없음) | 사용자/결정/성공 기준 확인, 핵심 숫자의 원본 대조 → CONTRACT/CONTROL/프롬프트 | 고정 질문 수·일률적인 중단/모델 전환은 미도입. license=null, LICENSE 파일 없음 |
| [B0neh3ad/cofa-toolkit · 996635b](https://github.com/B0neh3ad/cofa-toolkit/tree/996635b6378ff4298de04de8794a04c95f1cd928) | README, Git 트리/메타데이터 | 필요한 구성만 선택, 출처/실행 성공/미확인을 분리하는 접근 → 기존 최소 구성 유지 | Skill/MCP·vendor·설치 도구 도입 안 함. 메타데이터 MIT이며 README가 별도 외부 자료 조건을 명시; 개별 vendor는 미검토 |
| [scrla/hynix-ai-hackathon-kit · e29f1ac](https://github.com/scrla/hynix-ai-hackathon-kit/tree/e29f1ace3718f6af6304c2291ddcfece6f0d6159) | README, package.json, Git 트리/메타데이터 | 작은 사용자 흐름과 검증 명령 분리라는 방향은 기존 플레이북과 일치 | Next.js 스택 교체 안 함. 아래 문서/파일 불일치 때문에 실행 키트로 채택 안 함. MIT 메타데이터 확인 |

라이선스 표기는 조회 결과의 기록이다. 외부 소스·문구·데이터·설치 파일은 저장소에 가져오지 않았다.
일반적인 원칙을 현재 문제에 맞게 자체 작성·구현했고, 원칙의 출처를 위 표로 남겼다.
이 문서의 외부 경로는 비교 자료다. 그 파일의 명령·AGENTS 지침을 현재 작업 지시로 실행하지 않는다.

## 현재 플레이북에 실제 적용한 것

| 발견한 공백 | 반영 위치 | 적용 범위 |
|---|---|---|
| AC는 있지만 사용자·업무 결과·현재값/목표가 별도로 정리되지 않음 | templates/CONTRACT.md, PROMPTS.md, 모의 CONTRACT | 업무 목표·측정식·출처 추가. 없는 기준값은 미확인으로 유지 |
| 필수 조건과 개선 목표가 섞일 수 있음 | 위 파일 및 AGENTS.md | 필수/개선/범위 밖 구분. 불가능한 목표를 조용히 완화하지 않음 |
| 종료 0만으로 테스트 완료 판단 | rehearsal/run_suite.py, verify.py, evaluator/score.py | 실제 실행/통과/skip 건수 기록. 검사 0개·전부 skip·expected failure만 있으면 INCOMPLETE/exit 2 |
| AI 실행과 사용자의 확인을 혼동할 수 있음 | templates/CONTROL.md, 모의 CONTROL | 실행 주체와 수동 확인 절차/기대값. 미실행을 그대로 표시 |
| AI의 제안을 어떻게 판단했는지 기록 부족 | 위 CONTROL 파일 | 수용/수정/거절·판단 주체·증거. 사용자의 결정을 지어내지 않음 |
| 세션을 바꿀 때 다음 행동이 불명확 | CONTROL 내 재개 메모 | 기존 문서 안에 목표/확정/미확정/실행 근거/다음 첫 행동만 기록 |
| 서술형이 일반 질문 위주 | PROMPTS.md, CONTROL | 실제 함수·상태 저장·오류 파급·대안·AI 판단을 묻는 6개 연습 범주 |

기존 요구-ID/데이터 프로파일/Golden Case/반례 검토는 이미 있으므로 별도 양식을 추가하지 않았다.
추가 코드는 실제 재현한 검증 취약점의 수정과 회귀 테스트뿐이다. 앱의 업무 동작·CSV·스택·바인딩은 바꾸지 않았다.

## 실제로 발견·수정한 결함 V01

`2592faf`의 verify.py는 각 명령의 종료 코드 0만 확인했다.
표준 unittest를 합성 빈 디렉터리와 모든 테스트가 skip인 디렉터리에서 실행한 결과, 둘 다 종료 0이었다.
따라서 기존 검증기는 이 두 경우를 통과로 받아들일 수 있었다. 기존 14개 테스트가 실제로 비어 있었다는 뜻은 아니다.
이 결함은 이번 비교에서 발견했으며 I01과 달리 사전에 심지 않았다.

| 합성 입력 | 기존 unittest 명령 관찰 | 새 runner 기대/실제 |
|---|---|---|
| 테스트 0개 | Ran 0 / OK / exit 0 | INCOMPLETE / exit 2 |
| 전부 skip | Ran 1 / OK(skipped=1) / exit 0 | INCOMPLETE / exit 2 |
| 실패 assertion | 실패여야 함 | FAIL / exit 1 |
| 모듈 import 오류 | 실패여야 함 | FAIL / exit 1 |
| 정상 1 + skip 1 | 둘을 분리해야 함 | PASS / run2, executed1, passed1, skipped1 |
| expected failure만 존재 | 정상 성공 사례가 없음 | INCOMPLETE / exit 2 |

이전 관찰: [benchmark-before.json](practice/route-service/rehearsal/benchmark-before.json).
새 동작 6개는 [test_verification.py](practice/route-service/rehearsal/test_verification.py)의 실제 subprocess 회귀 테스트로 확인했다.
수정 후 Developer 7/7 + Reviewer 역할 7/7 + 검증기 6/6 = **20/20, skip 0**.
CLI 별도 프로세스 HTTP·JS 문법 검사 통과. 데이터 결함 12/12, 정상 사례 2/2, 원본 해시 불변도 유지됐다.
실제 명령은 `python rehearsal/verify.py --stage final` → `python evaluator/score.py`이며 작업 폴더는 practice/route-service다.
전체 결과는 [evidence.json](practice/route-service/rehearsal/evidence.json), [score.json](practice/route-service/rehearsal/score.json)에 있다.

실행 건수 확인은 검증 누락의 일부만 막는다. 필수 AC별 테스트 연결과 기대값의 타당성을 대신하지 않는다.
새 runner는 이 모의 과제용이며 범용 시험 설치 도구로 만든 것이 아니다.

## 채택하지 않은 것과 미확인

- 별도 Skill/MCP/병렬 에이전트/설치 스크립트/프레임워크는 기존 범위와 설치 비용 때문에 도입하지 않았다.
- 외부 자료가 제안하는 권한 완화·전역 설정·바인딩·모델·반입·문항 순서는 공식 지침으로 채택하지 않았다.
- 현재 저장소는 요청대로 Private이다. 실제 응시 환경이 이 자료에 접근할 수 있는지와 반입 허용 여부는 미확인이다. 공개 전환하지 않는다.
- scrla의 [package.json](https://github.com/scrla/hynix-ai-hackathon-kit/blob/e29f1ace3718f6af6304c2291ddcfece6f0d6159/package.json)은 `verify`에서 scripts/preflight.mjs를 호출하지만 조회한 재귀 Git 트리에는 scripts/와 tests/가 없다. README에 있는 harness/·prompts/·.agents/도 조회 트리에 없다. ZIP 내부는 검토하지 않았고 외부 프로젝트를 설치·실행하지 않았으므로 런타임 실패를 관측했다고 주장하지 않는다.
- 위 저장소들의 시험 설명은 작성자의 공개 주장이다. 이번 작업에서 주최사의 실제 공지/PDF를 확보·검증하지 않았으므로 실제 규칙·정확한 문항 구성으로 확정하지 않는다.
- 문서 보강이 제한시간 성적을 높였는지는 미측정이다. 같은 작성자의 비블라인드 검증이며 실제 브라우저 수동 조작·독립 Reviewer·180분 맹검은 다음 연습 과제다.
