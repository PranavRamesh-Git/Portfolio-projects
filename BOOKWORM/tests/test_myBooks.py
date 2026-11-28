def test_myBooks(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1


    response = client.get('/api/mybooks')
    data = response.get_json()

    assert response.status_code == 200
    google_book_ids = []
    for book in data["mybooks"]:
        google_book_ids.append(book["google_book_id"])

    assert google_book_ids == ["hxL2qWMAgv8C","GiLLEQAAQBAJ","BKooCwAAQBAJ","oQzJvQEACAAJ","Nx-vY7ac1OcC","eoIAEgAAQBAJ","x4WUEQAAQBAJ"]



