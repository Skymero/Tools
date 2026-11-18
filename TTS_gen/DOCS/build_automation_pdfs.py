"""Regenerate the five maintained TTS_gen PDF guides from committed text."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parent
styles = getSampleStyleSheet()
TITLE = ParagraphStyle("TitleNavy", parent=styles["Title"], textColor=colors.HexColor("#152b45"), fontSize=24, leading=28)
H1 = ParagraphStyle("H1Navy", parent=styles["Heading1"], textColor=colors.HexColor("#152b45"), fontSize=17)
H2 = ParagraphStyle("H2Blue", parent=styles["Heading2"], textColor=colors.HexColor("#176b87"), fontSize=12)
BODY = ParagraphStyle("BodyClean", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=7)
CODE = ParagraphStyle("CodeClean", parent=styles["Code"], fontName="Courier", fontSize=7.4, leading=9.4,
                      backColor=colors.HexColor("#eef5f7"), borderPadding=7, spaceAfter=9)
NOTE = ParagraphStyle("Note", parent=BODY, backColor=colors.HexColor("#fff4d6"), borderPadding=7)


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 7); canvas.setFillColor(colors.HexColor("#667788"))
    canvas.drawString(.65*inch, .4*inch, "TTS_gen - generated from committed source")
    canvas.drawRightString(7.85*inch, .4*inch, f"Page {doc.page}"); canvas.restoreState()


def deterministic_canvas(*args, **kwargs):
    kwargs["invariant"] = 1
    return Canvas(*args, **kwargs)


def build(filename, title, subtitle, sections):
    story = [Paragraph(title, TITLE), Paragraph(subtitle, H2), Spacer(1, 12)]
    for heading, blocks in sections:
        if heading == "PAGEBREAK": story.append(PageBreak()); continue
        story.append(Paragraph(heading, H1))
        for kind, value in blocks:
            if kind == "p": story.append(Paragraph(value, BODY))
            elif kind == "note": story.append(Paragraph(value, NOTE))
            elif kind == "h2": story.append(Paragraph(value, H2))
            elif kind == "code": story.append(Preformatted(value.strip(), CODE))
            elif kind == "table":
                table = Table(value, repeatRows=1, colWidths=[1.55*inch, 4.95*inch])
                table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#152b45")),
                                           ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                                           ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#9fb3c0")),("VALIGN",(0,0),(-1,-1),"TOP"),
                                           ("FONTSIZE",(0,0),(-1,-1),8),("LEADING",(0,0),(-1,-1),10),
                                           ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f6f8")])]))
                story += [table, Spacer(1, 9)]
    doc = SimpleDocTemplate(str(ROOT/filename), pagesize=letter, rightMargin=.65*inch, leftMargin=.65*inch,
                            topMargin=.65*inch, bottomMargin=.65*inch, title=title)
    doc.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=deterministic_canvas)


def main():
    build("TTS_gen_Technical_Guide.pdf", "TTS_gen Technical Guide", "Current implementation and manual acceptance boundaries - 2026-11-17", [
      ("System status", [("table", [["Area","Status"],["Kokoro narration","Implemented; stdlib tests pass"],["Strict validation and state","Implemented"],["Local/Drive workers","Implemented; real service acceptance pending"],["Gemini/Langflow","Opt-in implementation; feasibility spike pending"],["Task Scheduler","Scripts implemented; registration pending"],["FFmpeg/FFprobe","Required but not on this account's PATH"]])]),
      ("Architecture", [("p","The scheduled control plane is <b>run_drive_queue.py --once</b>. It selects at most one eligible Drive folder, creates an immutable local snapshot, calls <b>render_chapter.py --job-dir</b>, verifies media, and uploads with a stable Drive ID. The local worker never scans queues."),("code",(ROOT/"mermaid/chapter-workflow.mmd").read_text())]),
      ("Trust boundaries", [("p","Kokoro runs locally. Drive OAuth grants drive.readonly for configured input queries and drive.file for app-created outputs. Gemini/Langflow egress requires ENABLE_GEMINI_PLANNING=true plus explicit credentials. Public platform upload remains manual."),("note","Never commit OAuth client JSON, refresh tokens, API keys, raw manuscripts, or unredacted provider responses. Unit tests do not contact external services.")]),
      ("PAGEBREAK", []),
      ("Data and validation contracts", [("p","Job identity is SHA-256 over sorted Drive ID, modified time, checksum, and size tuples. Remote metadata is checked after snapshotting. Authored timelines reject unknown fields, path traversal, missing images, invalid motion, non-finite numbers, gaps, overlaps, and duration drift above one 30 fps frame."),("code",(ROOT/"mermaid/job-state.mmd").read_text())]),
      ("Operations", [("code","python -m unittest discover -s tests -p \"test_*.py\" -v\npython render_chapter.py --job-dir work\\example\npython run_drive_queue.py --once\n.\\DOCS\\task-status.ps1"),("p","Failures retain artifacts. Requeue requires a RETRY marker. The queue enforces a process lock and maximum attempts; Task Scheduler must also use Do not start a new instance.")]),
      ("Verification ladder", [("p","Automated evidence: imports, unit behavior, durable transitions, validation, and fake transport paths. Manual evidence still required: FFmpeg install, short and full local render, OAuth consent, real Drive snapshot/upload, Gemini/Langflow spike, scheduled-account execution, and playback/editorial review.")])])

    build("TTS_gen_Chapter_Video_Workflow.pdf", "Chapter-to-video workflow", "Implemented flow with optional later phases", [
      ("One job per run", [("code",(ROOT/"mermaid/chapter-workflow.mmd").read_text()),("p","Phase 0 accepts an authored timeline. Phase 2 can generate a timeline only when both job metadata and ENABLE_GEMINI_PLANNING explicitly opt in. Phase 3 teaser rendering requires teaser text and its own strict timeline.")]),
      ("Acceptance", [("p","A job completes only after FFprobe confirms one H.264 video stream, one AAC audio stream, configured dimensions/fps, positive size and duration, and stream agreement. Public upload is manual."),("note","Current machine status: FFmpeg and FFprobe are not on PATH, so a real render remains a manual prerequisite.")])])

    build("TTS_gen_Windows_Task_Scheduler_Setup.pdf", "Windows Task Scheduler", "Register only after a manual Drive end-to-end pass", [
      ("Preflight", [("code","ffmpeg -version\nffprobe -version\n.\\.venv\\Scripts\\python.exe -c \"import kokoro, soundfile\"\n.\\.venv\\Scripts\\python.exe .\\run_drive_queue.py --once"),("p","Run these checks as the same Windows account that will own the task. That account needs network access and read access to %LOCALAPPDATA%\\TTS_gen\\secrets.")]),
      ("Registration", [("code",".\\DOCS\\register-task.ps1\n.\\DOCS\\task-status.ps1\n.\\DOCS\\unregister-task.ps1"),("p","The script uses an absolute virtual-environment Python path, run_drive_queue.py --once, the project working directory, a five-minute repetition, and IgnoreNew overlap behavior.")]),
      ("Manual validation", [("p","Verify: empty queue; one real Drive job; two jobs across two runs; upload retry without rerender; auth_attention; quota_hold; overlap suppression; LastTaskResult; retained logs and artifacts."),("note","This guide does not claim the task is registered. Registration changes Windows state and remains an explicit operator action.")])])

    build("TTS_gen_Google_Drive_Video_Workflow.pdf", "Google Drive video workflow", "Implemented transport; real OAuth and endpoint acceptance pending", [
      ("Queue flow", [("code",(ROOT/"mermaid/drive-workflow.mmd").read_text()),("p","Input folders are ordered by modified time and ID. Completed, exhausted, or failed-without-RETRY versions are skipped so they cannot starve newer work.")]),
      ("Snapshot and identity", [("p","The fingerprint uses sorted ID, modifiedTime, checksum, and size. Native Docs export to plain text; blank-line paragraph boundaries are normalized. Metadata is fetched again before the snapshot becomes ready.")]),
      ("OAuth and retries", [("p","Interactive setup stores the refresh token outside the repository. Scheduled refresh never opens a browser; failure becomes auth_attention. Output IDs are generated and stored before upload, then queried before retry. Existing IDs are updated rather than duplicated."),("note","A production OAuth consent screen is required for durable unattended use. Testing-mode refresh tokens can expire after seven days.")]),
      ("Configuration", [("code","DRIVE_INCOMING_FOLDER_ID\nDRIVE_FINISHED_FOLDER_ID\nDRIVE_GEMINI_OUTPUT_FOLDER_ID\nGOOGLE_OAUTH_CLIENT_FILE\nGOOGLE_OAUTH_TOKEN_FILE")])])

    build("TTS_gen_Gemini_API_and_Langflow_Setup.pdf", "Gemini API and Langflow setup", "Optional Phase 2 - disabled until a real redacted feasibility spike", [
      ("Gated planner", [("code",(ROOT/"mermaid/gemini-workflow.mmd").read_text()),("p","countTokens estimates the complete numbered prose and artwork inventory. SQLite checks and reserves in one immediate transaction. Limits come from configuration; no historical provider value is compiled into code.")]),
      ("Langflow contract", [("p","The client posts to /api/v1/run/{flow_id}, saves raw bytes before parsing, finds the structured scenes object, and validates exact paragraph coverage, artwork IDs, motion, and intensity. The flow ID and prompt SHA-256 are stored with the plan."),("note","DOCS/langflow-flow.json is a schema template, not a claimed real export. Replace it with a secret-free export after the manual spike.")]),
      ("Usage caveats", [("p","The 80 percent threshold is local policy only. The ledger cannot see unrelated project traffic. Usage metadata availability through Langflow is not assumed. Phase 2 must remain disabled until DOCS/spikes records current RPM/TPM/RPD limits, countTokens behavior, actual usage metadata, and the reconciliation approach.")]),
      ("Configuration", [("code","ENABLE_GEMINI_PLANNING=true\nGEMINI_MODEL=<current accepted model>\nGEMINI_API_KEY=<secret>\nGEMINI_TPM_LIMIT=<dashboard value>\nLANGFLOW_BASE_URL=http://127.0.0.1:7860\nLANGFLOW_FLOW_ID=<flow id>\nLANGFLOW_API_KEY=<secret>")])])


if __name__ == "__main__": main()
