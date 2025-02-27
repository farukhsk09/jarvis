from src.audio_processor import AudioProcessor
from src.text_processor import TextProcessor
from src.file_handler import FileHandler
from src.llm_handler import LLMHandler
import time
from pathlib import Path
import logging
from config_local import WAKE_WORD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('resources/output/jarvis.log')
    ]
)
logger = logging.getLogger(__name__)

def chunk_text(text, chunk_size=1000):
    """Split text into chunks at sentence boundaries"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += 1
        
        # If we hit a sentence end or chunk size
        if word.endswith(('.', '!', '?')) and current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    # Add any remaining words
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def process_audio_file(audio_file):
    # Initialize components
    audio_proc = AudioProcessor('resources/input', 'resources/output', 'resources/temp')
    text_proc = TextProcessor(WAKE_WORD)
    file_handler = FileHandler('resources/output')
    llm_handler = LLMHandler()

    # Transcribe audio
    logger.info(f"Starting to process audio file: {audio_file}")
    transcribed_text = audio_proc.transcribe_audio(audio_file)
    
    if not transcribed_text:
        logger.warning(f"No transcription available for {audio_file}")
        return

    # Check if wake word is present
    if WAKE_WORD.lower() not in transcribed_text.lower():
        logger.info(f"Wake word '{WAKE_WORD}' not found in audio file {audio_file}. Skipping processing.")
        return

    # Split into questions
    questions = text_proc.split_questions(transcribed_text)
    if not questions:
        logger.info(f"No valid questions found in {audio_file}")
        return

    qa_pairs = []
    logger.info(f"Found {len(questions)} questions in the audio")

    # Process each question
    for i, question in enumerate(questions, 1):
        logger.info(f"Processing question {i}/{len(questions)}: {question}")
        
        # Get LLM response
        logger.info("Generating response from LLM...")
        response = llm_handler.generate_response(question)
        
        if response:
            # Format and save Q&A pair
            qa_pair = text_proc.format_qa_pair(question, response)
            qa_pairs.append(qa_pair)

    if qa_pairs:
        # Generate timestamp for this conversation
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save conversation text
        text_filename = f"conversation_{timestamp}.md"
        file_handler.save_qa_text(qa_pairs, text_filename)

        # Format audio text with proper spacing and punctuation
        audio_parts = []
        for q, a in zip(questions, [pair.split('\n')[1][3:] for pair in qa_pairs]):
            audio_parts.extend([
                "Question:",
                q.strip() + ".",  # Ensure question ends with period
                "Answer:",
                a.strip() + "."   # Ensure answer ends with period
            ])
        
        full_audio_text = " ".join(audio_parts)
        logger.info(f"Total response length: {len(full_audio_text.split())} words")
        
        # Split into chunks if necessary
        chunks = chunk_text(full_audio_text)
        
        # Process each chunk and keep track of audio files
        audio_files = []
        for chunk_idx, chunk in enumerate(chunks, 1):
            chunk_filename = f"qa_session_{timestamp}_part{chunk_idx}.mp3"
            audio_path = file_handler.get_audio_path(chunk_filename)
            logger.info(f"Converting chunk {chunk_idx}/{len(chunks)} to speech ({len(chunk.split())} words)")
            audio_proc.text_to_speech(chunk, str(audio_path))
            audio_files.append(chunk_filename)
        
        # Save metadata for this conversation
        file_handler.save_conversation_metadata(
            original_audio=audio_file,
            qa_pairs=qa_pairs,
            audio_files=audio_files,
            timestamp=timestamp
        )
        
        logger.info(f"Completed processing {audio_file} - Generated {len(chunks)} audio files")
        logger.info(f"Conversation saved in resources/output/text/{text_filename}")
        logger.info(f"Audio files saved in resources/output/audio/")

def main():
    # Create required directories
    for dir_path in ['resources/input', 'resources/output/text', 'resources/output/audio', 'resources/temp']:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    input_dir = Path('resources/input')
    logger.info(f"Watching for audio files in: {input_dir}")
    
    # Process all audio files in input directory
    audio_files = list(input_dir.glob('*.m4a'))
    logger.info(f"Found {len(audio_files)} .m4a files to process")
    
    for audio_file in audio_files:
        logger.info(f"Processing audio file: {audio_file.name}")
        process_audio_file(audio_file.name)

if __name__ == "__main__":
    main() 