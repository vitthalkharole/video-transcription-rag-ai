
import traceback
from sqlalchemy.orm import Session

from backend.services.vectore_store import build_vector_store
from backend.models.video_model import Video
from backend.services.audio_processor import process_input
from backend.services.transcriber import transcribe_all
from backend.services.summarize import summarize, generate_title
from backend.services.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)


def process_video(
    db: Session,
    source_url: str,
    user_id: int,  # CHANGE 1: Accept authenticated user's ID
    language: str = "english"
):
    print("\n========== VIDEO PROCESSING STARTED ==========")
    print(f"Source URL: {source_url}")
    print(f"Language: {language}")
    print(f"User ID: {user_id}")

    # Step 1: Create and save video record
    try:
        video = Video(
            source_url=source_url,
            user_id=user_id,  # CHANGE 2: Associate video with its owner
            status="pending"
        )

        db.add(video)
        db.commit()
        db.refresh(video)

        print(f"[SUCCESS] Video record created. ID: {video.id}")

    except Exception as e:
        db.rollback()
        print("[ERROR] Failed to create video record")
        print(f"Error: {e}")
        traceback.print_exc()
        raise

    try:
        video.status = "processing"
        db.commit()
        print("[SUCCESS] Status updated to processing")

        # Step 2: Download and split audio
        print("\n[STEP 2] Downloading and splitting audio...")
        chunks = process_input(source_url)
        print(f"[SUCCESS] Audio processed. Chunks: {len(chunks)}")

        # Step 3: Generate transcript
        print("\n[STEP 3] Transcribing audio...")
        transcript = transcribe_all(
            chunks,
            language=language
        )

        print("[SUCCESS] Transcription completed")
        print(f"Transcript length: {len(transcript)} characters")

        # Step 4: Store transcript vectors in ChromaDB
        print("\n[STEP 4] Creating text chunks and storing vectors...")

        if not transcript or not transcript.strip():
            raise ValueError(
                "Transcript is empty. Cannot create text chunks."
            )

        build_vector_store(
            video_id=video.id,
            transcript=transcript,
            source_url=source_url
        )

        print("[SUCCESS] Transcript chunks stored in ChromaDB")

        # Step 5: Generate title and summary
        print("\n[STEP 5] Generating title...")
        title = generate_title(transcript)
        print(f"[SUCCESS] Title: {title}")

        print("\n[STEP 6] Generating summary...")
        summary = summarize(transcript)
        print("[SUCCESS] Summary generated")

        # Step 6: Extract meeting information
        print("\n[STEP 7] Extracting action items...")
        action_items = extract_action_items(transcript)
        print("[SUCCESS] Action items extracted")

        print("\n[STEP 8] Extracting key decisions...")
        key_decisions = extract_key_decisions(transcript)
        print("[SUCCESS] Key decisions extracted")

        print("\n[STEP 9] Extracting open questions...")
        open_questions = extract_questions(transcript)
        print("[SUCCESS] Open questions extracted")

        # Step 7: Save results to MySQL
        print("\n[STEP 10] Saving results to database...")

        video.title = title
        video.transcript = transcript
        video.summary = summary
        video.action_items = action_items
        video.key_decisions = key_decisions
        video.open_questions = open_questions
        video.status = "completed"

        db.commit()
        db.refresh(video)

        print("[SUCCESS] Video processing completed")
        print(f"Video ID: {video.id}")
        print(f"Owner ID: {video.user_id}")
        print(f"Final status: {video.status}")
        print("===============================================\n")

        return video

    except Exception as e:
        print("\n========== VIDEO PROCESSING FAILED ==========")
        print(f"Video ID: {video.id}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        traceback.print_exc()

        db.rollback()

        # Mark the existing record as failed
        try:
            failed_video = (
                db.query(Video)
                .filter(Video.id == video.id)
                .first()
            )

            if failed_video:
                failed_video.status = "failed"
                db.commit()
                print("[INFO] Video status updated to failed")

        except Exception:
            db.rollback()
            print("[ERROR] Could not update video status")
            traceback.print_exc()

        raise
