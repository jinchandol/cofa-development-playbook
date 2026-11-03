# 순차 역할 검토 결과

검토자: 동일 작성자·동일 대화의 Reviewer 역할. 별도 컨텍스트의 독립 Reviewer는 실행하지 않았다.
README/원본 기준으로 경계값, 행 순서 뒤집기, 비연속 순번, 저장 실패, HTTP 오류를 반례로 추가했다.
정답과 초기 구현을 알고 있어 맹검 효과를 주장할 수 없다.

## I01 · P1 · 의도적으로 삽입한 구현 결함

- 코드: domain.py `_validate_patch` 초기 `clean['active'] = bool(patch['active'])`.
- 재현: `python -m unittest discover -s reviewer -p "test_*.py" -v`.
- 입력: `{"active":"false"}`. 기대: 400/ServiceError, 기존 상태 유지. 실제: 수락하고 true로 변환.
- Developer 초기 테스트 7개는 통과했지만 문자열/숫자/null/list 타입 반례가 없었다.
- 초기 Reviewer: 7개 메서드 중 3개에서 총 5개 실패(동일 결함의 여러 표현). baseline.json은 실제 실행 로그다.
- 수정: `type(value) is bool` 엄격 검사 후 원본 boolean만 저장. Python bool/int의 하위형 관계 때문에 isinstance(value, int)를 사용하지 않는다.
- 수정 후 Reviewer 7/7, Developer 회귀 7/7 통과. HTTP에서도 문자열 active가 400임을 확인했다.

## 데이터/계약 검토

- R1 순번4의 SX와 S3는 원시상 충돌하지만 SX 참조를 먼저 제거해야 한다. 유효 마스터 참조 검사 후 순번 충돌 검사를 수행한다.
- R2는 일부 충돌행만 빼면 의미가 바뀌므로 전체 경유를 격리하고 목록 상태를 유지한다.
- R3 속성 충돌은 행 순서로 해결하지 않는다. CSV를 역순으로 바꿔도 결과가 동일함을 실행 검증했다.
- R1 S1 재방문, S3 공유/운휴 R4를 정상 사례로 보존한다.
- 행별 최종 disposition과 격리 원인/연쇄 차단을 구분해 숨은 행 손실을 방지한다.

## 환경/프로세스에서 발견한 문제

1. Windows 콘솔 cp949와 subprocess UTF-8 디코딩이 섞여 초기 증거 수집기가 UnicodeEncodeError로 중단됐다. 부모 stdout과 자식 PYTHONIOENCODING을 UTF-8로 고정 후 정상 수집했다.
2. 샌드박스는 임시 파일 원자 교체와 루프백 HTTP를 차단했다. 이를 제품 결함/통과로 오기하지 않고, 승인된 실행 권한으로 재실행해 구분했다. 차단 로그는 output/에만 두고 커밋하지 않는다.
3. raw 키 존재만으로는 S5/R3의 의미상 참조 오류를 놓친다. 정제 마스터에 대한 참조 재검사와 입력 수지 AC를 추가했다.
4. 정답을 아는 작성자의 검토를 독립 검증이라 표현하면 과대평가된다. 문서/프롬프트에 자기검토와 독립 검토를 구분하도록 명시했다.

현재 실행된 범위에 남은 P0/P1은 발견되지 않았다. 이는 모든 결함이 없다는 보장이 아니다.
브라우저 시각/클릭 검증, 별도 Reviewer, 미공개 새 데이터, 180분 제한 실험은 미실행이다.
