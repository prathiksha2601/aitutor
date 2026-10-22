# MongoDB Database Schema Reference

The EIT platform uses **MongoDB 8.0** with BSON documents, `ObjectId` primary keys, and consistent UTC timestamps.

---

## Collections Overview

### 1. `users`
Stores student accounts.
```json
{
  "_id": "ObjectId",
  "email": "student@example.com",
  "password_hash": "$argon2id$v=19$m=19456,t=2,p=1$...",
  "display_name": "Student",
  "role": "student",
  "status": "active",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: Unique index on `email`.

---

### 2. `topics`
Core computer science disciplines.
```json
{
  "_id": "ObjectId",
  "title": "Java Fundamentals",
  "description": "Learn syntax, OOP, and data types in Java.",
  "category": "programming",
  "is_active": true,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: Compound index on `(is_active, category)`.

---

### 3. `lessons`
Individual video learning units.
```json
{
  "_id": "ObjectId",
  "topic_id": "ObjectId (ref: topics)",
  "title": "Variables and Data Types",
  "description": "Primitive types and variable declaration.",
  "video_url": "https://www.youtube.com/embed/...",
  "video_type": "youtube",
  "duration_seconds": 720,
  "sequence_number": 2,
  "is_published": true,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: Compound index on `(topic_id, is_published, sequence_number)`.

---

### 4. `learning_sessions`
Active and past student learning sessions.
```json
{
  "_id": "ObjectId",
  "user_id": "string (authenticated user_id or anonymous UUID)",
  "owner_id": "string (identical to user_id for lookup compatibility)",
  "topic_id": "ObjectId string",
  "lesson_id": "ObjectId string",
  "started_at": "ISODate",
  "ended_at": "ISODate",
  "last_position_seconds": 142.5,
  "status": "active",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: Index on `user_id`, index on `owner_id`.

---

### 5. `progress`
Verified learning progress and video playback positions.
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "lesson_id": "string",
  "topic_id": "string",
  "last_position_seconds": 320.0,
  "completion_status": "in_progress",
  "progress_updated_at": "ISODate"
}
```
**Indexes**: Unique compound index on `(user_id, lesson_id, topic_id)`.

---

### 6. `conversations`
Tutor message exchanges for multi-turn context.
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "owner_id": "string",
  "topic_id": "string",
  "messages": [
    {
      "role": "user",
      "content": "Can you give me an example of polymorphism?",
      "created_at": "ISODate"
    },
    {
      "role": "assistant",
      "content": "Consider a Shape base class with a draw() method...",
      "response_mode": "example",
      "created_at": "ISODate"
    }
  ],
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**: Compound index on `(session_id, owner_id)`.

---

### 7. `quiz_attempts`
Records of student quiz answers and AI feedback.
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "owner_id": "string",
  "topic_id": "string",
  "lesson_id": "string",
  "question": "What is the time complexity of quicksort?",
  "submitted_answer": "O(n log n) average, O(n^2) worst case",
  "feedback": "Correct! You accurately identified both cases.",
  "created_at": "ISODate"
}
```

---

### 8. `expression_summaries`
Persisted ONLY when explicit consent is provided.
```json
{
  "_id": "ObjectId",
  "session_id": "string",
  "owner_id": "string",
  "observation_window_start": "ISODate",
  "observation_window_end": "ISODate",
  "aggregated_category_counts": { "neutral": 6, "happy": 2 },
  "quality_metadata": { "resolution": "224x224" },
  "model_version": "1.0.0",
  "created_at": "ISODate",
  "expires_at": "ISODate"
}
```
**Indexes**: TTL index on `expires_at` (automatic deletion after 7 days).
