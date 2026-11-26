STUDENT360 — Student Management & Academic Analytics Dashboard
STUDENT360 is a full-stack student information and academic performance dashboard built with Python, Flask, PostgreSQL, React, JavaScript, HTML, and CSS. It enables authenticated teachers to explore student records for their assigned sections and analyze academic performance across grades and sections.

The application combines a Flask REST-style API, PostgreSQL queries and views, and a React frontend for interactive search, student profiles, marksheets, and academic analytics.
Key Features
Student Profiles & Marksheets
- Teacher login with password verification and Flask session-based authentication.
- Section-based authorization: teachers can access student profiles only for their assigned sections.
- Student search and class filtering with responsive React components.
- Student profile details displayed in an interactive modal.
- Student marksheets with assessment scores, subject-level results, and aggregate performance information.
Academic Analytics
- Grade-wide academic performance overview across all sections.
- Section-specific performance analytics for individual classes.
- Highest, lowest, and average performance statistics.
- Subject-wise performance breakdowns and ranked student lists.
- School-wide analytics access for authenticated teachers, independent of their assigned profile sections.
Security & Reliability
- Password hashing and verification using Werkzeug.
- Flask session management and server-side authorization checks.
- CSRF protection for form submissions and React POST requests using Flask-WTF.
- JSON API error responses and client-side loading/error states.
- Automated API testing with pytest, including class-access and analytics tests.
Tech Stack
Layer	Technologies
Backend	Python, Flask
Frontend	React, JavaScript, Vite, HTML, CSS
Database	PostgreSQL, psycopg 3, SQL, views
Authentication & Security	Flask sessions, Werkzeug password hashing, Flask-WTF CSRF
Testing	pytest, Flask test client
Version Control	Git, GitHub

##OUTPUT SCREENSHOTS

## Screenshots
<img width="2048" height="1164" alt="image" src="https://github.com/user-attachments/assets/9d166c94-75e0-4492-9e87-6d53e6c8c50b" />

<img width="2048" height="1180" alt="image" src="https://github.com/user-attachments/assets/45197705-fdb6-451a-b457-ea120746bfbc" />

<img width="2048" height="1160" alt="image" src="https://github.com/user-attachments/assets/638568fc-876f-439c-9214-cade1231e5de" />

<img width="2048" height="1167" alt="image" src="https://github.com/user-attachments/assets/a40bfadb-f7df-4f4e-8328-92d8b7c248ea" />


<img width="2064" height="1160" alt="image" src="https://github.com/user-attachments/assets/2b609acf-767d-4a3e-9728-7244be52d21f" />

<img width="2048" height="1213" alt="image" src="https://github.com/user-attachments/assets/0a30ce3f-b75a-496b-ae14-f63198bcab6b" />

<img width="2048" height="1332" alt="image" src="https://github.com/user-attachments/assets/ef0b89b3-1347-4502-9d6a-f1e9a4b8ea8f" />

<img width="2048" height="1167" alt="image" src="https://github.com/user-attachments/assets/19adab47-1d5e-4322-8f0a-6dc90f9aa7b6" />































