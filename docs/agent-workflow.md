# EIT Learning Agent Workflow

The **EIT Learning Agent** executes a controlled 7-step pedagogical pipeline implemented in Python (`app/agents/workflow.py`).

---

## The 7-Step Workflow

```
[ User Request / Question ]
           │
           ▼
[ Step 1: Request Understanding ]
    Validates request_type and response_mode against policy allowlist.
           │
           ▼
[ Step 2: Context Retrieval ]
    Invokes approved Python tools ONLY:
    - get_lesson_tool()
    - get_topic_tool()
    - get_conversation_tool()
    - get_progress_tool()
           │
           ▼
[ Step 3: Learning-Support Analysis ]
    Combines student intent with lesson metadata.
    Sanitizes optional expression signals (labeled as uncertain).
           │
           ▼
[ Step 4: Tutor Response Generation ]
    Constructs role-specific prompt and calls OpenAI API (max 30s timeout).
           │
           ▼
[ Step 5: Verification ]
    Validates non-empty, well-formed response within educational scope.
           │
           ▼
[ Step 6: Persistence ]
    Appends user and assistant messages to MongoDB conversations collection.
           │
           ▼
[ Step 7: Response Delivery ]
    Returns structured JSON with response text and metadata envelope.
```

---

## Pedagogical Teaching Modes

1. **`simple`**: Plain-English explanation avoiding heavy jargon.
2. **`step_by_step`**: Numbered, sequential breakdown of the concept.
3. **`example`**: Concrete real-world analogy.
4. **`programming`**: Working code snippet with syntax highlighting and explanation.
5. **`quiz`**: Multiple-choice practice question without immediately revealing the answer.
6. **`feedback`**: Constructive review of the student's submitted answer.
7. **`summary`**: Bulleted list of key takeaways.
8. **`revision`**: Concise flashcard review questions.
