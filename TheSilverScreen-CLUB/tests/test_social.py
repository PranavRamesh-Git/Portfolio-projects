def test_get_social(client):


    with client.session_transaction() as sess:
        sess["user_id"] = 1


    response = client.get("/api/viewProfile/7")
    print("STATUS CODE:", response.status_code)
    print("RESPONSE DATA:", response.get_data(as_text=True))
    assert response.status_code == 200