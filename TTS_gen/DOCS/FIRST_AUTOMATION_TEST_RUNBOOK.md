# TTS_gen First Automation Test Runbook

Last verified: November 17, 2026

This runbook takes the project from its current state to the first real Google
Drive-backed, authored-timeline automation test. Complete the sections in order.

The local Phase 0 worker has already passed a real 1080x1920 render. FFmpeg,
FFprobe, Kokoro, media verification, and the 32-test unit suite are working.
The remaining work is Google account configuration and the first Drive endpoint
test.

## Important boundaries

- The first test does **not** require Gemini, Langflow, a Gemini API key, or a
  vertical teaser. It uses an authored `video-timeline.json`.
- Do not register Windows Task Scheduler until the manual Drive test and the
  duplicate-prevention rerun both succeed.
- The application requests `drive.readonly`, which can view and download every
  file in the authorized Drive account. Use a development Google account if you
  do not want to grant that scope on your primary Drive.
- Do not place OAuth client JSON, refresh tokens, or API keys in this repository.
- `.env` is currently an example only. The application does not automatically
  load it. Set variables in the PowerShell session exactly as described below.

## Stage 1 - Open a fresh PowerShell and verify local prerequisites

1. Close old PowerShell windows so they do not retain the pre-install PATH.
2. Open a new PowerShell window.
3. Change to the project directory:

   ```powershell
   Set-Location 'C:\Users\ricky\Tools\TTS_gen'
   ```

4. Verify FFmpeg and FFprobe:

   ```powershell
   ffmpeg -version
   ffprobe -version
   ```

   Expected: both commands print version `9.0.2` or later and exit without a
   "command not found" error.

5. Verify the project environment:

   ```powershell
   .\.venv\Scripts\python.exe -c "import kokoro, soundfile; print('Kokoro environment OK')"
   ```

6. Run the test suite:

   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
   ```

   Expected: `Ran 32 tests` followed by `OK`.

## Stage 2 - Install the Google Drive Python libraries

From the project directory, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements-drive.txt
```

Verify the imports:

```powershell
.\.venv\Scripts\python.exe -c "from googleapiclient.discovery import build; from google_auth_oauthlib.flow import InstalledAppFlow; print('Google libraries OK')"
```

Expected: `Google libraries OK`.

## Stage 3 - Create or select a Google Cloud development project

Use the same Google account whose Drive will contain the test folders.

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Use the project selector at the top of the page.
3. Select an existing development project or choose **New project**.
4. If creating a project:
   - Project name: `TTS-gen-development`
   - Organization: leave unchanged unless this belongs to a Workspace
     organization.
   - Billing: billing is not required for the Drive API test.
5. Confirm the new project is selected before continuing.

Record the project name here for your own reference:

```text
Project name: Story-gen
```

## Stage 4 - Enable the Google Drive API

1. In Google Cloud Console, open **APIs & Services > Library**.
2. Search for `Google Drive API`.
3. Open **Google Drive API**.
4. Select **Enable**.
5. Wait until the API overview page appears.

Official reference: [Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis).

## Stage 5 - Configure Google Auth Platform

The current Google Cloud interface places these settings under **Google Auth
Platform**.

### 5.1 Branding

1. Open **Google Auth Platform > Branding**.
2. If the platform is not configured, choose **Get Started**.
3. Enter:
   - App name: `TTS_gen Drive Queue`
   - User support email: your Google account email
   - Developer contact email: your Google account email
4. Accept the Google API Services User Data Policy only after reading it.
5. Save or continue.

Do not upload a logo for this private test; it can introduce additional
verification requirements.

### 5.2 Audience

1. Open **Google Auth Platform > Audience**.
2. For a normal personal Gmail account, choose **External**.
3. Keep the publishing status as **Testing** for the first test.
4. Under **Test users**, add the exact Google account that will authorize the
   Drive connection.
5. Save.

Testing mode is appropriate for initial development, but its authorization can
expire after seven days. After the automation is accepted, decide whether to
publish the app and complete any required verification. Google documents the
Testing and In production behavior in [Manage App Audience](https://support.google.com/cloud/answer/15549945).

### 5.3 Data Access scopes

1. Open **Google Auth Platform > Data Access**.
2. Choose **Add or remove scopes**.
3. Add both exact scopes:

   ```text
   https://www.googleapis.com/auth/drive.readonly
   https://www.googleapis.com/auth/drive.file
   ```

4. Save the scope selection.

`drive.readonly` is a restricted scope with broad read/download access.
`drive.file` allows the application to create and manage files it uses. Review
Google's scope descriptions before continuing:
[Choose Google Drive API scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth).

## Stage 6 - Create the Desktop OAuth client

1. Open **Google Auth Platform > Clients**.
2. Select **Create Client**.
3. Application type: **Desktop app**.
4. Name: `TTS_gen Windows Worker`.
5. Leave **Use this client for an AI-powered agent** unchecked for this Drive
   transport client unless you intentionally want Google to classify it that
   way. The client is authenticating the local Drive queue, not Gemini.
6. Select **Create**.
7. Download the client JSON.

Record the client ID and downloaded JSON filename in your password manager or
other approved secrets store. Never record the OAuth client secret in this
runbook or any other repository file.

Official reference: [Google Drive Python quickstart](https://developers.google.com/workspace/drive/api/quickstart/python).

## Stage 7 - Store the OAuth client outside the repository

In PowerShell:

```powershell
$secretRoot = Join-Path $env:LOCALAPPDATA 'TTS_gen\secrets'
New-Item -ItemType Directory -Force -Path $secretRoot
```

Move the downloaded OAuth JSON into that directory and rename it to:

```text
C:\Users\ricky\AppData\Local\TTS_gen\secrets\client_secret.json
```

Verify the file exists without printing its contents:

```powershell
Test-Path "$env:LOCALAPPDATA\TTS_gen\secrets\client_secret.json"
```

Expected: `True`.

Do not paste the JSON into chat, source code, `.env`, or a Git commit.

## Stage 8 - Complete the one-time OAuth authorization

Run:

```powershell
.\.venv\Scripts\python.exe .\google_drive_auth.py --setup-auth
```

What should happen:

1. The script opens a browser window.
2. Select the Google account listed as the OAuth test user.
3. If Google displays an unverified-app warning, verify that the displayed app
   and project are the ones you just created. For your own development project,
   Google documents the development path under **Advanced** in its
   [authentication troubleshooting guide](https://developers.google.com/workspace/drive/api/troubleshoot-authentication-authorization).
4. Review both requested Drive permissions carefully.
5. Approve only if you accept the broad `drive.readonly` access.
6. Return to PowerShell.

Expected terminal result:

```text
Authorization stored outside the repository; valid=True
```

Verify that the token exists without displaying it:

```powershell
Test-Path "$env:LOCALAPPDATA\TTS_gen\secrets\token.json"
```

Expected: `True`.

Verify noninteractive refresh/loading:

```powershell
.\.venv\Scripts\python.exe -c "from google_drive_auth import get_credentials; print(get_credentials().valid)"
```

Expected: `True`, with no browser prompt.

## Stage 9 - Create the Drive folder structure

In Google Drive, create:

```text
TTS_gen/
  Incoming/
  Finished Videos/
  Gemini Outputs/
```

For the first authored-timeline test, `Gemini Outputs` will remain empty, but
create it now so the configuration is complete.

For each of the three child folders:

1. Open the folder in Google Drive.
2. Copy its ID from the browser address. In a URL shaped like:

   ```text
   https://drive.google.com/drive/folders/1AbCdEf...
   ```

   the text after `/folders/` is the folder ID.
3. Record the IDs locally. Treat them as identifiers; do not publish them.

```text
Incoming folder ID:       ______________________________________
Finished Videos folder ID:______________________________________
Gemini Outputs folder ID: ______________________________________
```

Google's API represents folders as files with MIME type
`application/vnd.google-apps.folder` and uses parent folder IDs when creating
children: [Create and populate folders](https://developers.google.com/workspace/drive/api/guides/folder).

## Stage 10 - Set configuration for the current PowerShell test session

Replace the three placeholder strings below with the real folder IDs. Do not
include `<` or `>` characters.

```powershell
$env:DRIVE_INCOMING_FOLDER_ID = 'PASTE_INCOMING_ID'
$env:DRIVE_FINISHED_FOLDER_ID = 'PASTE_FINISHED_ID'
$env:DRIVE_GEMINI_OUTPUT_FOLDER_ID = 'PASTE_GEMINI_OUTPUT_ID'
$env:TTS_GEN_DB_PATH = 'work\tts_gen.db'
$env:ENABLE_GEMINI_PLANNING = 'false'
```

Confirm only that values are present, without printing the IDs:

```powershell
@(
  'DRIVE_INCOMING_FOLDER_ID',
  'DRIVE_FINISHED_FOLDER_ID',
  'DRIVE_GEMINI_OUTPUT_FOLDER_ID'
) | ForEach-Object {
  "$_ configured: $([bool](Get-Item "Env:$_" -ErrorAction SilentlyContinue))"
}
```

All three should report `True`.

These `$env:` values exist only in the current PowerShell window. Keep this
window open for Stages 11-15.

## Stage 11 - Run the empty-queue test

Make sure `Incoming` is empty, then run:

```powershell
.\.venv\Scripts\python.exe .\run_drive_queue.py --once
```

Expected output:

```text
no-work
```

Expected side effects:

- No MP4 is uploaded.
- No browser opens.
- The command exits normally.

If authorization is missing or expired, expect an `auth_attention` error rather
than an interactive login from the scheduled worker.

## Stage 12 - Prepare the first Drive test job

In Drive `Incoming`, create one folder named:

```text
tts-gen-smoke-test
```

Its final structure must be exactly:

```text
tts-gen-smoke-test/
  chapter.txt
  video-timeline.json
  images/
    BD-CH1-img-1.png
    BD-CH1-img-2.png
```

Use these already verified local files:

| Drive destination | Local source |
|---|---|
| `chapter.txt` | `C:\Users\ricky\Tools\TTS_gen\sample.txt` |
| `video-timeline.json` | `C:\Users\ricky\Tools\TTS_gen\work\manual-acceptance\video-timeline.json` |
| `images\BD-CH1-img-1.png` | `C:\Users\ricky\Tools\TTS_gen\Chapter1-imgs\BD-CH1-img-1.png` |
| `images\BD-CH1-img-2.png` | `C:\Users\ricky\Tools\TTS_gen\Chapter1-imgs\BD-CH1-img-2.png` |

Important:

- Rename the uploaded `sample.txt` to `chapter.txt` in Drive.
- Do not upload `narration.wav`, `full-chapter.mp4`, `state.json`, `job.log`, or
  the `qa` directory from the local acceptance workspace.
- Wait for all uploads to finish before running the worker.

## Stage 13 - Run the first real Drive job

In the same PowerShell window from Stage 10, run:

```powershell
.\.venv\Scripts\python.exe .\run_drive_queue.py --once
```

Expected final output:

```text
completed
```

The first run downloads a snapshot, synthesizes narration, renders a vertical
MP4, verifies it with FFprobe, uploads it, and records the result in SQLite. A
short job can still take several minutes depending on CPU and model cache.

Do not close the window while the worker is rendering.

## Stage 14 - Verify the completed job

### 14.1 Verify Drive output

Open `Finished Videos`. Confirm exactly one new file exists with a name similar
to:

```text
tts-gen-smoke-test-full-chapter.mp4
```

Confirm that it plays and has both picture and narration.

### 14.2 Verify local state

Run:

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('work/tts_gen.db'); db.row_factory=sqlite3.Row; rows=db.execute('select drive_folder_id,status,stage,attempts,output_ids,error_text from jobs order by id desc limit 5').fetchall(); [print(dict(r)) for r in rows]"
```

Expected latest row:

- `status` is `completed`.
- `stage` is `completed`.
- `attempts` is `0`.
- `output_ids` contains `full_chapter`.
- `error_text` is empty or `None`.

### 14.3 Verify the local workspace

```powershell
Get-ChildItem .\work -Directory
```

The Drive job should have an isolated directory whose name starts with the Drive
folder ID and ends with part of the fingerprint.

## Stage 15 - Test duplicate prevention

Without changing any Drive input, run the queue again:

```powershell
.\.venv\Scripts\python.exe .\run_drive_queue.py --once
```

Expected:

```text
no-work
```

Then reopen `Finished Videos` and confirm there is still exactly one copy of the
MP4. This is the minimum idempotency acceptance test.

## Stage 16 - Record the result

Record:

```text
Date/time:                       ______________________________
Google account used:             ______________________________
Cloud project:                   ______________________________
Empty queue returned no-work:    Yes / No
Drive job returned completed:    Yes / No
Output played successfully:      Yes / No
Second run returned no-work:     Yes / No
Exactly one output remained:     Yes / No
Notes/errors:                    ______________________________
```

Do not record or paste OAuth tokens, API keys, client secrets, or complete Drive
folder IDs in troubleshooting notes.

## Troubleshooting

### `install requirements-drive.txt`

Run Stage 2 again using the `.venv` Python, not system Python.

### `OAuth client file not found`

Confirm the exact path and filename:

```powershell
Get-Item "$env:LOCALAPPDATA\TTS_gen\secrets\client_secret.json"
```

### OAuth `access_denied` or test-user error

In **Google Auth Platform > Audience**, confirm that:

- Publishing status is Testing.
- The authorizing Google account is listed under Test users.
- You selected that same account during authorization.

### Token repeatedly expires after seven days

That is expected for an External app in Testing status. Before unattended
scheduling, move to In production and complete any verification Google requires
for the restricted `drive.readonly` scope, or accept a documented weekly
reauthorization process.

### `ffmpeg` or `ffprobe` not recognized

Open a new PowerShell window. Winget updated the user PATH, but already-running
processes do not receive the new value.

### `missing required environment variable`

Return to Stage 10 in the same PowerShell window. The program does not currently
load `.env` automatically.

### `Drive authorization needs attention`

Run Stage 8 interactively. Never run an interactive OAuth flow from Task
Scheduler.

### Upload fails with a parent or permission error

Confirm the Finished Videos folder ID is correct and belongs to the same Drive
account that authorized the OAuth client. Do not substitute the parent `TTS_gen`
folder ID.

### Timeline duration mismatch

Confirm that the Drive job uses the exact `sample.txt` and acceptance timeline
listed in Stage 12. Do not edit the test text or voice configuration before the
first successful test.

## After Phase 1 succeeds

Only after Stages 11-15 pass should you proceed with:

1. Persisting the three Drive folder IDs as user environment variables.
2. Performing the Gemini/Langflow quota feasibility spike.
3. Replacing the Langflow schema template with a real secret-free flow export.
4. Testing generated timelines and optional teasers.
5. Registering and validating Windows Task Scheduler.

Do not register the five-minute task before the manual Drive test succeeds. A
bad folder ID or expired Testing-mode token would otherwise fail repeatedly in
the background.
