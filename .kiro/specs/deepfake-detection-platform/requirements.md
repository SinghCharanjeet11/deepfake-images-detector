# Requirements Document

## Introduction

This document covers the requirements for a web platform that lets users upload images or videos
and find out whether the media is a deepfake. The platform is aimed at two groups: general members
of the public who want a quick answer, and researchers who need detailed results they can export.

The platform has three core features that must work reliably before anything else is added:

1. Upload a file and get a detection result (real or fake, with a confidence score)
2. View a personal history of past detection results
3. Download a report of any past result as a PDF or JSON file

The detection models are trained from scratch using five standard deepfake datasets:
DeepFake-TIMIT, FaceForensics++, Google DFD, Celeb-DF, and Facebook DFDC.

The UI must be clean and plain. No AI-themed visuals, no jargon, no gimmicks.

---

## Glossary

- **Platform**: The web application described in this document.
- **User**: A person who has registered and logged in to the Platform.
- **Guest**: A person who visits the Platform without logging in.
- **Media_File**: An image (JPEG, PNG) or video (MP4, AVI, MOV) uploaded by a User.
- **Detection_Job**: A single run of the detection model against one Media_File.
- **Detection_Result**: The output of a Detection_Job, containing a label (real or fake) and a confidence score.
- **Confidence_Score**: A decimal number between 0.0 and 1.0 representing how certain the model is of its label.
- **History**: The list of all Detection_Results belonging to a User, ordered from newest to oldest.
- **Report**: A downloadable file (PDF or JSON) containing the details of one Detection_Result.
- **Detector**: The ML/DL inference component that processes a Media_File and produces a Detection_Result.
- **API**: The FastAPI backend that handles all requests between the frontend and the Detector.
- **Dashboard**: The frontend page that displays a User's History.

---

## Requirements

### Requirement 1: User Registration and Login

**User Story:** As a visitor, I want to create an account and log in, so that my detection results
are saved and only visible to me.

#### Acceptance Criteria

1. THE Platform SHALL allow a Guest to register with an email address and password.
2. WHEN a Guest submits a registration form with a valid email and a password of at least 8 characters, THE Platform SHALL create a new User account.
3. IF a Guest submits a registration form with an email that already exists, THEN THE Platform SHALL return an error message stating the email is already in use.
4. WHEN a User submits valid login credentials, THE Platform SHALL issue a session token valid for 24 hours.
5. IF a Guest submits incorrect login credentials, THEN THE Platform SHALL return an error message and SHALL NOT issue a session token.
6. WHILE a User's session token is valid, THE Platform SHALL allow the User to access protected pages.
7. IF a request is made to a protected endpoint without a valid session token, THEN THE API SHALL return an HTTP 401 response.
8. WHEN a User logs out, THE Platform SHALL invalidate the session token immediately.

---

### Requirement 2: Media Upload

**User Story:** As a User, I want to upload an image or video file, so that I can find out whether
it is a deepfake.

#### Acceptance Criteria

1. THE Platform SHALL accept image files in JPEG and PNG formats.
2. THE Platform SHALL accept video files in MP4, AVI, and MOV formats.
3. THE Platform SHALL accept Media_Files up to 500 MB in size.
4. IF a Guest attempts to upload a file without being logged in, THEN THE Platform SHALL redirect the Guest to the login page.
5. IF a User uploads a file with an unsupported format, THEN THE API SHALL return an error message listing the accepted formats.
6. IF a User uploads a file larger than 500 MB, THEN THE API SHALL return an error message stating the size limit.
7. WHEN a User uploads a valid Media_File, THE Platform SHALL display an upload progress indicator until the upload is complete.
8. WHEN a valid Media_File upload is complete, THE API SHALL create a Detection_Job and return a job identifier to the frontend.

---

### Requirement 3: Deepfake Detection

**User Story:** As a User, I want the platform to analyse my uploaded file and tell me whether it
is real or fake, so that I can make an informed judgement about the media.

#### Acceptance Criteria

1. WHEN a Detection_Job is created, THE Detector SHALL process the Media_File and produce a Detection_Result.
2. THE Detector SHALL classify every Media_File as either "real" or "fake".
3. THE Detector SHALL produce a Confidence_Score for every Detection_Result.
4. THE Detector SHALL produce a Confidence_Score that is always between 0.0 and 1.0 inclusive.
5. WHEN a Detection_Job is complete, THE API SHALL store the Detection_Result linked to the User and the Media_File.
6. WHEN a Detection_Job is complete, THE Platform SHALL display the label and Confidence_Score to the User.
7. WHILE a Detection_Job is running, THE Platform SHALL display a status indicator so the User knows processing is in progress.
8. IF a Detection_Job fails due to a processing error, THEN THE API SHALL store the failure status and THE Platform SHALL display a plain error message to the User.
9. WHEN processing an image file, THE Detector SHALL return a Detection_Result within 10 seconds.
10. WHEN processing a video file up to 2 minutes in length, THE Detector SHALL return a Detection_Result within 120 seconds.

---

### Requirement 4: Results Dashboard and History

**User Story:** As a User, I want to see all my past detection results in one place, so that I can
review and compare them over time.

#### Acceptance Criteria

1. THE Dashboard SHALL display all Detection_Results belonging to the logged-in User.
2. THE Dashboard SHALL display Detection_Results ordered from newest to oldest by submission time.
3. THE Dashboard SHALL display, for each Detection_Result: the original filename, the submission timestamp, the label, and the Confidence_Score.
4. THE Dashboard SHALL display a thumbnail preview for image Media_Files.
5. WHERE a Media_File is a video, THE Dashboard SHALL display the first frame as a thumbnail preview.
6. WHEN a User has no Detection_Results, THE Dashboard SHALL display a message prompting the User to upload a file.
7. THE Dashboard SHALL support pagination, displaying at most 20 Detection_Results per page.
8. WHEN a User clicks on a Detection_Result in the Dashboard, THE Platform SHALL display the full details of that result on a separate page.

---

### Requirement 5: Report Export

**User Story:** As a User, I want to download a report of a detection result, so that I can save
or share the findings outside the platform.

#### Acceptance Criteria

1. WHEN a User views a Detection_Result detail page, THE Platform SHALL offer a download option for a PDF report and a JSON report.
2. WHEN a User requests a PDF report, THE API SHALL generate and return a PDF file containing: the filename, submission timestamp, label, Confidence_Score, and a platform watermark.
3. WHEN a User requests a JSON report, THE API SHALL return a JSON file containing: the filename, submission timestamp, label, and Confidence_Score as structured fields.
4. THE JSON report SHALL be a valid JSON document that can be parsed by any standard JSON parser.
5. FOR ALL valid Detection_Results, parsing the JSON report and re-serialising it SHALL produce a document with identical field values (round-trip property).
6. IF a User requests a report for a Detection_Result that does not belong to them, THEN THE API SHALL return an HTTP 403 response.

---

### Requirement 6: File Handling and Storage

**User Story:** As a backend system, I want uploaded files to be stored and managed safely, so
that the platform remains reliable and secure.

#### Acceptance Criteria

1. THE API SHALL store each uploaded Media_File with a unique server-side identifier, not the original filename.
2. THE API SHALL validate the MIME type of every uploaded file before storing it.
3. IF the MIME type of an uploaded file does not match an accepted format, THEN THE API SHALL reject the file and return an error.
4. THE API SHALL store Media_Files in a location that is not directly accessible via a public URL.
5. WHEN a Detection_Job is complete, THE API SHALL retain the Media_File for 30 days and then delete it automatically.
6. THE API SHALL retain Detection_Result records indefinitely unless a User deletes them.

---

### Requirement 7: Security

**User Story:** As a User, I want my data and uploads to be handled securely, so that my files
and results are not accessible to others.

#### Acceptance Criteria

1. THE API SHALL enforce HTTPS for all communication between the frontend and the backend.
2. THE API SHALL sanitise all user-supplied input before storing or processing it.
3. IF a User attempts to access a Detection_Result or Media_File belonging to another User, THEN THE API SHALL return an HTTP 403 response.
4. THE Platform SHALL store passwords as salted hashes and SHALL NOT store plaintext passwords.
5. THE API SHALL rate-limit upload requests to a maximum of 10 uploads per User per hour.
6. IF a User exceeds the upload rate limit, THEN THE API SHALL return an HTTP 429 response with a message stating when the limit resets.

---

### Requirement 8: Usability

**User Story:** As a User, I want the platform to be easy to use without needing any technical
knowledge, so that I can get results without confusion.

#### Acceptance Criteria

1. THE Platform SHALL display all labels and messages in plain language without technical jargon.
2. THE Platform SHALL display a Confidence_Score as a percentage (e.g. "87% confident") rather than a raw decimal.
3. THE Platform SHALL be usable on screen widths from 375px (mobile) to 1440px (desktop) without horizontal scrolling.
4. WHEN a form submission fails validation, THE Platform SHALL display an inline error message next to the relevant field.
5. THE Platform SHALL load the Dashboard page within 3 seconds on a standard broadband connection.
6. THE Platform SHALL provide descriptive alt text for all images displayed in the UI.

---

## Correctness Properties for Property-Based Testing

These properties must hold for all valid inputs. They are suitable for automated property-based tests.

### P1: Confidence Score Range (Invariant)
For every Media_File processed by the Detector, the Confidence_Score in the Detection_Result
must satisfy: `0.0 <= confidence_score <= 1.0`.
This must hold regardless of file type, file size (within limits), or file content.

### P2: Detection Label Completeness (Invariant)
For every Detection_Result produced by the Detector, the label must be exactly one of the
two values: `"real"` or `"fake"`. No other value is permitted.

### P3: History Count Monotonicity (Invariant)
After each successful Detection_Job for a User, the number of entries in that User's History
must be exactly one greater than before the job was submitted.
Formally: `len(history_after) == len(history_before) + 1`.

### P4: History Ordering (Invariant)
For any User with two or more Detection_Results, every entry in the History must have a
submission timestamp greater than or equal to the timestamp of the entry that follows it.
Formally: for all i, `history[i].timestamp >= history[i+1].timestamp`.

### P5: JSON Report Round-Trip (Round-Trip Property)
For any valid Detection_Result, serialising it to a JSON report and then parsing that JSON
back into a result object must produce an object with identical field values.
Formally: `parse(serialize(result)) == result` for all fields: filename, timestamp, label, confidence_score.

### P6: File Rejection for Invalid Types (Error Condition)
For any uploaded file whose MIME type is not in the accepted set
(image/jpeg, image/png, video/mp4, video/avi, video/quicktime), the API must always return
an error response and must never create a Detection_Job.

### P7: Unauthorised Access Always Rejected (Error Condition)
For any request to a protected endpoint made without a valid session token, the API must
always return HTTP 401. This must hold for every protected route without exception.

### P8: Ownership Enforcement (Error Condition)
For any request by User A to access a Detection_Result or Media_File owned by User B
(where A ≠ B), the API must always return HTTP 403 and must never return the resource.

---

## Out of Scope

The following items are explicitly not part of this project:

- Real-time or live video stream analysis
- Audio deepfake detection
- Browser extension or mobile app
- Third-party integrations (social media, cloud storage)
- Admin panel or moderation tools
- Model retraining or fine-tuning through the UI
- Explainability features (e.g. heatmaps showing which regions triggered the detection)
- Multi-language support
- Paid tiers or subscription billing
- Public API access for external developers
