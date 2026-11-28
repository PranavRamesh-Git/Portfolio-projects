# BOOKWORM — Book Discovery & Reading Tracker

BOOKWORM is a full-stack web application built with **Flask, React, and PostgreSQL** that allows users to discover books through the Google Books API, maintain a personal library, and track their reading progress.

The project started with a Flask and vanilla JavaScript frontend, which was later migrated to React. The backend uses REST APIs, session-based authentication, and PostgreSQL for managing users, books, and reading activity.

## Features

**Book Discovery**
- Search for books by title or author using the Google Books API.
- Sort results by relevance or publication date.
- View book covers, authors, publication details, and descriptions.
- Add books to a personal library and identify previously saved books.

**Personal Library**
- View and manage saved books.
- Track reading progress using statuses such as *On Reading List*, *Currently Reading*, *Finished*, *Dropped*, and *Rereading*.
- Update reading statuses and remove books without reloading the page.
- Maintain separate libraries and reading statuses for individual users.

**Authentication & Security**
- User registration and login with password hashing.
- Flask session-based authentication and protected API endpoints.
- CSRF protection using Flask-WTF.
- Request rate limiting using Flask-Limiter, with Redis for storing rate-limit counters.
- Input validation and API error handling.

## Tech Stack

- **Backend:** Python, Flask, psycopg 3
- **Frontend:** React, JavaScript, HTML, CSS, Vite
- **Database:** PostgreSQL
- **API Integration:** Google Books API
- **Security:** Flask-WTF, Flask-Limiter, Werkzeug
- **Rate-Limit Storage:** Redis
- **Testing:** pytest, Flask test client
- **Tools:** Git, GitHub

## Backend & Database

The Flask backend exposes REST endpoints for book discovery, library management, and reading-status updates. External book information is retrieved through the Google Books API, while user-specific data is stored in PostgreSQL.

The database consists of three primary tables:

| Table | Purpose |
|---|---|
| `users` | Stores user accounts and authentication details |
| `books` | Stores book metadata retrieved from Google Books |
| `user_books` | Maps users to saved books and maintains their reading statuses |

The schema uses primary and foreign keys, unique constraints, and check constraints to maintain data integrity. SQL views are used to retrieve library details, and database operations are performed using parameterized queries with psycopg 3.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/discover` | Search books through Google Books |
| POST | `/api/discover/addtoMybooks` | Add a book to the user's library |
| GET | `/api/mybooks` | Retrieve saved books |
| POST | `/api/mybooks/remove` | Remove a saved book |
| PATCH | `/api/mybooks/status_change` | Update reading status |
| GET | `/api/get-csrf` | Retrieve a CSRF token |

Authentication and registration are handled through separate Flask routes.

## Frontend

The frontend was migrated from vanilla JavaScript to React, replacing manual DOM manipulation with reusable components and state-driven rendering.

The React application uses `useState` and `useEffect` for managing data, API requests, and UI state. Search filters, reading-status dropdowns, book cards, and summary modals are handled through controlled inputs and component props.

The production React build is served directly by Flask, allowing the frontend and backend to run under the same application origin.

## Testing

Backend tests are written using **pytest** and Flask's test client.

The test suite includes tests for login, book discovery, library operations, and rate limiting.

Run the tests using:

```bash
python -m pytest tests/ -v
```

## Running Locally

**Prerequisites:** Python, Node.js, PostgreSQL, and Redis.

**1. Clone the repository**

```bash
git clone https://github.com/PranavRamesh-Git/Practice_Projects.git
cd Practice_Projects/BOOKWORM
```

**2. Set up the Python environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Configure environment variables**

Create a `.env` file using `.env_example` as a reference. Configure the PostgreSQL connection, Flask secret key, Google Books API key, and Redis connection.

For Redis running locally:

```env
RATELIMIT_STORAGE_URI=redis://localhost:6379/0
```

**4. Initialize the database**

Create the PostgreSQL database and execute the SQL statements in `schema`.

**5. Build the React frontend**

```bash
cd frontend
npm ci
npm run build
cd ..
```

**6. Start Flask**

```bash
python app.py
```

Open `http://127.0.0.1:5000/bookworm/login` in your browser.

## Project Structure

```text
BOOKWORM/
├── app.py
├── db.py
├── rate_limiting.py
├── schema
├── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── BookCard.jsx
│   │   │   ├── MyBookCard.jsx
│   │   │   └── Modal.jsx
│   │   ├── pages/
│   │   │   ├── Discover.jsx
│   │   │   └── MyBooks.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── templates/
├── static/
└── tests/
    ├── conftest.py
    ├── test_login.py
    ├── test_discoverBooks.py
    ├── test_myBooks.py
    └── test_rateLimits.py
```

## Future Improvements

- Dockerize the application and deploy it to AWS.
- Introduce caching for frequently repeated book searches.
- Add automated frontend tests and CI/CD workflows.
