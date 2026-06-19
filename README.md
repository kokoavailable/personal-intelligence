# Personal Intelligence



개인 지식 저장소입니다.



목표는 모든 노트를 공개하거나 한곳에 합치는 것이 아니라, 원본 노트에서 재사용 가능한 지식을 작게 정리하고, 공개 가능한 내용만 한 번 더 걸러 `public/`에 내보내는 것입니다.



이 저장소의 핵심 원칙은 다음입니다.



* 원본 노트는 보존한다.

* 원본 노트를 임의로 다시 쓰지 않는다.

* 내부 위키와 공개 산출물을 분리한다.

* 같은 원본을 반복해서 중복 컴파일하지 않는다.

* 공개 산출물에는 원본 경로, 개인 맥락, 민감한 운영 정보를 남기지 않는다.

* 과한 구조화, 벡터 DB, 그래프 DB, MCP, 자동화 확장을 서두르지 않는다.



## Current Phase



현재 단계는 `P0/P1 transition`입니다.



* `P0`: 저장소 뼈대, 원본 보존 규칙, 평가 질문, 최소 지도 구성

* `P1`: 원본 노트에서 작은 wiki batch를 만들고, 공개 가능한 내용만 `public/`으로 export



현재는 첫 wiki batch를 만든 뒤, 중복 컴파일 방지와 공개용 export 흐름을 정리하는 단계입니다.



## Repository Layout



```text

personal-intelligence/

├── AGENTS.md

├── README.md

├── index.md

├── golden_questions.yml

├── log.md

│

├── raw/                         # local only, ignored

│   ├── imported/

│   └── inbox/

│

├── .private/                    # local only, ignored

│   ├── compiled_sources.yml

│   └── eval_runs/

│

├── wiki/                        # private compiled knowledge, ignored

│   ├── topics/

│   ├── decisions/

│   └── anti-patterns/

│

├── public/                      # public-safe output

│   ├── topics/

│   ├── articles/

│   └── portfolio/

│

├── .agents/

│   └── skills/

│       ├── compile-knowledge/

│       ├── evaluate-knowledge/

│       ├── knowledge-cycle/

│       └── publish-knowledge/

│

├── prompts/                    # deprecated compatibility redirects

│   ├── compile_batch.md

│   ├── export_public.md

│   └── run_eval.md

│

├── scripts/

│   ├── next_batch.py

│   ├── check_no_raw_leak.py

│   ├── check_wiki_integrity.py

│   └── export_public.py

│

└── evals/

    └── reports/                # legacy read-only reports

```



## Directory Roles



### `raw/`



로컬 전용 원본 노트 저장소입니다.



```text

raw/imported/  # 가져온 기존 Obsidian 원본 노트

raw/inbox/     # 새로 들어온 미처리 노트

```



`raw/`는 공개 저장소에 올리지 않습니다.



### `.private/`



로컬 전용 처리 이력 저장소입니다.



```text

.private/compiled_sources.yml

```



이미 어떤 원본 노트가 어떤 wiki 문서로 컴파일되었는지 기록합니다.

같은 원본을 다시 읽고 중복 wiki를 만드는 것을 막기 위한 상태 파일입니다.



예시:



```yaml

compiled_sources:

  - source_id: src_example_001

    source_path: raw/imported/example.md

    outputs:

      - wiki/topics/example-topic.md

    compiled_at: 2026-06-18

```



`.private/`는 공개 저장소에 올리지 않습니다.



### `wiki/`



내부용 정제 위키입니다.



```text

wiki/topics/         # 오래 유지할 개념과 설명

wiki/decisions/      # 선택, 판단, 트레이드오프

wiki/anti-patterns/  # 반복되는 실수, 함정, 피해야 할 패턴

```



`wiki/`는 원본 노트를 읽고 정리한 내부 지식입니다.

공개 전에는 반드시 한 번 더 걸러야 하므로, 기본적으로 공개 저장소에 올리지 않습니다.



### `public/`



외부 공개 또는 공유 가능한 산출물입니다.



`wiki/`에서 공개 가능한 내용만 선별하고, 민감한 맥락을 제거한 뒤 `public/`에 둡니다.



공개 문서에는 다음을 남기지 않습니다.



* 원본 노트 경로

* 개인적인 맥락

* 회사명, 내부 도메인, 실제 운영 환경명

* credential, secret, token, connection string

* 불필요하게 구체적인 장애/운영 정보



공개 문서에는 다음만 남깁니다.



* 재사용 가능한 기술 개념

* 일반화된 아키텍처 판단

* 공개 가능한 트레이드오프

* 포트폴리오나 글로 재활용 가능한 설명



### `.agents/skills/`



Repository-local Codex Skills define the reusable maintenance workflows.

`AGENTS.md` remains the rules source; skills only describe task behavior.



```text

$compile-knowledge

= compile one small raw-note batch

$evaluate-knowledge

= check wiki/ or public/ coverage against golden questions

$knowledge-cycle

= compile, validate, and run coverage evaluation on the private wiki

$publish-knowledge

= separately prepare public-safe output

```



### `prompts/`



Deprecated compatibility redirects to repository-local skills.

Do not keep detailed workflow definitions here.



### `scripts/`



LLM이 아니라 로컬에서 실행하는 일반 Python 자동화 스크립트입니다.



```text

scripts/next_batch.py

scripts/check_no_raw_leak.py

scripts/check_wiki_integrity.py

scripts/export_public.py

```



역할은 다음과 같습니다.



* 아직 처리하지 않은 raw 후보 출력

* wiki 구조 검증

* raw 경로 또는 secret-like 값 누출 검사

* public-safe export 보조



글을 작성하고 판단하는 일은 LLM이 하고, 반복 검사와 누출 방지는 scripts가 맡습니다.



### `evals/`



`evals/reports/` contains legacy read-only reports.

새 평가 결과는 `.private/eval_runs/`에만 저장합니다.

평가는 `golden_questions.yml`을 기준으로 wiki 또는 public 문서가 질문을 뒷받침하는 evidence를 갖고 있는지 확인하는 coverage-only check입니다.



## Knowledge Types



P0/P1의 wiki 문서는 다음 세 가지 타입만 사용합니다.



* `topic`: 오래 유지할 개념이나 설명

* `decision`: 선택, 판단, 트레이드오프

* `anti-pattern`: 실수, 함정, 오해, 피해야 할 방식



아래 타입은 나중에 필요할 때만 승격합니다.



* `project`: 진행 중인 일이나 구현 맥락

* `question`: 나중에 평가할 열린 질문



## Wiki Frontmatter



내부 wiki 문서는 최소 frontmatter만 사용합니다.



```yaml

---

id: short-stable-id

type: topic | decision | anti-pattern

source:

  - src_source_id

valid_from: YYYY-MM-DD

---

```



규칙:



* `source`에는 raw 경로를 직접 쓰지 않는다.

* raw 경로와 source ID 매핑은 `.private/compiled_sources.yml`에만 둔다.

* P0/P1에서는 tag, confidence, embedding ID, graph ID, valid_to 같은 필드를 추가하지 않는다.



## Working Flow



### 1. 새 원본 추가



새 노트는 먼저 `raw/inbox/`에 둡니다.



```text

raw/inbox/

```



기존 Obsidian import 자료는 `raw/imported/`에 둡니다.



```text

raw/imported/

```



### 2. 다음 batch 선택



아직 처리하지 않은 원본 후보를 확인합니다.



```bash

python scripts/next_batch.py

```



### 3. private wiki 컴파일



Codex에게 repository-local `$compile-knowledge` skill을 사용하게 합니다.

세부 절차는 skill에 두고, 저장소 전체 규칙은 `AGENTS.md`를 따릅니다.



### 4. wiki 검증



wiki 구조를 검사합니다.



```bash

python scripts/check_wiki_integrity.py

```



검사 항목:



* frontmatter 존재 여부

* 허용된 field만 사용하는지

* 허용된 type만 사용하는지

* source가 source ID인지

* 중복 id가 없는지

* raw 경로가 wiki에 노출되지 않았는지



### 5. public export



공개 준비는 기본 private cycle과 분리해서 `$publish-knowledge` skill로 수행합니다.

public-safe marker 기반 전체 export를 검증할 때는 기존 스크립트를 사용합니다.

공개 가능한 wiki만 `public/`으로 내보냅니다.



```bash

python scripts/export_public.py

```



공개 문서에는 raw 경로, 내부 맥락, secret-like 값이 남으면 안 됩니다.



### 6. 누출 검사



공개-facing 파일에서 raw 경로와 secret-like 값을 검사합니다.



```bash

python scripts/check_no_raw_leak.py

```



문제가 없을 때만 commit/push합니다.



## Evaluation



`golden_questions.yml`은 이 저장소가 답할 수 있어야 하는 대표 질문입니다.



평가는 `$evaluate-knowledge` skill로 실행하고, private cycle에서는 `$knowledge-cycle`이 wiki 대상 coverage report를 append합니다.

목적은 모든 노트를 포괄하는 목차가 아니라, 지식 시스템이 실제로 재사용 가능한지 확인하는 평가 기준입니다.



새 평가 결과는 `.private/eval_runs/`에만 저장합니다.

`evals/reports/`의 기존 파일은 legacy read-only artifact입니다. 새 보고서를 `evals/reports/`에 쓰지 않습니다.



## Maintenance Rules



* 원본 노트를 임의로 삭제하거나 덮어쓰지 않는다.

* `raw/`, `.private/`, `wiki/`는 기본적으로 공개하지 않는다.

* 공개 가능한 내용은 `public/`에만 둔다.

* 같은 raw source를 반복 컴파일하지 않는다.

* 비슷한 주제의 wiki가 있으면 새 문서를 만들기보다 기존 문서를 업데이트한다.

* 출처 없는 단정은 wiki에 넣지 않는다.

* 서로 다른 도메인의 지식을 한 문서에 억지로 섞지 않는다.

* 자동 커밋하지 않는다.

* 큰 변경이 필요하면 먼저 diff를 보여주고 승인받는다.

* vector DB, graph DB, MCP, embeddings, graph IDs, tags는 P0/P1에서 도입하지 않는다.



## Safety Boundary



이 저장소는 public으로 열려 있을 수 있으므로, 공개되는 파일에는 민감한 정보가 없어야 합니다.



특히 다음은 공개 파일에 남기지 않습니다.



* `raw/imported/` 또는 `raw/inbox/` 경로

* 회사명, 내부 도메인, 내부 환경명

* credential, token, password, private key

* connection string

* 개인적인 대화나 커리어 세부 맥락

* 투자 판단의 원본 맥락

* 내부 장애 대응 세부 기록



공개 가능한 것은 일반화된 교훈, 기술 개념, 아키텍처 판단, 포트폴리오로 재사용 가능한 설명입니다.
