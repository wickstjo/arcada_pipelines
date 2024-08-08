from fastapi import FastAPI, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import utils.websocket as websocket

# INITIALIZE COMPONENTS
app = FastAPI()
API_PORT = 3003

# CREATE A WEBSOCKET MANAGER
socket_manager = websocket.create_socket_manager()

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FETCH ALL EXERCISES
@app.get('/exercises')
def all(response: Response):

    dataset = db_client.read(
        query='SELECT * FROM exercises',
        schema=db_client.exercise_schema
    )
    
    return respond(200, dataset, response)

# FETCH ALL EXERCISES
@app.post('/exercise')
def all(input: schemas.solo_exercise, response: Response):

    dataset = db_client.read(
        query=f"SELECT * FROM exercises WHERE ID = '{input.exercise_id}'",
        schema=db_client.exercise_schema
    )
    
    return respond(200, dataset, response)

# FETCH ALL SUBMISSIONS
@app.post('/submissions')
def all(input: schemas.user_submissions, response: Response):

    dataset = db_client.read(
        query=f"SELECT * FROM submissions WHERE USERSESH = '{input.user}'",
        schema=db_client.submission_schema
    )
    
    return respond(200, dataset, response)

# FETCH CACHE VALUE
@app.post('/cache')
def cache_query(input: schemas.cache, response: Response):

    # FETCH CACHE VALUE
    success, content = cache.read(input.keyword)

    # VALUE EXISTS
    if success:
        return respond(200, {
            'success': True,
            'data': content
        }, response)

    return respond(200, {
        'success': False,
    }, response)

# SUBMIT SOLUTION FOR GRADING
@app.post('/submit')
def submit(input: schemas.submission, response: Response):

    # HASH THE SUBMISSION & CHECK CACHE FOR HITS
    submission_hash = misc.hash_dict({
        'solution': input.solution,
        'exercise': input.exercise
    })

    # CHECK IF THE HASH IS CACHED
    cache_exists = cache.check(submission_hash)

    # CACHE MISS
    if not cache_exists:
        print(f'{submission_hash} -- CACHE MISS')

        # PUSH GRADER JOB TO KAFKA
        grader_producer.push({
            'topic': 'grading_jobs',
            'message': {
                **input.__dict__,
                'hash': submission_hash
            }
        })

        # UPDATE CACHE WITH PENDING ANSWER
        cache.write(submission_hash, {
            'status': 'pending',
            'correct': False
        })

    # CACHE HIT
    else:
        print(f'{submission_hash} -- CACHE HIT')

        # PUSH SUBMISSION TO DB
        db_client.write(
            query='INSERT INTO submissions (USERSESH, EXERCISE, CORRECT) VALUES (%s, %s, %s)',
            values=(input.user, input.exercise, True)
        )

    # RESPOND
    return respond(201, {
        'hash': submission_hash,
    }, response)

# SUBMIT SOLUTION FOR GRADING
@app.post('/graded')
async def graded(input: schemas.graded, response: Response):
    
    # UPDATE CACHE
    cache.write(input.hash, {
        'status': 'graded',
        'correct': input.evaluation
    })

    # ADD SUBMISSION TO DB
    db_client.write(
        query='INSERT INTO submissions (USERSESH, EXERCISE, CORRECT) VALUES (%s, %s, %s)',
        values=(input.user, input.exercise, True)
    )

    # PUSH MESSAGE TO WEBSOCKETS, THEN REMOVE CONNECTIONS
    await socket_manager.publish(input.hash, input.__dict__)
    await socket_manager.remove(input.hash)

    # RESPOND
    return respond(201, {}, response)

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):

    # OPEN SOCKET CONNECTION
    await websocket.accept()

    # WAIT FOR HASH INTEREST
    try:
        submission_hash = await websocket.receive_text()
        await socket_manager.add(submission_hash, websocket)
        await websocket.receive_text()
    
    # RESOLVE EXCEPTIONS SILENTLY
    except:
        # print('WS EXCEPT TRIGGERED')
        pass

# RESPONSE WRAPPER
def respond(status, content, response):
    response.status_code = status
    return content

# LAUNCH SERVER
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=API_PORT, 
        log_level="info", 
        reload=True,
        # workers=NUM
    )