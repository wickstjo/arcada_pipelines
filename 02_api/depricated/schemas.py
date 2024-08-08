from pydantic import BaseModel

class submission(BaseModel):
    user: str
    exercise: int
    solution: str

class graded(BaseModel):
    hash: str
    user: str
    exercise: int
    evaluation: bool

class cache(BaseModel):
    keyword: str

class user_submissions(BaseModel):
    user: str

class solo_exercise(BaseModel):
    exercise_id: int