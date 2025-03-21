import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import openai

# Set your OpenAI API key
OPENAI_API_KEY = "..."
openai.api_key = OPENAI_API_KEY

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Flashcards")
        
        # Upload Page
        self.upload_frame = tk.Frame(root)
        self.upload_label = tk.Label(self.upload_frame, text="Upload a PDF to generate flashcards")
        self.upload_label.pack(pady=10)
        self.upload_btn = tk.Button(self.upload_frame, text="Upload PDF", command=self.upload_pdf)
        self.upload_btn.pack(pady=5)
        self.upload_frame.pack(expand=True)

        # Flashcard Page
        self.flashcard_frame = tk.Frame(root)
        self.flashcard_text = tk.Text(self.flashcard_frame, wrap="word", height=15, width=50)
        self.flashcard_text.pack(pady=10)
        self.quiz_btn = tk.Button(self.flashcard_frame, text="Start Quiz", command=self.start_quiz)
        self.quiz_btn.pack(pady=5)

        self.flashcards = []
        self.quiz_index = 0

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            extracted_text = self.extract_text_from_pdf(file_path)
            self.flashcards = self.generate_flashcards(extracted_text)

            if self.flashcards:
                self.show_flashcards()
            else:
                messagebox.showwarning("Warning", "No flashcards generated!")

    def extract_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return text

    def generate_flashcards(self, text):
        prompt = f"Generate Quizlet-style flashcards as Q&A pairs and definitions from the following text:\n{text}\n\nFlashcards:"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            flashcards_text = response["choices"][0]["message"]["content"].strip()
            return [tuple(card.split(" - ")) for card in flashcards_text.split("\n") if " - " in card]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate flashcards: {e}")
            return []

    def show_flashcards(self):
        self.upload_frame.pack_forget()  # Hide upload page
        self.flashcard_frame.pack(expand=True)  # Show flashcard page
        self.flashcard_text.delete("1.0", tk.END)
        for q, a in self.flashcards:
            self.flashcard_text.insert(tk.END, f"Q: {q}\nA: {a}\n\n")

    def start_quiz(self):
        self.quiz_index = 0
        self.show_question()

    def show_question(self):
        if self.quiz_index < len(self.flashcards):
            q, _ = self.flashcards[self.quiz_index]
            answer = tk.simpledialog.askstring("Quiz", f"Q: {q}")
            self.check_answer(answer)
        else:
            messagebox.showinfo("Quiz Complete", "You've completed the quiz!")

    def check_answer(self, answer):
        correct_answer = self.flashcards[self.quiz_index][1]
        if answer and answer.strip().lower() == correct_answer.lower():
            messagebox.showinfo("Correct!", "That's right!")
        else:
            messagebox.showinfo("Incorrect", f"Correct Answer: {correct_answer}")
        self.quiz_index += 1
        self.show_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
