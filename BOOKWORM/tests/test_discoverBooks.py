def test_discoverBooks(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        params = {
            "search" : "Gone Girl",
            "orderby": "relevance"
        }

    response = client.get('/api/discover',query_string=params)
    data = response.get_json()

    print(response.status)
    print(data["all_books"])


