# Code Coverage Report

**Project:** Meeting Audio to Structured Minutes  
**Date:** 19 November 2026  
**Tool:** Coverage.py  
**Test Framework:** Pytest

## 1. Test Execution Summary

The complete automated test suite was executed using:

`python -m coverage run --branch -m pytest -v`

Results:
- Total tests: 63
- Passed: 63
- Failed: 0
- Execution time: 12.88 seconds

## 2. Application-Only Coverage

Test files and the separate performance testing utility were excluded.

Command:

`python -m coverage report --include="app.py,app/*,audio_validator.py,docx_exporter.py,minutes_editor.py,minutes_extractor.py,transcription.py,validated_audio.py"`

| Metric | Result |
|---|---:|
| Statements | 615 |
| Statements covered | 520 |
| Statements missed | 95 |
| Statement coverage | 84.55% |
| Branches | 236 |
| Branches covered | 186 |
| Branches missed | 50 |
| Partially covered branches | 34 |
| Branch coverage | 78.81% |
| Coverage.py total | 83% |

## 3. Full-Project Coverage

This measurement includes application code, test files and supporting project files.

| Metric | Result |
|---|---:|
| Statements | 1,281 |
| Statements covered | 1,133 |
| Statements missed | 148 |
| Statement coverage | 88.45% |
| Branches | 262 |
| Branches covered | 199 |
| Branches missed | 63 |
| Partially covered branches | 43 |
| Branch coverage | 75.95% |
| Coverage.py total | 86% |

## 4. Coverage Observations

- The application-only statement coverage is 84.55%.
- The application-only branch coverage is 78.81%.
- Audio validation has 85% statement coverage.
- Minutes extraction has 92% statement coverage.
- Export functionality has strong coverage, with app export at 98%.
- Transcription and validated-audio handling contain additional untested paths.

## 5. Conclusion

The complete automated test suite passed all 63 tests.

Coverage results indicate that the core application workflows have substantial automated test coverage. Some conditional branches and error-handling paths remain uncovered and can be considered for future testing improvements.