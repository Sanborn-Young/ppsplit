import spacy
import re
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import numpy as np
import threading
from typing import List

def format_timestamp(seconds: float) -> str:
    """
    Convert seconds (float) into an [HH:MM] timestamp string.
    For example, 300 seconds becomes "[00:05]".
    """
    minutes, _ = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"[{int(hours):02d}:{int(minutes):02d}]"

# Load optimized spaCy model with required components.
nlp = spacy.load("en_core_web_md", disable=["ner", "lemmatizer"])
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer", first=True)

def process_large_text(text: str, progress_callback=None) -> str:
    """Split text into paragraphs using semantic and structural analysis."""
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    
    if not sentences:
        return ""
    
    # Process in batches for memory efficiency.
    batch_size = 50
    vectors = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i+batch_size]
        vectors.extend([nlp(sent).vector for sent in batch])
        if progress_callback:
            progress_callback(i/len(sentences))
    
    vectors = np.array(vectors)
    norms = np.linalg.norm(vectors, axis=1)
    
    paragraphs = []
    current_para = [sentences[0]]
    prev_vectors = [vectors[0]]
    
    # Enhanced paragraph splitting parameters.
    threshold = 0.65  # More sensitive similarity threshold.
    max_sentences = 4  # Maximum sentences per paragraph.
    window_size = 2    # Compare with fewer previous sentences.
    
    for i in range(1, len(sentences)):
        current_vec = vectors[i]
        
        # Calculate similarities with the window.
        similarities = []
        for v in prev_vectors[-window_size:]:
            sim = np.dot(v, current_vec) / (norms[i] * np.linalg.norm(v))
            similarities.append(sim)
        avg_similarity = np.mean(similarities) if similarities else 0
        
        # Break conditions.
        break_conditions = (
            avg_similarity < threshold,
            len(current_para) >= max_sentences,
        )
        
        if any(break_conditions):
            paragraphs.append(" ".join(current_para))
            current_para = [sentences[i]]
            prev_vectors = [current_vec]
        else:
            current_para.append(sentences[i])
            prev_vectors.append(current_vec)
        
        # Maintain the window size.
        prev_vectors = prev_vectors[-window_size:]
    
    if current_para:
        paragraphs.append(" ".join(current_para))
    
    return "\n\n".join(paragraphs)

class ProcessingThread(threading.Thread):
    def __init__(self, content, callback):
        super().__init__()
        self.content = content
        self.callback = callback

    def run(self):
        try:
            processed = process_large_text(
                self.content,
                progress_callback=lambda p: self.callback("progress", p)
            )
            self.callback("success", processed)
        except Exception as e:
            self.callback("error", str(e))

def process_file():
    file_path = filedialog.askopenfilename(
        title="Select Text File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        initialdir=Path.home()
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(400000)  # Read up to 400k characters
        
        progress_bar.start()
        status_label.config(text="Processing...", fg="black")
        
        def update_status(status_type, value):
            if status_type == "progress":
                root.after(0, update_progress, value)
            elif status_type == "success":
                root.after(0, lambda: save_result(value, file_path))
            elif status_type == "error":
                root.after(0, lambda: show_error(value))
        
        thread = ProcessingThread(content, update_status)
        thread.start()
        
    except Exception as e:
        show_error(str(e))

def save_result(processed, file_path):
    try:
        # Use regex to insert two newlines before and after any "[xx:xx]" pattern.
        processed = re.sub(r'(\[\d{2}:\d{2}\])', r'\n\n\1\n\n', processed)
        
        original_path = Path(file_path)
        new_path = original_path.with_name(f"{original_path.stem}_pp{original_path.suffix}")
        
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(processed)
            
        status_label.config(
            text=f"Processed {len(processed)} characters\nSaved as: {new_path.name}",
            fg="darkgreen"
        )
    except Exception as e:
        show_error(str(e))
    finally:
        progress_bar.stop()

def update_progress(value):
    progress_bar['value'] = value * 100

def show_error(message):
    progress_bar.stop()
    status_label.config(text=f"Error: {message}", fg="red")

# GUI Setup
root = tk.Tk()
root.title("Text Paragraph Processor Pro")
root.geometry("500x300")

style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TButton", font=('Arial', 10), padding=6)
style.configure("TProgressbar", thickness=20)

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(
    main_frame,
    text="Advanced Text Paragraph Splitter",
    font=('Arial', 14, 'bold'),
    foreground="#2c3e50"
)
header.pack(pady=10)

select_btn = ttk.Button(
    main_frame,
    text="📁 Select Text File",
    command=process_file
)
select_btn.pack(pady=10)

progress_bar = ttk.Progressbar(
    main_frame,
    orient='horizontal',
    mode='indeterminate',
    length=300
)
progress_bar.pack(pady=10)

status_label = tk.Label(
    main_frame,
    text="Ready to process files up to 400,000 characters",
    wraplength=400,
    justify="center",
    fg="#7f8c8d",
    bg="#f0f0f0"
)
status_label.pack(pady=10)

root.mainloop()
