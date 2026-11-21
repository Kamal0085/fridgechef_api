# FridgeChef API (Assignment 2)

ADA University, CSCI 3509 Intro to Software Engineering, Fall 2026, Group 17

FridgeChef helps users keep track of the ingredients in their pantry so they can plan meals and waste less food. This repository contains the first prototype of the backend: a REST API for pantry ingredients that uses mock data instead of a database.

## Requirements

Python 3.10 or newer.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn main:app --reload
```

The server runs at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/api/v1/greeting` in a browser to see the project page.

## Mock users

| User | Token | Permissions |
|---|---|---|
| User A | `user-a-token` | Own ingredients only |
| User B | `user-b-token` | Own ingredients only |
| Admin | `admin-token` | All ingredients |

Send the token in the header: `Authorization: Bearer user-a-token`

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/ingredients` | List ingredients |
| GET | `/api/v1/ingredients/{id}` | Get one ingredient |
| POST | `/api/v1/ingredients` | Create an ingredient |
| PUT | `/api/v1/ingredients/{id}` | Update an ingredient |
| DELETE | `/api/v1/ingredients/{id}` | Delete an ingredient |
| GET | `/api/v1/greeting` | HTML project page |

Full documentation is in `API_DOCS.md`. Example requests are in `requests.http` (VS Code REST Client extension).

## Mock data

The data is kept in memory and **resets every time the server restarts**. At startup User A owns `ingredient_1` and `ingredient_2`, User B owns `ingredient_3` and `ingredient_4`, and the admin can access all of them. `ingredient_999` does not exist and can be used to show a 404 response.

## Team and contributions

| Member | Student ID | Worked on |
|---|---|---|
| Ismayil Aliyev | ialiyev23021 | Ingredient CRUD endpoints and mock data |
| Kamal Hasanov | khasanov15271 | Authentication, role checks and error handling |
| Ahmad Taghiyev | ataghiyev15190 | Input validation, greeting page and API documentation |

Output of `git shortlog -sn --all`:

```
    10  KamalHasanov15271
     9  Ahmad
     9  ialiyev230217
```

## Demo video

YouTube: https://youtu.be/_CXT7avJ9TY
