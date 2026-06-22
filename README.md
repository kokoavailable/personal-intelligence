# Personal Intelligence

개인 지식 저장소입니다.

이 저장소의 목표는 모든 노트를 공개하거나 하나의 거대한 문서로 합치는 것이 아닙니다.
원본 노트는 로컬에 보존하고, 다시 쓸 만한 지식만 작은 단위로 정리한 뒤, 공개 가능한 내용만 `public/`에 따로 내보내는 것이 목표입니다.

핵심 흐름은 다음과 같습니다.

```text
raw source notes
→ private wiki
→ public-safe output
```

## Principles

* 원본 노트는 보존한다.
* 원본 노트를 임의로 다시 쓰지 않는다.
* 내부 위키와 공개 산출물을 분리한다.
* 같은 원본을 반복해서 중복 컴파일하지 않는다.
* 공개 산출물에는 원본 경로, 개인 맥락, 민감한 운영 정보를 남기지 않는다.
* LLM은 글을 읽고 정리하는 데 사용하고, 반복 검사는 스크립트로 처리한다.
* P0/P1 단계에서는 vector DB, graph DB, MCP, embeddings, graph IDs, tags를 도입하지 않는다.

## Current Phase

현재 단계는 `P0`입니다.

`P0`는 다음을 우선합니다.

* 원본 노트 보존
* 작은 단위의 private wiki 정리
* source traceability 유지
* deterministic validation
* manually curated evaluation

첫 wiki batch와 public export 보조 스크립트는 있지만, 운영 기준은 아직 P0입니다.
P0에서는 vector DB, graph DB, MCP, background agent, 대규모 자동화를 도입하지 않습니다.

## Repository Layout

```text
personal-intelligence/
├── AGENTS.md
├── README.md
├── .gitignore
├── golden_questions.yml
│
├── raw/                         # local only
│   ├── imported/
│   └── inbox/
│
├── .private/                    # local only
│   ├── compiled_sources.yml
│   ├── knowledge_cycle_log.md
│   └── eval_runs/
│
├── wiki/                        # local/private compiled knowledge
│   ├── index.md
│   ├── topics/
│   ├── decisions/
│   └── anti-patterns/
│
├── public/                      # public-safe output
│   └── drafts/
│
├── .agents/
│   └── skills/
│       ├── compile-knowledge/
│       ├── evaluate-knowledge/
│       ├── knowledge-cycle/
│       └── publish-knowledge/
│
├── scripts/
│   ├── init_workspace.py
│   ├── next_batch.py
│   ├── check_no_raw_leak.py
│   ├── check_wiki_integrity.py
│   ├── update_index.py
│   ├── append_log.py
│   └── export_public.py
│
└── evals/
    ├── runs/
    └── reports/
```

## Public / Private Boundary

이 저장소는 public으로 열려 있을 수 있으므로, 공개되는 파일과 로컬 전용 파일을 명확히 분리합니다.

### Local only

다음은 로컬 전용입니다.

```text
raw/
.private/
wiki/
```

역할:

* `raw/`: 원본 노트
* `.private/`: 처리 이력, source mapping, operational history
* `wiki/`: 내부용 정제 위키와 navigation index

이 세 디렉터리는 기본적으로 공개하지 않습니다.

### Public-facing

다음은 공개 가능성을 전제로 관리합니다.

```text
public/
AGENTS.md
README.md
.gitignore
golden_questions.yml
.agents/skills/
scripts/
evals/
```

단, `evals/`도 평가 내용에 private evidence가 들어갈 수 있으므로 공개 전 확인이 필요합니다.

## Directory Roles

### `raw/`

로컬 전용 원본 노트 저장소입니다.

```text
raw/imported/  # 가져온 기존 Obsidian 원본 노트
raw/inbox/     # 새로 들어온 미처리 노트
```

원칙:

* 원본 노트는 임의로 수정하지 않는다.
* 기존 import 자료는 보존한다.
* 새 노트는 먼저 inbox에 둔다.
* raw 파일은 공개 저장소에 올리지 않는다.

### `.private/`

로컬 전용 처리 이력 저장소입니다.

```text
.private/compiled_sources.yml
.private/knowledge_cycle_log.md
.private/eval_runs/
```

`.private/compiled_sources.yml`은 이미 어떤 원본 노트가 어떤 wiki 문서로 컴파일되었는지 기록합니다.
같은 원본을 다시 읽고 중복 wiki를 만드는 것을 막기 위한 상태 파일입니다.

예시:

```yaml
compiled_sources:
  - source_id: src_vmss_rolling_upgrade_001
    source_path: raw/imported/example.md
    outputs:
      - wiki/topics/example-topic.md
      - wiki/decisions/example-decision.md
    compiled_at: 2026-06-18
```

원칙:

* `.private/`는 공개하지 않는다.
* source ID와 실제 raw path의 mapping은 이곳에 둔다.
* 중복 컴파일 방지는 프롬프트가 아니라 이 상태 파일을 기준으로 한다.
* `.private/knowledge_cycle_log.md`는 성공한 knowledge cycle만 append-only로 기록한다.
* `.private/eval_runs/`에는 local-only evaluation report를 저장한다.
* `compile-fidelity` report와 `golden-answerability` report는 knowledge-cycle log에서 참조할 수 있지만 공개 산출물은 아니다.
* `.private/eval_runs/` report는 기존 `evals/reports/`보다 우선하는 현재 평가 산출물 위치다.

### `wiki/`

내부용 정제 위키입니다.

```text
wiki/index.md       # navigation-only generated wiki index
wiki/topics/         # 오래 유지할 개념과 설명
wiki/decisions/      # 선택, 판단, 트레이드오프
wiki/anti-patterns/  # 반복되는 실수, 함정, 피해야 할 패턴
```

`wiki/`는 원본 노트를 읽고 정리한 내부 지식입니다.
공개 전에는 반드시 `public/`으로 따로 export해야 합니다.

P0/P1에서 사용하는 wiki type은 세 가지입니다.

* `topic`: 오래 유지할 개념이나 설명
* `decision`: 선택, 판단, 트레이드오프
* `anti-pattern`: 실수, 함정, 오해, 피해야 할 방식

### `public/`

외부 공개 또는 공유 가능한 산출물입니다.

`public/`에는 `wiki/`에서 공개 가능한 내용만 선별하고, 민감한 맥락을 제거한 문서만 둡니다.

공개 문서에는 다음을 남기지 않습니다.

* 원본 노트 경로
* 개인적인 맥락
* 회사명, 내부 도메인, 실제 운영 환경명
* credential, secret, token, connection string
* 불필요하게 구체적인 장애/운영 정보
* private source ID
* 내부 판단 과정 중 공개할 필요가 없는 내용

공개 문서에는 다음을 남깁니다.

* 재사용 가능한 기술 개념
* 일반화된 아키텍처 판단
* 공개 가능한 트레이드오프
* 포트폴리오나 글로 재활용 가능한 설명

### `.agents/skills/`

Codex 작업 절차를 나눈 skill 문서입니다.

```text
.agents/skills/compile-knowledge/    # raw -> private wiki proposal/apply
.agents/skills/evaluate-knowledge/   # compile-fidelity, golden-answerability
.agents/skills/knowledge-cycle/      # private maintenance cycle orchestration
.agents/skills/publish-knowledge/    # public export/publishing boundary
```

역할 분리:

* `AGENTS.md`: 저장소 정책의 source of truth
* `compile-knowledge`: source를 읽고 wiki/registry 변경을 제안하거나 승인 후 적용
* `evaluate-knowledge`: 평가 suite와 evaluation report persistence 담당
* `knowledge-cycle`: workspace check, compile, validation, wiki index, evaluation, log를 순서대로 orchestration
* `publish-knowledge`: private cycle과 분리된 public-safe export/publish 절차

Skills는 `AGENTS.md`를 먼저 읽고 따라야 하며, repository-wide policy를 재정의하지 않습니다.

### `scripts/`

로컬에서 실행하는 Python 자동화 스크립트입니다.
LLM이 아니라 일반 프로그램입니다.

```text
scripts/init_workspace.py
scripts/next_batch.py
scripts/check_no_raw_leak.py
scripts/check_wiki_integrity.py
scripts/update_index.py
scripts/append_log.py
scripts/export_public.py
```

역할:

* local-only workspace check 및 없는 초기 파일 생성
* 아직 처리하지 않은 raw 후보 출력
* wiki 구조 검증
* `wiki/index.md`의 generated wiki marker block 생성 및 검사
* completed knowledge-cycle log entry preview 및 append-only 기록
* public 출력물의 raw 경로 또는 secret-like 값 누출 검사
* public-safe export 보조

글을 읽고 판단하고 정리하는 일은 LLM이 합니다.
반복 검사와 누출 방지는 scripts가 맡습니다.

### `evals/`

기존 평가 report 위치입니다. 새 local-only evaluation report는 `.private/eval_runs/`에 저장합니다.

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

* field name은 `source`이고 값은 list다. `source_id`로 바꾸지 않는다.
* `wiki/` frontmatter의 `source` 값은 stable `src_...` source ID만 사용한다.
* raw source path는 `.private/compiled_sources.yml`의 `source_path`에만 둔다.
* `.private/compiled_sources.yml`이 `source_id` -> `source_path` -> `outputs` mapping을 소유한다.
* raw file이 move 또는 rename되어도 source ID는 안정적으로 유지한다.
* 공개용 문서인 `public/`에는 raw source path나 private source ID를 남기지 않는다.
* P0/P1에서는 tag, confidence, embedding ID, graph ID, valid_to 같은 필드를 추가하지 않는다.

## Usage

### 1. Initialize Local Workspace

로컬 전용 디렉터리와 초기 파일은 명시적으로 확인하거나 생성합니다.

```bash
python3 -B scripts/init_workspace.py --check
python3 -B scripts/init_workspace.py --write
```

`--check`는 파일을 수정하지 않습니다. `--write`는 없는 디렉터리와 초기 파일만 만들며 기존 파일을 덮어쓰지 않습니다.

### 2. Add Source Notes

기존 Obsidian import 자료는 `raw/imported/`에 둡니다.
새로 들어온 미처리 노트는 `raw/inbox/`에 둡니다.

원본 노트는 수정하지 않습니다.

### 3. Find Candidate Sources

아직 처리하지 않은 raw 후보를 확인합니다.

```bash
python3 -B scripts/next_batch.py
```

이 스크립트는 `.private/compiled_sources.yml`에 이미 기록된 source를 제외하고 후보를 출력합니다.

### 4. Recommended Path: `$knowledge-cycle`

일반적인 private maintenance는 `$knowledge-cycle`을 사용합니다.

```text
$knowledge-cycle

Compile these sources:
- raw/imported/example-1.md
- raw/imported/example-2.md
```

정상 sequence:

1. compile proposal
2. source-exhaustion check
3. read-only compile-fidelity preview
4. combined proposal and fidelity result
5. exact `approve` boundary
6. approved wiki and registry changes only
7. deterministic validation
8. deterministic index update and index check
9. final compile-fidelity report against applied files
10. golden-answerability report against `wiki/`
11. append-only cycle log through `scripts/append_log.py`
12. final summary

중요한 boundary:

* `approve`라는 정확한 응답 전에는 파일을 쓰지 않는다.
* compile-fidelity preview가 `FAIL`이면 approval을 요청하지 않고 proposal을 고친다.
* validation 또는 index update/check가 실패하면 evaluation report와 cycle log를 남기지 않는다.
* publishing은 `$knowledge-cycle`에 포함하지 않는다.

### 5. Manual Compile Only: `$compile-knowledge`

wiki proposal만 만들거나 작은 compile 작업만 따로 할 때 사용합니다.

```text
$compile-knowledge

Compile this batch:
- raw/imported/example.md

Show the proposed diff before writing.
```

이 skill은 다음만 담당합니다.

* source 읽기
* 기존 wiki 검색
* 최대 3개 wiki/registry 변경 제안
* source-exhaustion 판단
* exact `approve` 후 승인된 wiki와 `.private/compiled_sources.yml` 변경만 적용

평가 suite와 evaluation report 저장은 `$evaluate-knowledge`가 담당합니다.

### 6. Evaluation Only: `$evaluate-knowledge`

평가는 정확히 두 suite만 지원합니다.

```text
$evaluate-knowledge suite=compile-fidelity
$evaluate-knowledge suite=golden-answerability target=wiki
```

`compile-fidelity`는 source note, proposed/applied wiki, registry entry 사이의 충실도를 봅니다.

`golden-answerability`는 enabled golden question마다 selected corpus만 사용해 candidate answer를 만들고 다음을 기록합니다.

* question
* candidate answer
* evidence files
* supportedness
* completeness
* directness
* conflict handling
* missing knowledge
* status

Candidate answer는 평가 산출물이며 canonical wiki 지식이 아닙니다.

Report 위치:

```text
.private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md
.private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-wiki.md
```

### 7. Deterministic Checks

수동으로 검증할 때는 다음 순서를 사용합니다.

```bash
python3 -B scripts/check_wiki_integrity.py
python3 -B scripts/check_no_raw_leak.py
git diff --check
python3 -B scripts/update_index.py --write
python3 -B scripts/update_index.py --check
```

`scripts/update_index.py`는 `wiki/index.md`의 marker 사이 content만 갱신합니다.

```md
<!-- BEGIN GENERATED WIKI INDEX -->
...
<!-- END GENERATED WIKI INDEX -->
```

규칙:

* begin marker와 end marker가 정확히 하나씩 없으면 실패한다.
* marker가 중복되거나 순서가 잘못되면 실패한다.
* marker 밖의 byte는 보존한다.
* `wiki/topics/`, `wiki/decisions/`, `wiki/anti-patterns/` 아래 malformed wiki note가 있으면 nonzero로 실패한다.

### 8. Append Completed Cycle Log

성공적으로 완료된 knowledge cycle만 `.private/knowledge_cycle_log.md` EOF에 append합니다.

```bash
python3 -B scripts/append_log.py \
  --cycle-id YYYY-MM-DD-HHMM-knowledge-cycle \
  --source-id src_example_001 \
  --wiki-output wiki/topics/example.md \
  --index-status updated \
  --compile-fidelity-report .private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md \
  --golden-answerability-report .private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-wiki.md \
  --write
```

이 스크립트는 실패한 cycle을 기록하지 않습니다.
중복 cycle ID, 중복 report pair, 중복 source ID, 중복 wiki output, 없는 report, 잘못된 report filename, 없는 wiki output은 거부합니다.

### 9. Public Export Is Separate

공개 가능한 wiki 문서에는 body에 다음 marker를 추가합니다.

```html
<!-- public_safe: true -->
```

그 다음 public export를 실행합니다.

```bash
python3 -B scripts/export_public.py
python3 -B scripts/check_no_raw_leak.py
```

`public_safe: true` marker가 없는 wiki 문서는 export되지 않습니다.
원본 wiki는 수정하지 않습니다.

### 10. Commit Boundary

자동 commit은 하지 않습니다.

보통 commit 대상:

```text
AGENTS.md
README.md
.gitignore
golden_questions.yml
.agents/skills/
scripts/
public/
evals/
```

보통 commit하지 않는 대상:

```text
raw/
.private/
wiki/
```

`git ls-files raw .private wiki`에서 아무것도 나오지 않아야 public/private 경계가 안전합니다.

## Evaluation

`golden_questions.yml`은 이 저장소가 답할 수 있어야 하는 대표 질문입니다.

이 파일은 수동으로 관리하며 skills가 수정하지 않습니다.

목적은 모든 노트를 포괄하는 목차가 아니라, 지식 시스템이 실제로 재사용 가능한지 확인하는 평가 기준입니다.

평가할 때는 `$evaluate-knowledge`를 사용합니다.

```text
$evaluate-knowledge suite=compile-fidelity
$evaluate-knowledge suite=golden-answerability target=wiki
```

평가 결과는 다음 위치에 저장합니다.

```text
.private/eval_runs/
evals/reports/  # legacy read-only reports
```

## Maintenance Rules

* 원본 노트를 임의로 삭제하거나 덮어쓰지 않는다.
* `raw/`, `.private/`, `wiki/`는 기본적으로 공개하지 않는다.
* 공개 가능한 내용은 `public/`에만 둔다.
* 같은 raw source를 반복 컴파일하지 않는다.
* 비슷한 주제의 wiki가 있으면 새 문서를 만들기보다 기존 문서를 업데이트한다.
* 출처 없는 단정은 wiki에 넣지 않는다.
* `golden_questions.yml`은 skills가 수정하지 않는다.
* generated wiki index marker content는 `scripts/update_index.py`로 갱신한다.
* `.private/knowledge_cycle_log.md`는 `scripts/append_log.py`로 EOF에 append한다.
* 서로 다른 도메인의 지식을 한 문서에 억지로 섞지 않는다.
* 자동 커밋하지 않는다.
* 큰 변경이 필요하면 먼저 diff를 보여주고 승인받는다.
* vector DB, graph DB, MCP, embeddings, graph IDs, tags는 P0/P1에서 도입하지 않는다.

## Safety Boundary

이 저장소는 public으로 열려 있을 수 있으므로, 공개되는 파일에는 민감한 정보가 없어야 합니다.

특히 다음은 공개 파일에 남기지 않습니다.

* raw source path
* 회사명, 내부 도메인, 내부 환경명
* credential, token, password, private key
* connection string
* 개인적인 대화나 커리어 세부 맥락
* 투자 판단의 원본 맥락
* 내부 장애 대응 세부 기록

공개 가능한 것은 일반화된 교훈, 기술 개념, 아키텍처 판단, 포트폴리오로 재사용 가능한 설명입니다.

## Current Rule of Thumb

헷갈리면 이 기준을 따릅니다.

```text
raw/       = 원본. 로컬 전용.
.private/  = 처리 이력. 로컬 전용.
wiki/      = 내부 위키. 로컬 전용.
public/    = 공개 가능한 결과물.
scripts/   = 검사와 보조 자동화.
.agents/skills/ = Codex 작업 절차.
```

LLM은 지식을 정리합니다.
scripts는 규칙을 검사합니다.
Git은 공개 가능한 결과만 고정합니다.
