# Tasks: 手机端双按键映射通道重构 (key-mappings-redesign)

**Input**: Design documents from `/specs/004-key-mappings-redesign/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY (TDD Rule III) - always write failing tests before implementing production code.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and validation of environment

- [ ] T001 Verify active git branch is `004-key-mappings-redesign` and working tree is ready
- [ ] T002 Ensure project python dependencies are synced using `uv sync` or virtualenv is loaded

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core validation tests to ensure current baseline passes before any change

- [ ] T003 Execute the baseline test suite via `pytest` to ensure 100% green before editing

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 正常文本发送与追加按键解耦 (Priority: P1) 🎯 MVP

**Goal**: Deliver clean text sending that appends keys only when configured, decoupled from single-send dropdown, and cache state to local storage.

**Independent Test**: Put "发送时追加" select to "无", send text, verify it records on PC without trailing key simulation.

### Tests for User Story 1 (MANDATORY - TDD Phase) ⚠️

- [ ] T004 [US1] Write a failing test in tests/test_backend.py that asserts `mobile.html` stores `selected_key_mapping_id` to LocalStorage and applies it on send only when input is not empty

### Implementation for User Story 1

- [ ] T005 [US1] Remove deprecated label and styling blocks from the HTML body in phonemic/resources/mobile.html
- [ ] T006 [US1] Relocate `#key-mapping-select` to the newly structured `#shortcut-bar` in phonemic/resources/mobile.html
- [ ] T007 [US1] Update the JS select change listener to save selection to LocalStorage key `selected_key_mapping_id` in phonemic/resources/mobile.html
- [ ] T008 [US1] Update JS `sendCurrentMessage` to fetch and apply selection to WebSocket message payload only when textbox has content in phonemic/resources/mobile.html

**Checkpoint**: User Story 1 is functional and testable independently.

---

## Phase 4: User Story 2 - 空输入快速触发单独按键 (Priority: P1)

**Goal**: Permit users to click the send button or hit keyboard Enter to trigger a single key mapping simulation when textbox is empty.

**Independent Test**: Clear text input, set "单独发按键" select to Tab, click "发送", confirm PC simulation triggers once and screen echoes `[单独发送按键]`.

### Tests for User Story 2 (MANDATORY - TDD Phase) ⚠️

- [ ] T009 [US2] Write a failing test in tests/test_backend.py that asserts `mobile.html` defines `single-key-mapping-select`, implements empty-textbox logic routing, and caches `selected_single_key_mapping_id`

### Implementation for User Story 2

- [ ] T010 [US2] Add the `#single-key-mapping-select` dropdown structure to the `#shortcut-bar` in phonemic/resources/mobile.html
- [ ] T011 [US2] Bind select change listener to save selection to LocalStorage key `selected_single_key_mapping_id` in phonemic/resources/mobile.html
- [ ] T012 [US2] Restore state on page load by reading `selected_single_key_mapping_id` in phonemic/resources/mobile.html
- [ ] T013 [US2] Modify JS `sendCurrentMessage` to check if input is empty, and route to `sendKeyMappingOnly` using `#single-key-mapping-select` value in phonemic/resources/mobile.html
- [ ] T014 [US2] Implement chatManager echo format in `sendKeyMappingOnly` method in phonemic/resources/mobile.html
- [ ] T015 [US2] Add disabled/enabled connection transition logic to `#single-key-mapping-select` in phonemic/resources/mobile.html

**Checkpoint**: User Stories 1 and 2 are both independently functional and testable.

---

## Phase 5: User Story 3 - 界面去噪与控制台简化 (Priority: P2)

**Goal**: Style the dual-dropdown panels neatly, clean up unused CSS styles, and drop the deprecated physical rocket send button.

**Independent Test**: Run layout verification to ensure rocket button elements are gone.

### Tests for User Story 3 (MANDATORY - TDD Phase) ⚠️

- [ ] T016 [US3] Write a failing test in tests/test_backend.py that asserts `btn-send-mapping` elements are completely absent from `mobile.html`

### Implementation for User Story 3

- [ ] T017 [US3] Remove `#btn-send-mapping` element and its click listener bindings in phonemic/resources/mobile.html
- [ ] T018 [US3] Restructure CSS styling classes of `#shortcut-bar` and select boxes to align beautifully in phonemic/resources/mobile.html

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Polish CSS styling, update i18n variables, run quickstart validation, and produce final walkthrough.

- [ ] T019 Update French/English translation strings if needed in phonemic/resources/locales/
- [ ] T020 Run `render_preview.py` and inspect layout alignment in browser
- [ ] T021 Execute full pytest suite to verify all unit tests pass
- [ ] T022 Perform manual scenarios validation per quickstart.md and generate walkthrough.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Stories**: All depend on Foundational completion, developed sequentially (US1 -> US2 -> US3).
- **Polish (Phase 6)**: Depends on all user stories completion.

### Parallel Opportunities

- Unit tests writing (T004, T009, T016) can run in parallel before writing code.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2.
2. Complete Phase 3 (US1 - text decoupled send).
3. Validate US1 works independently before starting US2.
