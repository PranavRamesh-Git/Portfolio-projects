def test_getStudent(client):

    with client.session_transaction() as sess:
        sess["teacher_id"] = 3

    params = {
        "search": "Varun Chandran",
        "class_name": "12C"
    }

    response = client.get("/api/students",query_string=params)

    assert response.status_code == 403
    print(response.status_code)