class TextProcessor:
    def __init__(self, wake_word="jarvis"):
        self.wake_word = wake_word.lower()

    def split_questions(self, text):
        """Split text into questions based on wake word"""
        # Convert to lowercase for case-insensitive matching
        text = text.lower()
        # Split on wake word and filter empty strings
        questions = [q.strip() for q in text.split(self.wake_word) if q.strip()]
        return questions

    def format_qa_pair(self, question, answer):
        """Format a Q&A pair for saving"""
        return f"Q: {question}\nA: {answer}\n\n" 