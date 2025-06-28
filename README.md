# FastAPI Application

This is a basic FastAPI application demonstrating a simple API with Pydantic for data validation.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```

The API documentation will be available at `http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/redoc` (ReDoc) after running the application.

## Endpoints

*   **GET /**: Returns a welcome message.
*   **POST /items/**: Creates a new item.
    *   **Request Body Example:**
        ```json
        {
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2
        }