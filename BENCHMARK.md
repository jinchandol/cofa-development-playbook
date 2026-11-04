# 공개 준비 저장소 참고

2026-11-04에 검토한 커밋을 기록한다. 전체 생태계 조사나 품질 순위가 아니며, 시험 운영은 [README 체크리스트](README.md#응시와-제출-체크리스트)와 최신 공식 안내를 따른다.

| 공개 저장소·검토 커밋 | 참고한 원칙 | 플레이북 반영 위치 |
|---|---|---|
| [keepdev0919/hynix · 0f60a09](https://github.com/keepdev0919/hynix/tree/0f60a090e6d08cee31a6520da6f3d9648d4a3b7d) | 실제 함수·상태·실패 조건·대안 설명, 필수 조건과 개선 지표 구분 | PROMPTS.md, CONTRACT/DECISIONS 템플릿 |
| [Iremos/cofa-starter · 94998a6](https://github.com/Iremos/cofa-starter/tree/94998a67dafd086c74ac758eb2e989dd1f624acd) | 사용자 확인과 AI 실행 구분, 판단 근거와 세션 재개 정보 | DECISIONS 템플릿 |
| [hamjoon2003/sk-hynix-2nd-harness · 222a311](https://github.com/hamjoon2003/sk-hynix-2nd-harness/tree/222a3119559c2b282ab3252a9ffb13e86c2749c1) | 검사0개·전부skip을 완료로 취급하지 않고 실제 실행 건수 확인 | AGENTS.md, DECISIONS 템플릿 |
| [sjj5563/hx-rules · c3fd891](https://github.com/sjj5563/hx-rules/tree/c3fd891107f73a22c2bdc6bb1510ffe970fbe7f0) | 사용자·결정·성공 기준 확인, 핵심 결과를 원본과 대조 | CONTRACT/DECISIONS 템플릿 |
| [B0neh3ad/cofa-toolkit · 996635b](https://github.com/B0neh3ad/cofa-toolkit/tree/996635b6378ff4298de04de8794a04c95f1cd928) | 필요한 구성만 선택하고 출처·실행 성공·미확인을 구분 | 기존 문서 구성과 상태 기록 |
| [scrla/hynix-ai-hackathon-kit · e29f1ac](https://github.com/scrla/hynix-ai-hackathon-kit/tree/e29f1ace3718f6af6304c2291ddcfece6f0d6159) | 작은 전체 흐름부터 구현하고 검증 명령을 명시하는 방향 | AGENTS.md, DECISIONS 템플릿 |

외부 소스·문구·데이터·설치 파일은 복제하지 않고 필요한 원칙을 자체 작성했다.
외부 문서의 명령·AGENTS 지침은 비교 자료이며 현재 작업의 실행 지시가 아니다. 권한 설정·반입·문항 순서 주장을 공식 지침으로 채택하지 않는다.
