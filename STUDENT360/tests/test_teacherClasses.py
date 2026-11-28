def test_classes(client):


    with client.session_transaction() as sess:
        sess["teacher_id"] = 3


    response = client.get("/api/class_access")
    print("STATUS CODE:", response.status_code)
    print("RESPONSE DATA:", response.get_data(as_text=True))
    assert response.status_code == 200
    assert response.get_json() == {"classes" : ["8A","8B","8C","9A","9B","9C","10A","10B","10C"]}