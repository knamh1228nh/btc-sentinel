# Step 2. AI Analyst 구현 계획

## 1. Gemini API 연동 – .env / 환경 변수

### 결론: **GOOGLE_API_KEY는 불필요, 기존 GEMINI_API_KEY만 사용**

| 항목 | 내용 |
|------|------|
| **현재 설정** | `.env` / `config.py`에 `GEMINI_API_KEY` 이미 사용 중 |
| **SDK 동작** | `google-generativeai`는 `genai.configure(api_key=...)`로 키 전달 가능. env 자동 읽기는 `GOOGLE_API_KEY` 이름 사용 |
| **권장** | 코드에서 `settings.GEMINI_API_KEY`를 읽어 `genai.configure(api_key=settings.GEMINI_API_KEY)`로 설정. `.env`에는 **GEMINI_API_KEY만 유지** (GOOGLE_API_KEY 추가 불필요) |

---

## 2. 연동 구조 (Plan)

```
anomaly_logs에 새 행 INSERT
       │
       ▼
save_anomaly_event() → Supabase INSERT → 응답으로 id 수신
       │
       ▼
Background Task (thread) 시작: 분석 요청
       │
       ├─► analyzer.analyze_with_gemini(가격, 거래량, 변동률)
       │         │
       │         ▼
       │   Gemini API: "현재 시장 상황이 기술적으로 어떤 의미인지 3줄 이내로 분석해줘"
       │         │
       │         ▼
       │   분석 텍스트(3줄) 반환
       │
       ▼
Supabase에 분석 결과 저장
  - 옵션 A: analysis_results 테이블 (anomaly_log_id, summary, created_at)
  - 옵션 B: anomaly_logs.comment 컬럼 추가 후 해당 행 UPDATE
  → 구현: 옵션 B 우선 (comment 컬럼 추가), 필요 시 analysis_results 테이블 추가 가능
```

---

## 3. 비동기(Background) 처리 방식

- **상황**: `save_anomaly_event()`는 WebSocket 스레드에서 호출되며, FastAPI 요청 컨텍스트가 없음.
- **선택**: **`threading.Thread`로 백그라운드 실행**
  - `save_anomaly_event()` 성공 후 삽입된 행의 `id`를 받음.
  - `threading.Thread(target=run_analysis_background, args=(anomaly_log_id, market_data, detection_result), daemon=True).start()` 호출.
- **백그라운드 함수** `run_analysis_background(id, market_data, detection_result)`:
  1. `analyzer.analyze_with_gemini(...)` 호출 → 3줄 분석 텍스트 획득.
  2. Supabase에서 해당 `anomaly_logs.id` 행의 `comment`(또는 analysis_results 행) 업데이트.

이렇게 하면 anomaly_logs에 새 로그가 쌓일 때마다 **자동으로** Gemini 분석이 한 번씩 비동기로 실행되고, 결과만 DB에 반영됩니다.

---

## 4. 구현 체크리스트

- [x] `app/core/analysis/analyzer.py`: Gemini 호출 + 3줄 프롬프트, 결과 반환.
- [x] `app/core/analysis/prompts.py`: 프롬프트 문자열 정의.
- [x] Supabase: `anomaly_logs`에 `comment` 컬럼 추가 마이그레이션 (003).
- [x] `analyzer.run_analysis_and_save_comment`: 분석 결과로 `anomaly_logs.comment` 업데이트.
- [x] `detector`: INSERT 후 반환된 id로 `threading.Thread` 백그라운드 시작.
- [x] config: `GEMINI_API_KEY` 사용 유지 (GOOGLE_API_KEY 불필요).
