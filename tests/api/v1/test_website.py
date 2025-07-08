from fastapi import status

def test_get_websites_endpoint(test_client, seeded_website):
    response = test_client.get("/v1/website/get_websites")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["url"] == seeded_website.url