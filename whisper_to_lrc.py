import os
import sys
import shutil
import traceback
from pathlib import Path
import math
import time
import argparse
import whisper
import srt_to_lrc

# --- Constants and Path Definitions ---
TEMP_DIR_NAME = "temp_lrc_processing"
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.flac', '.ogg', '.opus', '.mkv', '.mp4'}

def format_srt_time(seconds: float) -> str:
    """Converts seconds to SRT time format HH:MM:SS,ms"""
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    seconds = milliseconds // 1_000
    milliseconds %= 1_000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt_content(transcription_result: dict) -> str:
    """Generates SRT file content string from Whisper transcription result."""
    srt_content = ""
    segment_count = 1
    for segment in transcription_result["segments"]:
        if 'words' in segment:
            for word in segment['words']:
                start_time_str = format_srt_time(word['start'])
                end_time_str = format_srt_time(word['end'])
                text = word['word'].strip()
                srt_content += f"{segment_count}\n"
                srt_content += f"{start_time_str} --> {end_time_str}\n"
                srt_content += f"{text}\n\n"
                segment_count += 1
        else: # Fallback to segment-level timestamps if word timestamps are not available
            start_time_str = format_srt_time(segment['start'])
            end_time_str = format_srt_time(segment['end'])
            text = segment['text'].strip()
            srt_content += f"{segment_count}\n"
            srt_content += f"{start_time_str} --> {end_time_str}\n"
            srt_content += f"{text}\n\n"
            segment_count += 1
    return srt_content

def main():
    parser = argparse.ArgumentParser(description="Generate LRC files for a single audio file using Whisper.")
    parser.add_argument("file_path", type=str, help="Path to the audio file.")
    parser.add_argument("--model", type=str, default="base", help="Whisper model to use (e.g., tiny, base, small, medium, large).")
    parser.add_argument("--language", type=str, default="auto", help="Language of the audio file (e.g., en, ja, auto).")
    parser.add_argument("--word_timestamps", action="store_true", help="Enable word-level timestamps.")
    args = parser.parse_args()

    audio_file = Path(args.file_path)
    model_name = args.model
    language = args.language if args.language and args.language.lower() != 'auto' else None
    word_timestamps = args.word_timestamps

    if not audio_file.is_file():
        print(f"Error: File not found at {audio_file}")
        sys.exit(1)

    if audio_file.suffix.lower() not in AUDIO_EXTENSIONS:
        print(f"Error: Unsupported file type. Supported extensions are: {', '.join(AUDIO_EXTENSIONS)}")
        sys.exit(1)

    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg not found. Please install ffmpeg and ensure it is in your PATH.")
        sys.exit(1)

    try:
        print(f"Loading Whisper model: {model_name}...")
        model = whisper.load_model(model_name)
        print(f"Model '{model_name}' loaded.")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        sys.exit(1)

    temp_dir_path = audio_file.parent / TEMP_DIR_NAME
    temp_dir_path.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {audio_file.name}")
    expected_srt_file_path = temp_dir_path / (audio_file.stem + '.srt')
    generated_lrc_path = None

    try:
        transcribe_options = {
            "language": language,
            "word_timestamps": word_timestamps,
            "beam_size": 5,
            "fp16": False,
        }
        result = model.transcribe(str(audio_file), **transcribe_options, verbose=False)

        srt_data = generate_srt_content(result)
        if not srt_data:
            print(f"Warning: Whisper produced no output for {audio_file.name}")
            # No need to continue, will go to finally block for cleanup
        else:
            with open(expected_srt_file_path, 'w', encoding='utf-8') as srt_f:
                srt_f.write(srt_data)

            if expected_srt_file_path.exists():
                generated_lrc_path = srt_to_lrc.srt_to_lrc(expected_srt_file_path)

                if generated_lrc_path and generated_lrc_path.exists():
                    target_lrc_path = audio_file.with_suffix('.lrc')
                    shutil.move(str(generated_lrc_path), str(target_lrc_path))
                    print(f"Successfully generated LRC file: {target_lrc_path}")
                else:
                    print(f"Error: LRC file not generated for {audio_file.name}")

    except Exception as e:
        print(f"Error processing {audio_file.name}: {e}")
        traceback.print_exc()
    finally:
        if expected_srt_file_path.exists():
            try:
                expected_srt_file_path.unlink()
            except OSError:
                pass
        if generated_lrc_path and generated_lrc_path.exists():
            try:
                generated_lrc_path.unlink()
            except OSError:
                pass
        if temp_dir_path.exists():
            try:
                shutil.rmtree(temp_dir_path)
            except Exception as e:
                print(f"Warning: Failed to delete temp directory {temp_dir_path}: {e}")

    print("Processing finished.")

if __name__ == "__main__":
    main()
