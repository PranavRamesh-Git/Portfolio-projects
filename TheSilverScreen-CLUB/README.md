The Silver Screen Club — Movie & TV Discovery, Tracking and Social Recommendations
The Silver Screen Club is a full-stack movie and TV tracking application built using Python, Flask, PostgreSQL, SQLAlchemy, Redis, JavaScript, HTML, and CSS. It enables users to discover entertainment content, manage personal libraries, connect with other users, and exchange recommendations, with an emphasis on backend API development, relational data modelling, and secure session-based workflows.
Key Features
Movie & TV Discovery
- Discover movies and TV shows using the TMDB API.
- Browse trending titles and search or filter discovery results with pagination.
- View content information and add titles to personal libraries.
Personal Library & Social Features
- User registration, password hashing, session-based login, and profile management.
- Separate movie and TV libraries with watch-status updates and removal options.
- Search for other users and view their profiles.
- Send, accept, and decline connection requests with notifications.
- Send movie and TV recommendations to connections and view sent and received recommendations.
Tech Stack
- Backend: Python, Flask, Flask Blueprints, SQLAlchemy
- Database: PostgreSQL, Flask-Migrate, Alembic
- Frontend: HTML, CSS, JavaScript, Jinja2
- External API: TMDB API
- Caching & Rate Limiting: Redis, Flask-Caching, Flask-Limiter
- Security: Session authentication, password hashing, CSRF protection, request validation
- Testing: pytest, Flask test client, unittest.mock
  
Technical Highlights
The Silver Screen Club separates authentication, content discovery, library management, social connections, and recommendations into modular Flask Blueprints, using SQLAlchemy models and PostgreSQL migrations to manage relational data and user-specific workflows.

Redis-backed caching reduces repeated TMDB API requests for identical discovery parameters, while Redis-backed rate limiting helps control excessive authentication and recommendation requests. User-specific library information is handled separately from cached public content.

Built to demonstrate practical Python backend engineering, third-party API integration, session security, relational database design, HTTP API development, and automated testing.
