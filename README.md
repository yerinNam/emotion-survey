# 감정 단어 설문

감정 단어 13개와 얼굴 표정 사진 13장으로 진행하는 2단계 웹 설문입니다. `index.html` 파일 하나로 동작하며, 응답은 제출할 때 JSONL 파일로 내려받아집니다.

## 실행

`index.html`을 브라우저(Chrome, Edge, Safari, Firefox 최신판)로 열면 됩니다. 서버나 설치가 필요 없고, 인터넷이 없어도 동작합니다. 인터넷이 없을 때는 글꼴만 시스템 글꼴로 바뀝니다.

## 진행 순서

1. **시작**: 참가자 번호를 입력합니다.
2. **1단계, 감정 단어 묶기**: 색을 고른 뒤 단어 카드를 눌러 칠하는 방식으로, 뜻이 비슷한 단어끼리 묶습니다. 13개를 모두 칠해야 ‘다음 페이지’로 넘어가며, 넘어간 뒤에는 돌아올 수 없습니다.
3. **2단계, 표정과 단어 짝짓기**: 얼굴마다 1순위 단어(필수)와 2순위 단어(선택)를 고르고, 각각 확신도를 1~5점으로 매깁니다.
   - 고르는 동안에는 같은 단어를 여러 얼굴에 써도 됩니다.
   - 제출하려면 1순위 단어 13개가 얼굴마다 하나씩, 겹치지 않게 짝지어져 있어야 합니다.
   - 2순위를 넣었다면 그 확신도도 있어야 합니다.
4. **제출**: `emotion_survey_<참가자번호>_<날짜-시각>.jsonl` 파일이 내려받아집니다.

카드 순서, 얼굴 순서, 단어 목록 순서는 참가자마다 무작위로 바뀝니다.

## 저장 형식 (JSONL, 참가자 1명당 14줄)

모든 줄에 `participant_id`, `session_id`, `part`가 들어갑니다.

**1줄: `"part": "word_clustering"`**

| 필드 | 내용 |
|---|---|
| `groups` | 묶음 목록. 묶음마다 `group_no`, `name`(참가자가 붙인 이름, 없으면 빈 문자열), `size`, `words`가 들어갑니다. |
| `assignment` | 단어별 묶음 번호. 예: `{"열망": 1, "탐욕": 1, …}` |
| `n_groups` | 묶음 개수 |
| `card_order` | 화면에 보인 카드 순서 |
| `history` | 칠하고 지운 기록 (`t_ms`, `action`, `word`, `group_id` …) |
| `started_at`, `finished_at`, `duration_sec` | 시작 시각, 끝난 시각, 걸린 시간(초) |

**13줄: `"part": "face_matching"` (얼굴 1장당 1줄)**

| 필드 | 내용 |
|---|---|
| `face_no` | 화면에 보인 번호(제시 순서) |
| `image_id`, `image_file` | 이미지 ID와 원본 파일 이름 |
| `target_word` | 의도한 감정 (CSV 기준) |
| `rank1_word`, `rank1_confidence` | 1순위 단어와 확신도(1~5) |
| `rank2_word`, `rank2_confidence` | 2순위 단어와 확신도. 고르지 않았으면 `null` |
| `rank1_correct` | 1순위가 의도한 감정과 같은지 |
| `target_in_top2` | 의도한 감정이 1순위나 2순위 안에 있는지 |
| `n_word_changes`, `n_confidence_changes` | 단어와 확신도를 바꾼 횟수 |
| `history` | 그 얼굴에서 단어를 놓고 빼고 바꾼 기록 |
| `word_bank_order` | 화면에 보인 단어 목록 순서 |
| `started_at`, `submitted_at`, `duration_sec` | 2단계 시작 시각, 제출 시각, 걸린 시간(초) |

여러 참가자 파일은 그대로 이어 붙이면 하나의 데이터셋이 됩니다. 예: `cat emotion_survey_*.jsonl > all.jsonl`.
Python에서는 `pandas.read_json('all.jsonl', lines=True)`로 읽은 뒤 `part`로 나누어 쓰면 됩니다.

## 설정 바꾸기

`src/survey_template.html` 아래쪽 `<script>`의 `CONFIG`에서 바꿀 수 있습니다. 바꾼 뒤에는 아래 ‘다시 만들기’를 실행합니다.

| 항목 | 기본값 | 설명 |
|---|---|---|
| `shuffleCards`, `shuffleImages`, `shuffleWords` | `true` | 카드, 얼굴, 단어 목록 순서를 무작위로 할지 |
| `confMin`, `confMax` | `1`, `5` | 확신도 척도 범위 |
| `confQuestion`, `confLabels` |  | 확신도 질문과 양 끝 문구 |
| `uniqueFirst` | `true` | 제출할 때 1순위 단어가 얼굴마다 겹치지 않아야 하는지 |
| `uniqueSecond` | `false` | 2순위도 겹치지 않아야 하는지 |

## 이미지나 단어 바꾸기 (다시 만들기)

1. `stimuli/`에 있는 `번호_단어.png` 파일과 `00_감정단어_이미지_일람표.csv`를 바꿉니다. 파일 이름의 번호와 단어가 CSV의 `번호`, `감정단어`와 맞아야 합니다.
2. 아래 명령을 실행하면 `index.html`이 새로 만들어집니다.

```bash
pip install pillow
python build.py
```

이미지는 무손실 WebP로 바꿔 넣고, 원본과 픽셀 단위로 같은지 확인합니다. 해상도와 화질은 원본 그대로입니다.

## 폴더 구성

```
index.html                 # 참가자에게 주는 설문 파일 (이미지 포함, 약 25MB)
build.py                   # stimuli → index.html 만드는 스크립트
src/survey_template.html   # 설문 화면과 로직 (이미지 제외 원본)
stimuli/                   # 원본 표정 이미지 13장과 단어 목록 CSV
```

## 참고

- 화면에는 얼굴 번호만 보이고 의도한 감정은 보이지 않습니다. 다만 HTML 소스 안에는 `target_word`가 들어 있으므로, 개발자 도구를 여는 참가자는 볼 수 있습니다.
- CSV의 `저장된_파일명`은 자극 폴더의 PNG 이름이고, `원본_파일명`은 생성 이미지의 파일 이름입니다. `build.py`는 `번호`와 `감정단어`로 PNG를 찾습니다.
