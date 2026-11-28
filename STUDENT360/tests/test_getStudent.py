def test_getStudent(client):

    with client.session_transaction() as sess:
        sess["teacher_id"] = 3

    params = {
        "search": "Pranav Menon",
        "class_name": "8C"
    }

    response = client.get("/api/students",query_string=params)

    assert response.status_code == 200

    data = response.get_json()

    for student in data["students"]:
        print("NAME:", student["full_name"])
        assert student["email"] == "pranav.menon@school.edu"
        assert student["phone_no"] == "9000000241"