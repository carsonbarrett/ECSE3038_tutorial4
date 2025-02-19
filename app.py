from fastapi import FastAPI, HTTPException
import motor.motor_asyncio
from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated, List
from bson import ObjectId

app = FastAPI()

connection = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://lecture4CB:Lecture4aswellCB@cluster0.1vt5y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
people_db = connection.people

PyObjectId = Annotated[str, BeforeValidator(str)]

class Person(BaseModel):
    id: PyObjectId | None = Field(default=None, alias = "_id")
    name:str
    occupation: str
    address: str

class PersonCollection(BaseModel):
    persons: List[Person]
  
class PersonUpdate(BaseModel):
    name: str | None = None
    occupation: str | None = None
    address: str | None = None

@app.post("/person")
async def create_person(person_request: Person):
    person_dictionary = person_request.model_dump()

    created_person = await people_db["group"].insert_one(person_dictionary)

    person = await people_db["group"].find_one({"_id": created_person.inserted_id})

    return Person(**person)

@app.get("/person")
async def get_person():
    person_collection = await people_db["group"].find().to_list(999)
    return PersonCollection(persons=person_collection)

@app.patch("/person/{_id}")
async def update_person(_id: str, person_update: PersonUpdate):

   try:
        objectId = ObjectId(_id)
   except: 
        raise HTTPException(status_code=400, content = "Invalid ID")

   update_data = person_update.model_dump(exclude_none=True)

   result = await people_db["group"].update_one({"_id": ObjectId(_id)}, {"$set": update_data})

   return{"That's correct": "This person was updated"}

@app.delete("/person/{_id}")
async def delete_person(_id: str):
    try:
        objectId = ObjectId(_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID Invaled")

    result = await people_db["group"].delete_one({"_id": objectId})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="He is not here")

    return {"That's correct": "This person was deleted"}
