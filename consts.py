DATA_DIR = 'static/'
CHROMA_PATH = 'chroma/'
PDF_PATH = 'pdf/'
AUDIO_PATH = 'wav/'
SCORE_THRESH = 60

QUESTION_PROMPT = (
    """
    Given an academic lecture in PDF format (5-10 pages long) provided by the student, generate diverse and in-depth questions to evaluate a university student's understanding in preparation for their final exam. The lecture delves moderately into applications and theories. Follow these guidelines:
    1. Extract 4-5 broad learning goals that comprehensively cover the content of the lecture.
    2. For each learning goal, generate 1-2 very simple questions (Using simple language like a 5 year old) suitable for a  student to introduce the learning goal. These questions should be easy enough for anyone to understand.
    3. For each learning goal, generate 2-3 complex, short-answer questions to thoroughly test the student's understanding of the goal.
    Additionally, make sure your reply ONLY with json and that you follow the following json format EXACTLY.\n'
    {
      "learning_goals": [
        {
          "goal name": [
            {
              "Introductory Questions": ["q1", "q2"]
            },
            {
              "Complex Questions": ["q3", "q4", "q5"]
            }
          ]
        },
        {
          "goal name": [
            {
              "Introductory Questions": ["q1", "q2"]
            },
            {
              "Complex Questions": ["q3", "q4", "q5"]
            }
          ]
        },
        {
          "goal name": [
            {
              "Introductory Questions": ["q1", "q2"]
            },
            {
              "Complex Questions": ["q3", "q4", "q5"]
            }
          ]
        },
        {
          "goal name": [
            {
              "Introductory Questions": ["q1", "q2"]
            },
            {
              "Complex Questions": ["q3", "q4", "q5"]
            }
          ]
        }
      ]
    }
    """
)

ANSWER_PROMPT = """
Assess the answer to the question below based only on the following context:

{context}

---

Assess the answer to this question based on the above context: 

{question}

--
Assess this answer to the question above concisely and in simple english. Avoid repeating the answer and question in your answer:

{answer}

"""

ANSWER_PROMPT2 = """
Assess the answer to the question below and calculate a correctness score (0-100) based only on the following context:

{context}

---

Assess the answer to this question and calculate a correctness score (0-100) based on the above context: 

{question}

--
Assess this answer to the question above AND calculate a correctness score (0-100). Return only a single number as the score and nothing else.

{answer}

"""