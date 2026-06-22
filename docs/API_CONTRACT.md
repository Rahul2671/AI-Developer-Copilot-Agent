## Upload API

POST /upload

Input:
zip file


Response:

{
project_id,
status
}



## Chat API

POST /chat

Body:

{
project_id,
question
}


Response:

{
answer,
sources
}