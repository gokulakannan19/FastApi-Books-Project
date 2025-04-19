from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from typing import Optional


app = FastAPI()


class Book:
    id: Optional[int]
    title : str
    author: str
    description: str
    rating: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="Id is not needed on create")
    title: str = Field(min_length=3, max_length=20)
    author: str = Field(min_length=3, max_length=20)
    description: str = Field(min_length=3, max_length=100)
    rating: int = Field(lt=6, gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
            "title": "goks",
            "author": "gokulakannan",
            "description": "test",
            "rating": 5
        }}
    }


BOOKS = [
    Book(1, "Title1", "Author1", "Description", 5),
    Book(2, "Title2", "Author2", "Description", 4),
    Book(3, "Title3", "Author2", "Description", 3),
    Book(4, "Title4", "Author4", "Description", 2),
    Book(5, "Title5", "Author3", "Description", 5),
]
    

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/", status_code=status.HTTP_200_OK)
async def filter_book(
    author: Optional[str] = Query(default=None, min_length=1, max_length=10),
    rating: Optional[int] = Query(default=None, gt=0, lt=6),
    title: Optional[str] = Query(default=None, min_length=1, max_length=10)
    ):
    
    books_to_return = BOOKS

    if author:
        books_to_return = [
            book for book in books_to_return
            if book.author.casefold() == author.casefold()
        ]
    if rating:
        books_to_return = [
            book for book in books_to_return
            if book.rating == rating
        ]
    if title:
        books_to_return = [
            book for book in books_to_return
            if book.title.casefold() == title.casefold()
        ]

    return books_to_return


@app.get("/books/Mybook", status_code=status.HTTP_200_OK)
async def read_favourite_book():
    return BOOKS[0]


@app.get("/books/{title}", status_code=status.HTTP_200_OK)
async def read_book(
    title: str = Path(min_length=3, max_length=20)):
    for book in BOOKS:
        if book.title.casefold() == title.casefold():
            return book


@app.post("/books/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    new_book.id = get_new_id(BOOKS)
    BOOKS.append(new_book)


def get_new_id(books: list):
    if len(books) > 0:
        return BOOKS[len(books)-1].id + 1
    return 1


@app.put("/books/update-book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    is_book_found = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            is_book_found = True
            BOOKS[i] = book
    if not is_book_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book id not found0")
    


@app.delete("/books/delete-book", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    is_book_found = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            is_book_found = True
            break
    if not is_book_found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book id not found0")
