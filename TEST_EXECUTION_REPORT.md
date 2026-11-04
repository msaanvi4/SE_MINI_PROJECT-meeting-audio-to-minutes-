# Test Execution Report

## Meeting Audio to Structured Minutes



**Report date:** 4 November 2026

**Testing responsibility:** Test Plan, Validation, and Evidence

**Project branch:** `member2-audio-transcription`



---



## 1. Purpose



This report records the automated and manual testing performed on the Meeting Audio to Structured Minutes application.



It documents the test environment, execution results, observed application behavior, requirement traceability, and outstanding validation activities.



Only tests that were actually executed are marked as passed. Tests that have not been completed are explicitly identified as pending or not executed.



## 2. Test Environment



| Item | Recorded environment |

|---|---|

| Operating system | Windows (`win32`) |

| Python versions tested | 3.14.6 and 3.11.9 |

| pytest | 9.2.0 |

| Test runner | `python -m pytest -v` |

| Browser | Microsoft Edge |

| Application | Streamlit |

| Local application address | `localhost:8501` |

| Test audio | `sample_meeting.wav` |

| Test date | 4 November 2026 |



**Environment verification:**



The complete automated test suite was executed successfully using both Python 3.14.6 and Python 3.11.9.



Python 3.11.9 matches the Python version specified by the STP/CI configuration.



Both environments collected 23 tests, with all 23 tests passing.



A successful GitHub Actions run has not yet been confirmed.



## 3. Automated Test Execution Summary



**Command executed:**



```cmd

python -m pytest -v

```



### Run 1: Python 3.14.6



| Metric | Result |

|---|---:|

| Tests collected | 23 |

| Passed | 23 |

| Failed | 0 |

| Skipped | 0 |

| Duration | 0.33 seconds |

| Pass rate | 100% |



### Run 2: Python 3.11.9



| Metric | Result |

|---|---:|

| Tests collected | 23 |

| Passed | 23 |

| Failed | 0 |

| Skipped | 0 |

| Duration | 0.75 seconds |

| Pass rate | 100% |



**Overall automated execution:** Both runs completed successfully, giving 46 successful test executions across the two Python environments.



The 100% pass rate applies only to the 23 automated tests executed in each run. It does not represent complete STP requirement coverage or overall project quality.



## 4. Automated Test Execution Details



| Test file | Test case / method | Result |

|---|---|---|

| `test_audio_cleanup.py` | `test_cleanup_deletes_temporary_audio_file` | PASS |

| `test_audio_validator.py` | `test_corrupted_audio` | PASS |

| `test_audio_validator.py` | `test_empty_file` | PASS |

| `test_audio_validator.py` | `test_file_over_100_mb` | PASS |

| `test_audio_validator.py` | `test_supported_wav` | PASS |

| `test_audio_validator.py` | `test_unsupported_format` | PASS |

| `test_integration_pipeline.py` | `test_validated_audio_to_structured_minutes` | PASS |

| `test_minutes_editor_export.py` | `test_docx_export_creates_readable_document` | PASS |

| `test_minutes_editor_export.py` | `test_edited_action_item_is_preserved_in_export` | PASS |

| `test_minutes_editor_export.py` | `test_edits_are_saved` | PASS |

| `test_minutes_extractor.py` | `test_empty_transcript` | PASS |

| `test_minutes_extractor.py` | `test_extract_action_item` | PASS |

| `test_minutes_extractor.py` | `test_extract_deadline` | PASS |

| `test_minutes_extractor.py` | `test_extract_decision` | PASS |

| `test_minutes_extractor.py` | `test_extract_multiple_action_items` | PASS |

| `test_minutes_extractor.py` | `test_extract_owner` | PASS |

| `test_minutes_extractor.py` | `test_extract_topic` | PASS |

| `test_minutes_extractor.py` | `test_missing_owner_and_deadline` | PASS |

| `test_transcription.py` | `test_handles_audio_with_no_recognized_speech` | PASS |

| `test_transcription.py` | `test_handles_transcription_failure` | PASS |

| `test_transcription.py` | `test_rejects_missing_audio_file` | PASS |

| `test_transcription.py` | `test_rejects_unvalidated_audio` | PASS |

| `test_transcription.py` | `test_returns_transcript_successfully` | PASS |



### Integration Test Scope Limitation



The test `test_validated_audio_to_structured_minutes` validates a WAV-like input and passes a simulated transcript to the minutes extractor.



It does not invoke the actual Whisper model.



Actual transcription was separately exercised during the manual application demonstration using `sample_meeting.wav`.



## 5. Manual Test Execution



The application was started locally using Streamlit and opened in Microsoft Edge at `localhost:8501`.



| Manual test | Procedure and observed result | Status |

|---|---|---|

| Valid audio upload | Uploaded `sample_meeting.wav`, shown as approximately 0.48 MB. | PASS |

| Transcript display | Transcript appeared in the Meeting Transcript text area. | PASS |

| Topic extraction | Project deadline topic appeared in generated minutes. | PASS |

| Decision extraction | Decision to review the final design next Monday appeared. | PASS |

| Action item extraction | Priya's report-preparation action item appeared. | PASS |

| Owner and deadline | Owner displayed as Priya; deadline displayed as Friday. | PASS |

| Edit and save | Changed title to "Project Planning Meeting", added "Project report preparation", and received the confirmation message "Your edited minutes have been saved." | PASS |

| DOCX export | Exported Word document opened successfully and contained the edited title, topic, decision, task, owner, and deadline. | PASS |

| Corrupted audio rejection | Uploaded a text file saved with a `.wav` extension. Application displayed "The file appears corrupted or is not a valid audio file." | PASS |

| Prevent transcription before validation | Clicking Transcribe Audio before validating the selected file displayed "Please validate the currently selected file first." | PASS |

| Actual audio transcription | After restoring and validating `sample_meeting.wav`, the user confirmed that transcription worked correctly. A screenshot of the final result is not included in this report. | PASS (user-confirmed) |



## 6. STP-to-SRS Traceability and Execution Status



"Partially verified" means some relevant behavior was tested, but the complete test-case scope was not executed.



| STP test case | Requirement area | Execution status | Evidence / limitation |

|---|---|---|---|

| TC-AUD-01 | MM-F-001 supported audio upload | Partially verified | WAV upload demonstrated; MP3 and M4A not manually demonstrated. |

| TC-AUD-02 | MM-F-002 / MM-SR-005 invalid audio and file boundaries | Partially verified | Automated corrupted, empty, unsupported and over-100-MB tests passed; manual corrupted WAV rejected. Full boundary combinations not independently demonstrated in UI. |

| TC-TR-01 | MM-F-003 transcription | Partially verified | Transcription adapter unit tests passed; actual sample-audio transcription confirmed manually. |

| TC-TR-02 | MM-F-004 transcript/status visibility | Partially verified | Transcript displayed in UI; all status and edge conditions not separately exercised. |

| TC-EXT-01 | MM-F-005 topic extraction | Partially verified | Topic extraction unit test and manual sample demonstrated. |

| TC-EXT-02 | MM-F-006 decision extraction | Partially verified | Decision extraction unit test and manual sample demonstrated. |

| TC-EXT-03 | MM-F-007 multiple action items | Partially verified | Multiple-action-item unit test passed; manual sample showed one action item. |

| TC-EXT-04 | MM-F-008 owner extraction | Partially verified | Owner unit test and manual owner value demonstrated. |

| TC-EXT-05 | MM-F-009 deadline extraction | Partially verified | Deadline unit test and manual deadline value demonstrated. |

| TC-EXT-06 | MM-F-010 missing/ambiguous owner or deadline | Partially verified | Automated missing-owner/deadline test passed; broader ambiguity cases not manually tested. |

| TC-MIN-01 | MM-F-011 structured minutes | Partially verified | Topics, decisions and action items displayed in separate sections. |

| TC-EDIT-01 | MM-F-012 editing | Verified for demonstrated flow | Edited title and topic were saved and appeared in export. |

| TC-EXP-01 | MM-F-013 editable DOCX export | Verified for demonstrated flow | Exported DOCX opened and displayed structured content. |

| TC-EXP-02 | MM-F-014 task-owner-deadline mapping | Verified for demonstrated flow | Export table retained task, owner and deadline. |

| TC-ERR-01 | MM-F-015 meaningful error handling | Partially verified | Corrupted-file and unvalidated-transcription messages observed; other error paths not fully tested. |

| TC-PERF-01 | MM-NF-001 performance | NOT EXECUTED | No timed performance test recorded. |

| TC-UX-01 | MM-NF-002 usability | Partially verified | Basic upload-to-export flow completed; formal first-time-user evaluation not performed. |

| TC-REL-01 | MM-NF-003 reliability/recovery | Partially verified | Invalid input was rejected and app remained usable; broader recovery scenarios not tested. |

| TC-MAINT-01 | MM-NF-004 maintainability/testability | Partially verified | Automated unit tests exist and passed; no formal maintainability assessment performed. |

| TC-COMP-01 | MM-NF-005 compatibility | NOT EXECUTED | Demonstrated in one Windows/Edge environment only; full compatibility matrix not tested. |

| TC-SEC-01 | MM-SR-001 secure transport | NOT EXECUTED / architecture confirmation pending | Local demonstration does not verify remote HTTPS/TLS behavior. |

| TC-SEC-02 | MM-SR-002 secret handling | NOT EXECUTED | No dedicated secrets scan or repository audit recorded. |

| TC-SEC-03 | MM-SR-003 session isolation | NOT EXECUTED | Multi-session isolation not tested. |

| TC-SEC-04 | MM-SR-004 privacy-safe logging | NOT EXECUTED | Logs were not audited for sensitive content. |

| TC-SEC-05 | MM-SR-005 file validation boundaries | Partially verified | Automated file validation tests passed; further file-boundary/security testing remains. |



## 7. Observations and Issues to Report



### OBS-01: File-size information mismatch



**Observation:** The application information banner states a maximum file size of 100 MB, while the Streamlit upload control displayed "200MB per file".



**Impact:** Users may receive inconsistent information about the supported upload limit.



**Status:** Observed; requires confirmation of the intended limit by the feature owner and alignment of the UI text/configuration.



### OBS-02: Previous transcript remained visible after invalid file selection



**Observation:** After selecting an invalid audio file, the previous transcript remained visible in the transcript area.



**Impact:** A user could potentially mistake an earlier transcript for the result of the currently selected file.



**Status:** Needs investigation. This is a potential stale-state issue, not a confirmed defect until reproduced and reviewed by the feature owner.



### OBS-03: Python version verification



**Observation:** Initial local test execution used Python 3.14.6, while the STP and GitHub Actions workflow specify Python 3.11.



**Additional verification:** The complete automated suite was subsequently executed using Python 3.11.9, with all 23 tests passing.



**Status:** Local Python 3.11 verification completed. GitHub Actions execution remains to be confirmed.



## 8. Tests and Activities Still Pending



The following activities should be completed before claiming full validation:



1. Confirm a successful GitHub Actions run for the relevant branch or pull request.

2. Execute remaining performance tests.

3. Execute remaining security and session-isolation tests.

4. Complete the compatibility test matrix.

5. Verify MP3 and M4A uploads if they are in the supported scope.

6. Investigate the file-size mismatch with the feature owner.

7. Reproduce and investigate the stale-transcript observation.

8. COMPLETED - Captured and stored 9 manual-testing screenshots in the evidence/ folder. The screenshots cover automated test results, Python 3.11 verification, valid audio validation, transcription, extracted minutes, editing, DOCX export, invalid audio validation, and the validation-required message.

9. Ensure no private audio or sensitive information is included in submitted evidence.



## 9. Overall Conclusion



The complete automated test suite consisting of 23 tests passed successfully in both Python 3.14.6 and Python 3.11.9 environments using pytest 9.2.0.



The manual demonstration verified the main sample workflow, including audio upload, transcript display, structured minutes generation, editing, saving, and DOCX export.



Invalid audio was rejected, and transcription was blocked until validation.



These results demonstrate successful execution of the automated tests and the documented manual scenarios. They do not establish that every STP requirement has passed.



Performance, security, full compatibility, and GitHub Actions validation remain pending. The observed file-size mismatch and possible
