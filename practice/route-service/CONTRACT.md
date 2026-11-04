# 리허설 CONTRACT

근거: 과제 README R-01~07 / data/*.csv / rehearsal/INTERVIEW.md / evaluator/RULES.md B-01~07.
상태: 요구=README 명시, 업무=합성 현업 확정, 기술=개발 판단. 실제 담당자의 답변이 아니다.

## 업무 목표·필수/개선/범위 밖

- 사용자/순간/결정: 합성 운영 담당자가 노선 경유를 조회하고 이름·운행 여부를 관리한다 (과제 README).
- 현재 문제: 중복·참조 오류가 섞여 단순 조인으로는 정확한 경유를 표시할 수 없다. 실제 소요 시간·비용 기준값은 미측정이다.
- 최소 흐름: 노선 검색 → 경유 상세 → 이름/운행 변경 → 저장 후 재조회.
- 필수: R-01~07, 원본 불변, 업무 규칙에 맞는 경유·격리·저장, 실행 가능한 웹 서비스.
- 개선 목표: 작업 시간 단축·화면 사용성은 정량 목표를 합의하지 않았으므로 달성했다고 주장하지 않는다. 문서 가독성 개선은 개발 판단이다.
- 범위 밖: 지도·노선 생성/삭제·로그인·배포·다중 프로세스 협업 (과제 README/개발 범위).
- 측정식/기준값: 원시 CSV 5/6/16행, raw inner join 18행. Golden R1 경유 4와 S3 역조회 2노선, 행 수지 일치는 필수 정확성 기준이며 업무 효율 지표와 구분한다.
- 불가능한 결과 처리: 상충 엔터티 R3와 순서 충돌 R2를 임의 선택으로 정상화하지 않고 B-03/04의 격리·blocked 정책을 적용한다.

## Requirement Contract / AC

| ID/AC (모두 필수) | README 근거 | 데이터/관계 근거 | 인터뷰 근거 | 확정 상태 | 완료조건 | 연결 테스트 |
|---|---|---|---|---|---|---|
| R-01 / AC-01 | README R-01 프로파일/원본 불변 | CSV 5/6/16행, R3/S3 키 충돌/중복, raw 조인18행 | Q2~4→B-03~05 처리 정책 | 명시+합성 현업 확정 | 행 수·키·결측·관계/수지 보고, 원본 해시 불변 | test_profile_and_source_immutable |
| R-02 / AC-02 | README R-02 목록/검색/필터 | routes.csv의 R3 두 행은 이름 상충, R4는 운휴 | Q2→B-03, Q6→B-06 | 명시+합성 현업 확정 | R1,R2,R4만 목록. trim+casefold 이름 부분검색/운행 필터, count/blocked 표시 | test_list_search_filter |
| R-03 / AC-03 | README R-03 경유 순서·반복 정확성 | R1의 순번1/3은 S1 재등장, R2 순번2는 서로 다른 두 정류장 | Q1→B-01, Q3→B-04, Q4→B-05 | 명시+합성 현업 확정 | R1=S1,S2,S1,S3 (순번1,2,3,4); R2 blocked·경유0 | test_golden_route_and_blocked |
| R-04 / AC-04 | README R-04 역조회, 운휴/오류 정책 확인 | S3를 R1/R2/R4가 공유하며 R2는 순번 충돌, R4는 운휴 | Q5→B-02, Q3→B-04 | 명시+합성 현업 확정 | S3→R1,R4, S1→R1 한 건, 없는 정류장404 | test_reverse_membership |
| R-05 / AC-05 | README R-05 이름/운행 편집·영속성·원본 불변 | name/active 컬럼 존재. 입력 길이/JSON 타입/저장 정책은 데이터만으로 미결정 | Q6→B-06/07 | 명시+합성 현업 확정, JSON 방식은 개발 판단 | 이름/active만 수정·재시작 유지, trim 1~80자·JSON bool 외400, 원본 불변 | test_edit_persists / test_boolean_string_rejected / test_patch_boundaries |
| R-06 / AC-06 | README R-06 처리 근거/행 번호/수지 | 5/6/16행 모두의 최종 처분 필요, 중복/참조/순번 오류와 연쇄 차단 존재 | Q2~4→B-03~05 | 명시+합성 현업 확정 | 각 원본 행은 accepted/deduplicated/quarantined 중 하나, 코드/행 번호·합계 일치 | test_quality_balances / evaluator/score.py |
| R-07 / AC-07 | README R-07 실행·검증·지정 문서 | 해당없음: 실행/제출 요구이며 데이터에서 새 정책을 추론하지 않음 | 해당없음: README에 명시 | 명시+개발 판단 | HTTP 페이지/API 실제 동작, 실행 명령·문서·테스트·한계 기록 | test_http_end_to_end / test_http_errors / evidence.json |

위 AC는 모두 필수다. 빈 결과의 위반 0건으로 만족시킬 수 없다: 목록 3개, R1 유효 경유 4개, S3 역조회 2개를 확인한다.
검증 대상이 0개/전부 skip이면 INCOMPLETE다. 검증기는 각 테스트 군의 실제 실행/통과/skip 수를 기록한다.
연결 테스트: rehearsal/test_verification.py 6개 회귀 사례. 웹 화면 직접 확인은 DECISIONS의 NOT_RUN으로 별도 관리한다.
AC-07-P(제공 가이드 반영): 기본127.0.0.1을 유지하고 `--host 0.0.0.0`을 명시하면 해당 주소로 바인딩한다.
연결 테스트: test_platform_preview_binding, cli_smoke.py의 두 모드 실제 실행. 실제 플랫폼 Browser 통과는 별도 수동 확인 대상이다.

## Data Contract

| 파일 | 스키마/한 행/키 | 입력 → 수용+중복제거+격리 | 관계·정책·근거 |
|---|---|---|---|
| routes | route_id/name 문자열, active true/false 텍스트 / 노선 레코드 / route_id | 5→3+0+2 | R3 충돌 키 전체 격리 B-03 |
| stops | stop_id/name 문자열 / 정류장 레코드 / stop_id | 6→4+1+1 | S3 동일행 접기, S5 필수이름 결측 격리 B-03,05 |
| route_stops | route_id/stop_id 문자열, sequence 양의 정수 / 경유 사건 / 정제 후(route_id,sequence) | 16→5+1+10 | route/stop 참조 재검사 후 충돌 판단. 노선/정류장 1:N, 노선↔정류장 N:M |

처리 순서: 마스터 검증/그룹 충돌 → 경유 필수값/양의 정수/정제 마스터 참조 → 동일 경유 접기 → 실제 순번 충돌 노선 전체 경유 격리.
한 원본 행의 최종 disposition은 하나다. 충돌 원인 행과 연쇄 격리 행을 구분한다. 순번을 다시 매기지 않는다.
해시는 rehearsal/evidence.json의 raw_profile.sha256과 post_test_sha256을 비교한다.
단순 raw inner join의 18행을 정상 결과로 채택하지 않는다. 정제된 5경유는 모두 정확히 한 노선/정류장으로 연결된다.

## Business Contract

Q1~Q6의 관찰·선택지·우선순위는 rehearsal/ANALYSIS.md, 답변/구현 영향은 INTERVIEW.md에 고정했다.
B-01 재방문 보존 / B-02 공유+운휴 역조회 / B-03 완전동일 접기·충돌 격리 / B-04 전체 경유 차단 / B-05 행 격리 / B-06 입력 규칙 / B-07 저장 정책 모두 합성 확정.
Golden Cases는 AC-03/04. 미확정 정책으로 임의 구현한 항목은 없다.

## 요구사항 리뷰 상태

이번 문서 감사에서 README R-01~07·CSV·합성 인터뷰와 위 요구/AC를 소급 대조했다. 과거 개발 전에 이 리뷰를 수행한 이력으로 소급해 주장하지 않는다.
R-03은 반복 경유를 제거하면, R-04는 운휴를 빼면 Golden Case와 달라지므로 해당 업무 답변을 요구에 연결했다. R-07에 데이터/인터뷰 근거를 억지로 만들지 않았다.
추가된 AC-07-P는 사용자 제공 환경 가이드에서 나온 기술적 실행 보완이며 원본 README에서 새 업무 기능을 유추한 것이 아니다.
검토 방식: 동일 세션 자기검토. 범위: 기존 R-01~07의 근거/완료 조건, 새 지침의 요구사항 리뷰 절차. 개발자 본인의 이해 확인은 아직 미실행이다.

## 기술 결정·범위

Python 3.10+ 표준 라이브러리 서버+정적 JS. 단일 프로세스, 기본 루프백/명시적 미리보기 host 옵션. 편집 상태는 원본과 분리된 JSON으로 원자 교체.
최소 흐름: CSV→검증→목록→상세→편집 저장→재조회. 데이터 편집/삭제·인증·배포·동시 다중 프로세스·대용량은 범위 밖.
UI 렌더링의 시각 검증과 HTTP/API 실행 검증을 구분한다.
