# Branch Coverage Report

**Project:** Meeting Audio to Structured Minutes  
**Date:** 19 November 2026  
**Tool:** Coverage.py with branch measurement enabled

## 1. Test Execution

Command:

`python -m coverage run --branch -m pytest -v`

Results:
- Total tests: 63
- Passed: 63
- Failed: 0
- Execution time: 12.88 seconds

## 2. Application-Only Branch Coverage

Test files and the separate performance testing utility were excluded.

| Metric | Result |
|---|---:|
| Total branches | 236 |
| Covered branches | 186 |
| Missing branches | 50 |
| Partially covered branches | 34 |
| Branch coverage | 78.81% |

## 3. Full-Project Branch Coverage

This measurement includes application code, test files and supporting project files.

| Metric | Result |
|---|---:|
| Total branches | 262 |
| Covered branches | 199 |
| Missing branches | 63 |
| Partially covered branches | 43 |
| Branch coverage | 75.95% |

## 4. Observations

- Application-only branch coverage is 78.81%.
- Full-project branch coverage is 75.95%.
- Some conditional paths remain partially covered.
- Additional tests can improve coverage of error handling, validation failures and less frequently used application paths.

## 5. Conclusion

All 63 automated tests passed successfully. The branch coverage results indicate that the main application workflows are tested, while some alternative execution paths remain candidates for future test improvements.