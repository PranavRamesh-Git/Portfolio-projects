
def test_section_analytics(client):


    with client.session_transaction() as sess:
        sess["teacher_id"] = 3

    # Request data
    payload = {
        "assessment_class": "8",
        "class_name": "8C"
    }

    response = client.post(
        "/api/analytics/SectionSpecific",
        json=payload
    )

    print("STATUS CODE:", response.status_code)
    #print("RESPONSE:", response.get_json())

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    print(data["overall"])
    print(data["subData"])
    print(data["ranked_list"])

    assert data["overall"]["max_percent"] == "87.33"
    assert data["overall"]["min_percent"] == "56.78"
    assert data["overall"]["avg_percent"] == "72.54"




#select MIN(total_percentage), MAX(total_percentage), ROUND(AVG(total_percentage),2) from student_total_marks where class_name = '8C';
#56.78	87.33	72.54