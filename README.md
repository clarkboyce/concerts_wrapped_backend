# concerts_wrapped_backend

## Backend Stack

- Flask: Backend Framework
- GraphQL: Database querying and
- MariaDB: Database Management
- Docker: Application Containerization

---

### Flask

The first question I had about creating this flask backend was how should i
organize the folders and functions.

**Functions**

I need to create functions to read

1. Get User Concert
   - Get Concert Based on Concert Name, Artist, Date, etc...
2. Add User Concert
3. Update User Concert
4. Delete User Concert
5. Delete Concert
6. Create Concert

**Concert Statistics**

This one is still up in the air clark wants to do it on the client side however
I feel like It might be better to store the statistics before hand well see

---

### GraphQL

**Revolvers**

### MariaDB

**Tables**

1. UsersConcert

- Columns
  - id
  - userId
  - concertId
  - time stamp

2. Concerts

- Columns
  - id
  - Artist
  - Genres
  - Date
  - Venue
  - City
  - State
  - Capacity
  - Number of Songs
