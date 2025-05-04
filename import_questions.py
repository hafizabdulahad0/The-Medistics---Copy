import sys
import pandas as pd
from database import get_db_connection, init_db

def import_questions(file_path):
    init_db()  # ensure tables exist
    try:
        if file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    required_cols = ["Question", "Option1", "Option2", "Option3", "Option4", "Correct Option", "Explanation", "Subject"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Column '{col}' not found in the file.")
            return
    conn = get_db_connection()
    cur = conn.cursor()
    count = 0
    for _, row in df.iterrows():
        question_text = str(row["Question"]).strip()
        if not question_text:
            continue
        option1 = str(row["Option1"])
        option2 = str(row["Option2"])
        option3 = str(row["Option3"])
        option4 = str(row["Option4"])
        correct = row["Correct Option"]
        # Determine correct_option index (1-4)
        if isinstance(correct, str):
            correct_str = correct.strip()
            if correct_str.upper() in ['A', 'B', 'C', 'D']:
                correct_option = ['A', 'B', 'C', 'D'].index(correct_str.upper()) + 1
            else:
                if correct_str == option1:
                    correct_option = 1
                elif correct_str == option2:
                    correct_option = 2
                elif correct_str == option3:
                    correct_option = 3
                elif correct_str == option4:
                    correct_option = 4
                else:
                    try:
                        correct_option = int(correct_str)
                    except:
                        continue
        else:
            try:
                correct_option = int(correct)
            except:
                continue
        if correct_option not in (1, 2, 3, 4):
            continue
        explanation = str(row["Explanation"])
        subject = str(row["Subject"]).strip()
        # Insert question into the database
        cur.execute(
            """INSERT INTO questions 
               (subject, question_text, option1, option2, option3, option4, correct_option, explanation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (subject, question_text, option1, option2, option3, option4, correct_option, explanation)
        )
        count += 1
    conn.commit()
    conn.close()
    print(f"Imported {count} questions.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_questions.py <questions_file.xlsx/csv>")
        sys.exit(1)
    import_questions(sys.argv[1])
