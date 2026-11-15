import hashlib
import re
import tempfile
from pathlib import Path

import streamlit as st

from validated_audio import validate_and_save, cleanup_audio
from transcription import TranscriptionAdapter
from minutes_extractor import ActionItem, MinutesDraft
from minutes_editor import MinutesEditor

from app.extraction import extract_minutes
from app.export_minutes import export_minutes


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Meeting Audio to Structured Minutes",
    page_icon="🎙️",
    layout="wide",
)


# --------------------------------------------------
# Visual design system
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --ink: #18243a;
        --muted: #64748b;
        --brand: #5b5ce2;
        --brand-dark: #4445c7;
        --line: #e7eaf3;
        --surface: #ffffff;
        --soft: #f5f6ff;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp {
        background:
          radial-gradient(ellipse at 12% 0%, rgba(116,112,255,.10), transparent 34%),
          radial-gradient(ellipse at 95% 8%, rgba(53,194,190,.09), transparent 28%),
          #f7f8fc;
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(247,248,252,.82); }
    .block-container { max-width: 1180px; padding-top: 2.1rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--ink); letter-spacing: -.035em; }
    h1 { font-size: clamp(2rem, 4vw, 2.8rem) !important; font-weight: 800 !important; }
    h2 { font-size: 1.55rem !important; font-weight: 750 !important; }
    h3 { font-size: 1.12rem !important; font-weight: 700 !important; }
    p, label, .stMarkdown { color: var(--ink); }
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #f3f2ff 0%, #f0fbfb 100%);
        border: 1.5px dashed #aaaaf0;
        border-radius: 20px;
        padding: 1rem;
        transition: border-color .2s ease, transform .2s ease;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--brand); transform: translateY(-1px); }
    [data-testid="stFileUploader"] section { border: 0; }
    [data-testid="stFileUploader"] button {
        border-radius: 10px !important;
        border: 1px solid #d9dafa !important;
        background: white !important;
        color: var(--brand-dark) !important;
        font-weight: 700 !important;
    }
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        border-radius: 12px !important;
        min-height: 2.8rem;
        padding: .55rem 1.1rem !important;
        font-weight: 700 !important;
        border: 1px solid #dedff5 !important;
        box-shadow: 0 3px 10px rgba(34,43,90,.05);
        transition: all .18s ease;
    }
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(115deg, #6263e9, #7772f5) !important;
        color: white !important;
        border: 0 !important;
        box-shadow: 0 8px 18px rgba(91,92,226,.22);
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(34,43,90,.12);
        border-color: #aaaaf0 !important;
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
        border-radius: 12px !important;
        border: 1px solid #dfe3ef !important;
        background: #fff !important;
        line-height: 1.55;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: #7772f5 !important;
        box-shadow: 0 0 0 3px rgba(119,114,245,.12) !important;
    }
    [data-testid="stAlert"] { border-radius: 14px; border: 1px solid rgba(100,116,139,.12); }
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: white;
        overflow: hidden;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { gap: 1rem; }
    hr { border-color: var(--line) !important; margin: 1.6rem 0 !important; }
    .hero {
        position: relative; overflow: hidden;
        padding: 2rem 2.15rem; margin: .2rem 0 1.35rem;
        border-radius: 24px;
        color: white;
        background: linear-gradient(115deg, #4547bf 0%, #6665e8 58%, #8276f4 100%);
        box-shadow: 0 18px 38px rgba(79,78,196,.18);
    }
    .hero:after {
        content: ''; position: absolute; width: 260px; height: 260px;
        right: -65px; top: -115px; border-radius: 50%;
        border: 1px solid rgba(255,255,255,.23);
        box-shadow: 0 0 0 28px rgba(255,255,255,.05), 0 0 0 58px rgba(255,255,255,.04);
    }
    .hero-kicker { color: #dcdcff; text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 700; }
    .hero-title { color: white; font: 800 clamp(1.8rem,4vw,2.65rem) 'Manrope',sans-serif; letter-spacing: -.045em; margin: .45rem 0 .55rem; }
    .hero-copy { color: #eeedff; font-size: 1rem; max-width: 650px; margin: 0; line-height: 1.65; }
    .hero-pill { display: inline-block; margin-top: 1.15rem; padding: .38rem .75rem; border-radius: 999px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.2); color: white; font-size: .78rem; font-weight: 600; }
    .section-eyebrow { color: #7772d9; text-transform: uppercase; letter-spacing: .13em; font-size: .69rem; font-weight: 800; margin-bottom: .25rem; }
    .section-heading { font: 750 1.45rem 'Manrope',sans-serif; letter-spacing: -.035em; color: #202b43; margin: 0 0 .35rem; }
    .section-copy { color: #748097; margin: 0 0 1rem; font-size: .92rem; }
    .step-strip { display:flex; gap:.55rem; flex-wrap:wrap; margin: .5rem 0 1.5rem; }
    .step { display:flex; align-items:center; gap:.45rem; padding:.48rem .75rem; background:#fff; border:1px solid #e7e9f2; border-radius:999px; color:#64708a; font-size:.78rem; font-weight:650; }
    .step-num { display:grid; place-items:center; width:1.35rem; height:1.35rem; border-radius:50%; background:#eeedff; color:#5556d4; font-size:.72rem; font-weight:800; }
    .step.active { border-color:#c9c8ff; background:#f3f2ff; color:#4547bf; }
    .mini-note { color:#7a8499; font-size:.82rem; }
    @media (max-width: 700px) {
      .block-container { padding: 1rem 1rem 3rem; }
      .hero { padding: 1.5rem; border-radius: 18px; }
      .step { font-size:.72rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Your meeting, made actionable</div>
      <div class="hero-title">Turn conversations into clarity.</div>
      <p class="hero-copy">Transform meeting recordings into clear transcripts, decisions and action items — then refine everything before sharing.</p>
      <span class="hero-pill">✦ AI-assisted minutes · Human-reviewed · DOCX export</span>
    </div>
    <div class="step-strip">
      <div class="step active"><span class="step-num">1</span> Upload audio</div>
      <div class="step"><span class="step-num">2</span> Transcribe</div>
      <div class="step"><span class="step-num">3</span> Review minutes</div>
      <div class="step"><span class="step-num">4</span> Export</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-eyebrow">Start here</div>'
    '<div class="section-heading">Bring your meeting audio</div>'
    '<p class="section-copy">Upload a recording and we’ll guide you through validation, transcription and structured minutes.</p>',
    unsafe_allow_html=True,
)

st.info(
    "Supported formats: WAV, MP3, M4A · Maximum file size: 100 MB."
)


# --------------------------------------------------
# Session-state initialization
# --------------------------------------------------

if "validated_audio_path" not in st.session_state:
    st.session_state["validated_audio_path"] = None

if "validated_audio_name" not in st.session_state:
    st.session_state["validated_audio_name"] = None

if "validated_audio_signature" not in st.session_state:
    st.session_state["validated_audio_signature"] = None

if "minutes_draft" not in st.session_state:
    st.session_state["minutes_draft"] = None

if "validated_minutes" not in st.session_state:
    st.session_state["validated_minutes"] = None

if "minutes_review_flags" not in st.session_state:
    st.session_state["minutes_review_flags"] = []


def clear_minutes():
    """Clear results that belong to an earlier transcript."""
    st.session_state["minutes_draft"] = None
    st.session_state["validated_minutes"] = None
    st.session_state["minutes_review_flags"] = []


def remove_temporary_audio():
    """Delete the saved temporary audio file, if present."""
    audio_path = st.session_state.get("validated_audio_path")

    if audio_path:
        try:
            cleanup_audio(
                type(
                    "TemporaryAudio",
                    (),
                    {"path": audio_path},
                )()
            )
        except OSError:
            st.warning(
                "The temporary audio file could not be deleted. "
                "Please remove it manually if it remains on disk."
            )

    st.session_state["validated_audio_path"] = None
    st.session_state["validated_audio_name"] = None
    st.session_state["validated_audio_signature"] = None


def convert_extraction_to_draft(extraction):
    """
    Convert Priya's dictionary-based extraction result into the
    MinutesDraft/ActionItem structures used by the existing editor.
    """
    action_items = []

    for item in extraction.get("action_items", []):
        action_items.append(
            ActionItem(
                task=str(item.get("task") or "Not specified"),
                owner=str(item.get("owner") or "Not specified"),
                deadline=str(item.get("deadline") or "Not specified"),
            )
        )

    return MinutesDraft(
        topics=list(extraction.get("topics", [])),
        decisions=list(extraction.get("decisions", [])),
        action_items=action_items,
        review_flags=list(extraction.get("review_flags", [])),
    )


def validated_minutes_to_export_dict(validated):
    """Convert the editor's validated object to the export format."""
    return {
        "title": validated.title,
        "topics": validated.topics,
        "decisions": validated.decisions,
        "action_items": [
            {
                "task": item.task,
                "owner": item.owner,
                "deadline": item.deadline,
            }
            for item in validated.action_items
        ],
    }


# --------------------------------------------------
# Audio upload and validation
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload meeting audio",
    type=["wav", "mp3", "m4a"],
    help="Choose a WAV, MP3, or M4A recording up to 100 MB.",
    max_upload_size=100,
)

if uploaded_file is not None:
    st.write(f"**File:** {uploaded_file.name}")
    st.write(
        f"**Size:** {uploaded_file.size / (1024 * 1024):.2f} MB"
    )

    # Use filename, size and content digest to identify an upload.
    uploaded_file.seek(0)
    file_digest = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    uploaded_file.seek(0)

    current_signature = (
        uploaded_file.name,
        uploaded_file.size,
        file_digest,
    )

    previous_signature = st.session_state.get(
        "validated_audio_signature"
    )

    if (
        previous_signature is not None
        and previous_signature != current_signature
    ):
        remove_temporary_audio()
        st.session_state.pop("transcript", None)
        st.session_state.pop("transcription_status", None)
        clear_minutes()

    if st.button("Validate Audio", type="primary"):
        # Remove the previous temporary recording before replacing it.
        remove_temporary_audio()
        st.session_state.pop("transcript", None)
        st.session_state.pop("transcription_status", None)
        clear_minutes()

        try:
            uploaded_file.seek(0)
            result = validate_and_save(uploaded_file)

            if result.valid:
                st.session_state["validated_audio_path"] = result.path
                st.session_state["validated_audio_name"] = uploaded_file.name
                st.session_state["validated_audio_signature"] = (
                    current_signature
                )
                st.success(result.message)
            else:
                st.error(result.message)

        except Exception as exc:
            st.error(
                "Audio validation failed unexpectedly. "
                f"Details: {exc}"
            )

    # --------------------------------------------------
    # Transcription
    # --------------------------------------------------

    if st.button("Transcribe Audio"):
        audio_path = st.session_state.get("validated_audio_path")
        saved_signature = st.session_state.get(
            "validated_audio_signature"
        )

        if saved_signature != current_signature:
            st.warning(
                "The selected recording has changed. "
                "Please validate it again before transcription."
            )

        elif not audio_path or not Path(audio_path).is_file():
            st.warning(
                "Please validate the audio file before transcription."
            )

        else:
            clear_minutes()

            audio = type(
                "AudioForTranscription",
                (),
                {
                    "valid": True,
                    "path": audio_path,
                },
            )()

            try:
                with st.spinner(
                    "Loading the speech model and transcribing audio..."
                ):
                    adapter = TranscriptionAdapter()
                    result = adapter.transcribe(audio)

                st.session_state["transcript"] = result.text
                st.session_state["transcription_status"] = result.status

                if result.text.strip():
                    st.success(result.status)
                else:
                    st.warning(result.status)

            except Exception as exc:
                st.error(
                    "Transcription failed. Check the recording, "
                    "model installation, available memory, and "
                    "internet connection if the model is downloading. "
                    f"Details: {exc}"
                )

    # --------------------------------------------------
    # Transcript review
    # --------------------------------------------------

    if "transcript" in st.session_state:
        st.markdown(
            '<div class="section-eyebrow">Step 2 · Transcript</div>'
            '<div class="section-heading">Review your transcript</div>'
            '<p class="section-copy">Correct names, wording and details before generating the minutes.</p>',
            unsafe_allow_html=True,
        )

        edited_transcript = st.text_area(
            "Review and edit the transcript",
            value=st.session_state["transcript"],
            height=250,
            key="transcript_editor",
        )

        if edited_transcript != st.session_state["transcript"]:
            st.session_state["transcript"] = edited_transcript
            clear_minutes()

        if st.button("Generate Meeting Minutes"):
            clear_minutes()

            try:
                with st.spinner("Extracting meeting minutes..."):
                    extraction = extract_minutes(
                        st.session_state["transcript"]
                    )
                    draft = convert_extraction_to_draft(extraction)

                st.session_state["minutes_draft"] = draft
                st.session_state["minutes_review_flags"] = (
                    list(extraction.get("review_flags", []))
                )
                st.success("Draft meeting minutes generated.")

            except Exception as exc:
                st.error(
                    "Could not generate meeting minutes. "
                    "Please check the transcript and try again. "
                    f"Details: {exc}"
                )

    # --------------------------------------------------
    # Review and edit meeting minutes
    # --------------------------------------------------

    draft = st.session_state.get("minutes_draft")

    if draft is not None:
        st.markdown(
            '<div class="section-eyebrow">Step 3 · Minutes</div>'
            '<div class="section-heading">Shape the final meeting record</div>'
            '<p class="section-copy">Review topics, decisions and ownership. Edit anything that needs clarification.</p>',
            unsafe_allow_html=True,
        )

        review_flags = st.session_state.get(
            "minutes_review_flags",
            draft.review_flags,
        )

        if review_flags:
            with st.expander(
                "Items that may need your review",
                expanded=True,
            ):
                for flag in review_flags:
                    st.warning(flag)

        with st.form("minutes_form"):
            title = st.text_input(
                "Meeting title",
                value=st.session_state.get(
                    "meeting_title",
                    "Meeting Minutes",
                ),
            )

            topics_text = st.text_area(
                "Topics discussed (one per line)",
                value="\n".join(draft.topics),
            )

            decisions_text = st.text_area(
                "Decisions made (one per line)",
                value="\n".join(draft.decisions),
            )

            actions_text = st.text_area(
                "Action items (one per line; "
                "use Task | Owner: name | Deadline: date)",
                value="\n".join(
                    f"{item.task} | Owner: {item.owner} | "
                    f"Deadline: {item.deadline}"
                    for item in draft.action_items
                ),
            )

            submitted = st.form_submit_button("Save Edited Minutes")

        if submitted:
            action_items = []
            parsing_errors = []

            for line_number, line in enumerate(
                actions_text.splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue

                # Only treat a pipe followed by a recognized metadata label
                # as a separator. Other pipes remain part of the task text.
                metadata_match = re.search(
                    r"\s*\|\s*(?=Owner\s*:|Deadline\s*:)",
                    line,
                    flags=re.IGNORECASE,
                )

                if metadata_match:
                    task = line[:metadata_match.start()].strip()
                    metadata_text = line[metadata_match.start():]
                else:
                    task = line.strip()
                    metadata_text = ""

                if not task:
                    parsing_errors.append(
                        f"Action item on line {line_number} has no task."
                    )
                    continue

                owner = "Not specified"
                deadline = "Not specified"

                for part in re.split(r"\s*\|\s*", metadata_text):
                    part = part.strip()

                    if part.lower().startswith("owner:"):
                        owner = part.split(":", 1)[1].strip()

                    elif part.lower().startswith("deadline:"):
                        deadline = part.split(":", 1)[1].strip()

                action_items.append(
                    ActionItem(
                        task=task,
                        owner=owner or "Not specified",
                        deadline=deadline or "Not specified",
                    )
                )

            if parsing_errors:
                for error in parsing_errors:
                    st.error(error)
            else:
                edits = {
                    "title": title,
                    "topics": topics_text.splitlines(),
                    "decisions": decisions_text.splitlines(),
                    "action_items": action_items,
                }

                try:
                    validated = MinutesEditor.validate_and_update(
                        draft,
                        edits,
                    )

                    st.session_state["validated_minutes"] = validated
                    st.session_state["meeting_title"] = validated.title

                    # Refresh the draft so the editor displays the latest
                    # saved values on the next Streamlit rerun.
                    st.session_state["minutes_draft"] = MinutesDraft(
                        topics=list(validated.topics),
                        decisions=list(validated.decisions),
                        action_items=list(validated.action_items),
                        review_flags=list(draft.review_flags),
                    )
                    st.success("Your edited minutes have been saved.")

                except (ValueError, AttributeError, TypeError) as exc:
                    st.error(
                        "The edited minutes could not be saved. "
                        f"Check the fields and try again. Details: {exc}"
                    )

        # --------------------------------------------------
        # Word document export using Priya's exporter
        # --------------------------------------------------

        validated = st.session_state.get("validated_minutes")

        if validated is not None:
            st.markdown(
                '<div class="section-eyebrow">Step 4 · Export</div>'
                '<div class="section-heading">Your minutes are ready to share</div>'
                '<p class="section-copy">Download an editable Word document for your team.</p>',
                unsafe_allow_html=True,
            )

            try:
                export_data = validated_minutes_to_export_dict(validated)

                # Priya's exporter writes to a path, so use a temporary
                # directory and read the generated DOCX bytes for Streamlit.
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / "Meeting_Minutes.docx"

                    export_minutes(
                        export_data,
                        output_path,
                        file_format="docx",
                    )

                    document_bytes = output_path.read_bytes()

                st.download_button(
                    label="Download Minutes as Word Document",
                    data=document_bytes,
                    file_name="Meeting_Minutes.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    key="download_minutes_docx",
                )

            except Exception as exc:
                st.error(
                    "The Word document could not be generated. "
                    "Please save your edited minutes again and retry. "
                    f"Details: {exc}"
                )

else:
    # Clear any previous upload's data when the uploader is empty.
    if st.session_state.get("validated_audio_path"):
        remove_temporary_audio()

    st.session_state.pop("transcript", None)
    st.session_state.pop("transcription_status", None)
    clear_minutes()
