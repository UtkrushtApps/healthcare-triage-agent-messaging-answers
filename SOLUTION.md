# Solution Steps

1. Change the POST /agent/message handler to accept the raw request body instead of relying on FastAPI dict validation, parse JSON safely, and fall back to an empty message if parsing fails so malformed inputs never crash the endpoint.

2. Update AgentMessage.from_payload so only JSON objects are treated as message envelopes; non-object JSON values become an empty raw dict for deterministic validation.

3. Add AgentMessage.first_missing_required_field(), iterating through sender, receiver, conversation_id, performative, and payload in that exact order and returning the first absent or null field.

4. In TriageCoordinator.handle_message, run required-field validation before any Redis write. If a field is missing, log a rejected-message warning and return status 400 with {"error": "invalid agent message: <field>"}.

5. Build the patient note only after validation succeeds, preserving sender, receiver, conversation_id, performative, and payload.

6. Replace non-idempotent Redis list appends with save_note_once(conversation_id, performative, note), where the idempotency identity is exactly the conversation_id + performative pair.

7. Implement RedisStore.save_note_once with a deterministic hashed idempotency key and a Redis Lua script that atomically checks whether the key exists, sets it if new, and appends the note to the notes list only for the first valid message.

8. Return 200 {"status": "stored"} when save_note_once writes the note for the first time, and log an accepted-message info event including sender, receiver, conversation_id, and performative.

9. Return 200 {"status": "duplicate_ignored"} when save_note_once detects a replay, do not append another note, and log an ignored-message info event with the same observability fields.

10. Catch unexpected storage or coordinator errors, log them with stack traces, and return a stable 500 response rather than allowing the endpoint to crash.

