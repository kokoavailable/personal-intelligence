# Personal Intelligence

개인 지식 저장소입니다.

목표는 모든 노트를 한곳에 모으는 것이 아니라, 나중에 다시 쓸 수 있는 지식을 원본 경로와 함께 보존하는 것입니다. 기존 Obsidian 노트는 원본 자료로 남기고, 반복해서 참조할 만한 내용만 `wiki/`에 작게 정리합니다.

## Current Phase

현재 단계는 `P0`입니다.

P0의 원칙:

- 기존 노트를 보존한다.
- 원본 노트를 임의로 다시 쓰지 않는다.
- 과한 구조화, 자동화, 데이터베이스 도입을 피한다.
- 작은 변경 단위로 지식을 정리한다.
- `wiki/`의 비자명한 주장은 원본 노트 경로를 남긴다.

## Repository Layout

- `AGENTS.md`: 저장소 유지보수 규칙과 작업 원칙
- `index.md`: 전체 지식 시스템의 가벼운 지도
- `golden_questions.yml`: 이 저장소가 답할 수 있어야 하는 평가 질문
- `log.md`: 중요한 유지보수 작업 기록
- `raw/imported/`: 가져온 Obsidian 원본 노트
- `raw/inbox/`: 새로 들어온 미처리 노트
- `wiki/topics/`: 오래 유지할 개념과 설명
- `wiki/decisions/`: 선택, 판단, 트레이드오프
- `wiki/anti-patterns/`: 반복되는 실수, 함정, 피해야 할 패턴
- `evals/`: 수동 평가 기록
- `public/`: 공개 또는 공유 가능한 초안

## Knowledge Types

노트를 처리할 때는 재사용 가능한 지식을 다음 유형 중 하나로 분류합니다.

- `topic`: 오래 유지할 개념이나 설명
- `decision`: 선택, 판단, 트레이드오프
- `anti-pattern`: 실수, 함정, 오해, 피해야 할 방식
- `project`: 진행 중인 일이나 구현 맥락
- `question`: 나중에 평가할 열린 질문

P0에서 `wiki/`에 승격하는 문서는 `topic`, `decision`, `anti-pattern`만 사용합니다. `project`와 `question`은 명시적으로 승격하지 않는 한 원본 노트, `index.md`, `log.md`에 둡니다.

## Working Flow

새 노트는 먼저 `raw/inbox/`에 둡니다.

노트를 지식으로 정리할 때:

1. 관련 원본 노트를 먼저 읽는다.
2. 이미 비슷한 `wiki/` 문서가 있는지 검색한다.
3. 재사용 가능한 내용만 추린다.
4. 최대한 작은 단위의 `wiki/` 변경을 제안한다.
5. 원본 경로를 frontmatter나 본문에 남긴다.
6. 충돌하는 정보가 있으면 조용히 합치지 않고 충돌을 표시한다.
7. 필요하면 `index.md`, `golden_questions.yml`, `log.md`를 작게 갱신한다.

## P0 Wiki Frontmatter

새 `wiki/` 문서를 만들 때는 최소 frontmatter만 사용합니다.

```yaml
---
id: short-stable-id
type: topic | decision | anti-pattern
source:
  - path/to/source.md
valid_from: YYYY-MM-DD
---
```

태그, confidence, `valid_to`, embedding ID, graph ID 같은 필드는 P0에서 요구하지 않습니다.

## Maintenance Rules

- 모든 노트를 하나의 파일로 합치지 않는다.
- 원본 노트를 임의로 삭제하거나 덮어쓰지 않는다.
- 출처 없는 단정은 `wiki/`에 넣지 않는다.
- 서로 다른 도메인의 지식을 한 문서에 억지로 섞지 않는다.
- 자동 커밋하지 않는다.
- 큰 변경이 필요하면 먼저 변경안을 보여주고 승인받는다.
