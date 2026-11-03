# 리허설 CONTROL

작성 기준일: 2026-11-04 (Asia/Seoul). 실제 명령/시각/출력은 rehearsal/evidence.json 참조.
README 요구와 합성 업무 답변을 계약에 반영한 뒤 구현·순차 검토·수정·재검증했다.

## 요구사항별 상태

| 요구/AC | 구현 | Developer 실제 검증 | Reviewer 역할 실제 검증 | 상태/한계 |
|---|---|---|---|---|
| R-01/AC-01 | profile_data.py, domain.py | 행 수·조인18·해시 불변 | 행 순서 역전 | 완료, 제공 CSV 한정 |
| R-02/AC-02 | domain.list_routes, web/app.js | 목록3·검색·필터 | 잘못된 필터400 | HTTP 완료, UI 클릭 미검증 |
| R-03/AC-03 | domain.detail/_edges | R1 반복·R2 차단 | 비연속 순번 보존·행 역전 | 완료 |
| R-04/AC-04 | domain.reverse | S3=R1,R4 / S1=R1 | 역순 데이터 동일 | 완료 |
| R-05/AC-05 | domain.update/_validate_patch | 파일 저장→서비스 재생성 유지 | I01 타입 반례·저장 실패 불변 | 완료, 다중 프로세스 미지원 |
| R-06/AC-06 | domain.quality, UI | 파일별 수지 | evaluator/score 12/12 | 완료, 맹검 성능 아님 |
| R-07/AC-07 | app.py, 문서/테스트 | 실제 HTTP 정적파일/API | 오류 응답·CLI 별도 프로세스 | 완료, 시각/클릭 검증 미실행 |

Reviewer는 별도 컨텍스트가 아닌 같은 작성자의 역할 전환이다. 독립 검증 완료로 주장하지 않는다.

## 주요 결정과 버린 대안

| 결정 | 선택/버린 대안 | 이유·근거 |
|---|---|---|
| 스택 | Python 표준 HTTP+JSON+정적 JS / 외부 웹프레임워크·빌드 체인 | 설치 없이 재현, 작은 과제에 충분. 공개 서비스용 서버는 범위 밖 |
| 데이터 품질 | 원본 불변+행별 격리/중복제거 ledger / 조용한 drop·last-write-wins | 추적과 수지, B-03~05 |
| 경유 키 | route+sequence / route+stop | 순환 노선 재방문 보존 B-01 |
| 충돌 처리 순서 | 정제 마스터 참조 후 순번 충돌 / raw 순번만 검사 | R1의 무효 SX를 실제 충돌로 오인하지 않음 |
| 저장 | 파생 JSON+동일 디렉터리 임시파일 fsync/os.replace, 단일 프로세스 RLock / 원본 CSV 수정·DB | 원본 보존, 작은 상태 영속성. 프로세스 간 동시 편집은 미지원 |
| UI 출력 | textContent / 데이터의 innerHTML 삽입 | 이름을 HTML로 해석하지 않음 |

현업 답변으로 변경된 사항은 INTERVIEW.md Q1~Q6 참조. 실제 외부 인터뷰가 아닌 시나리오 답변이다.

## 데이터 수지와 검출

| 파일 | 원본 | 수용 | 중복제거 | 격리 |
|---|---|---|---|---|
| routes.csv | 5 | 3 | 0 | 2 |
| stops.csv | 6 | 4 | 1 | 1 |
| route_stops.csv | 16 | 5 | 1 | 10 |

원본 해시 3개는 baseline→final 모두 동일. raw inner join은 18행으로 증폭되어 채택하지 않았다.
정제 경유 5건은 각각 유효 마스터 한 건에 대응한다.
사전 고정 데이터 결함 D01~D12 **12/12 (100%)**, 미검출 없음.
정상 사례 2/2 보존. 의도적 구현 결함 I01 **1/1 발견 후 수정·재검증**.
이 지표는 같은 작성자의 합성 정답 대조 결과이며 새 문제/인터뷰/실제 시험의 성능 추정치가 아니다.

## 실제 실행 증거

작업 디렉터리: practice/route-service.

| 명령 | 실제 결과 | 증거 |
|---|---|---|
| python profile_data.py | 종료0, 5/6/16행·조인18·결측/키/참조/해시 | evidence.json raw_profile |
| python rehearsal/verify.py --stage baseline | 종료1, Dev7 통과, Review5 assertion 실패(합성 I01) | baseline.json |
| python rehearsal/verify.py --stage final | 종료0, Dev7+Review7 통과, JS 문법/CLI 확인 | evidence.json |
| python evaluator/score.py | 종료0, D12/12·정상2/2·I01 발견/재검증·원본 불변 | score.json |

확인 대상: 이름/상태 편집·파생 저장 재로딩, 목록/상세/역조회/품질 API, HTML/JS/CSS 200, 400/404/405/413, malformed JSON, 상태 파일 손상, 저장 실패 시 메모리 불변.
실제 CLI는 `python app.py --port 0`으로 별도 프로세스를 띄워 HTTP 확인 후 종료한다. 사용자용 고정 포트 실행법은 README 참조.
node가 있으면 `node --check web/app.js`를 실행하며 Node는 서버 실행 필수 조건이 아니다.
테스트를 재현하려면 `python rehearsal/verify.py --stage final` → `python evaluator/score.py` 순서로 실행한다.

## 결함·한계

자세한 재현/기대/실제/수정은 rehearsal/REVIEW.md. I01은 자연 발견 결함이 아니라 사전에 심은 결함이다.
자연 발생 과정 문제는 Windows 증거 수집 인코딩 오류였고 수정 후 재실행했다.
남은 미검증: 브라우저 화면·클릭·모바일·키보드 사용성, 별도 Reviewer, 진짜 담당자 인터뷰, 180분 타이머, 새 도메인, Excel·대용량 데이터.
서버는 단일 프로세스 로컬 전용이며 인증/배포/다중 프로세스 충돌 해결이 없다. CSV 스키마가 다르면 시작을 실패시킨다.
저장 파일 오류를 조용히 초기화하지 않는다. 사용자가 상태를 검토/백업 후 복구해야 한다.

## WHAT / WHY / HOW / VERIFY

- WHAT: 검색/필터 목록, 경유 상세, 역조회, 이름/운행 편집, 데이터 품질 보고를 구현했다.
- WHY: 설치 없이 실행하고, 오류를 숨기지 않으면서 유효 업무 흐름을 먼저 완성하기 위해서다.
- HOW: CSV→마스터 정제→경유 참조 검사→중복 접기→순번 충돌 차단→조회/파생 저장→HTTP/화면.
- VERIFY: 자동 14개 테스트와 CLI/JS 검사, 정답12개 대조, 정상2개 보존, 원본 해시 불변. 시각 검증은 수행하지 않았다.

## AI 없이 6문항: 각 5분

1. **무엇을 완성했나?** R-01~07과 AC-01~07을 기능/테스트에 연결. 목록3·R1경유4·편집 영속성을 예로 설명한다.
2. **데이터를 어떻게 이해했나?** 5/6/16행, 경유 사건 단위, N:M, 원시 조인18의 증폭과 미매칭3행, 정제 수지 설명.
3. **현업 질문이 무엇을 바꿨나?** S1 재방문 유지, R3 전체 격리, R2 전체 경유 차단, S3 운휴 포함이라는 실제 코드 영향을 설명.
4. **왜 이 설계인가?** 표준 라이브러리/파생 JSON과 버린 프레임워크/원본 수정/DB의 비용을 비교. 단일 프로세스 한계도 설명.
5. **실제로 어떤 결함을 잡았나?** bool("false")=true인 합성 I01, Dev 초기 누락, Review 5실패, 엄격 bool 수정 후 14통과를 설명.
6. **어디까지 믿을 수 있나?** 비블라인드·자기검토·시간제한 없음·UI 미검증을 구분. 다음은 새 과제 맹검180분+실제 브라우저 확인을 우선.
