from locust import HttpUser, between, task


class AdTrafficUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        response = self.client.post(
            "/users",
            json={"country": "US", "age": 24, "device": "ios", "interests": "fitness"},
        )
        self.user_id = response.json()["id"]

    @task(5)
    def request_ad(self) -> None:
        self.client.post("/ads/request", json={"user_id": self.user_id}, name="/ads/request")

    @task(1)
    def list_alerts(self) -> None:
        self.client.get("/quality/alerts", name="/quality/alerts")

