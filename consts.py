DATA_DIR = 'static/'
CHROMA_PATH = 'chroma/'
PDF_PATH = 'pdf/'
AUDIO_PATH = 'wav/'


QUESTION_PROMPT = ('Given the following input text, generate diverse and in-depth questions to test a university '
          'student\'s knowledge and understanding of a given document of text,'
          'approximately 25 pages long. Follow these steps:  1. Identify 5-6 broader '
          'learning goals that comprehensively cover all the major topics in the text. 2. For each learning goal: '
          '    a. Create 2-3 simple and introductory questions.     b. Develop 3-5 harder and more complex '
          'questions to thoroughly test the student\'s understanding through qualitative analysis and factual '
          'knowledge. 3. Ensure the questions are short to medium length answer format. 4. Segment the document '
          'by topics to ensure comprehensive coverage. 5. Make sure the learning goals encompass the entire '
          'content of the text, aiming at university difficulty level for students aged 19-23. Additionally, '
          'make sure your reply ONLY with json and that you follow the following json format EXACTLY.\n'
              '''{
                  "learning goals": [
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
                ''')