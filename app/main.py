from fastapi import FastAPI

app = FastAPI()

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

@app.get("/users")
def get_users():
    return users

@app.get("/users_count")
def get_users_count():
    return {"count": len(users)}
