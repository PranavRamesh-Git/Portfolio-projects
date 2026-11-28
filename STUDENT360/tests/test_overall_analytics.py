def test_overall_analytics(client):
    with client.session_transaction() as sess:
        sess["teacher_id"] = 3

    payload = {
        "assessment_class" : "8"
    }

    response = client.post('/api/analytics/ClassOverall',json=payload)

    assert response.status_code == 200

    data = response.get_json()

    assert data["overall"]["min_percent"] == "47.85"
    assert data["overall"]["max_percent"] == "98.81"
    assert data["overall"]["avg_percent"] == "72.01"



#select MIN(total_percentage), MAX(total_percentage), ROUND(AVG(total_percentage),2) from student_total_marks where assessment_class = '8';
#47.85	98.81	72.01