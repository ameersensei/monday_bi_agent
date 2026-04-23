##create session
curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
 https://us-central1-aiplatform.googleapis.com/v1/projects/my-project-test-489116/locations/us-central1/reasoningEngines/883496075824988160:query \
-d '{"class_method": "create_session", "input":{"user_id": "u_123"}}'

##get session id

##query
curl \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
 https://us-central1-aiplatform.googleapis.com/v1/projects/my-project-test-489116/locations/us-central1/reasoningEngines/883496075824988160:streamQuery?alt=sse -d '{
  "class_method": "async_stream_query",
  "input": {
    "user_id": "USER_ID",
    "session_id": "SESSION_ID",
    "message": "give me details of my workspace",
  }
}'
