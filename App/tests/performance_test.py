from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.login()

    def login(self):
        self.client.post("/login", data={
            "username": "emma",       
            "password": "emmapass"
        })

class AuthenticatedStudent(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.login()

    def login(self):
        self.client.post("/login", data={
            "username": "mark",      
            "password": "markpass"
        })

    
    @task
    def leaderboard_page(self):
        self.client.get(url="/leaderboard")
    
    @task
    def student_profile_page(self):
        student_id = random.randint(1, 30)
        self.client.get(url=f"/student_profile/{student_id}")
    
    @task
    def moderator_profile_page(self):
        moderator_id = random.randint(1, 5)
        self.client.get(url=f"/moderator_profile/{moderator_id}")
    
    @task
    def all_competitions(self):
        res = self.client.get("/competitions")
    
    @task
    def competition_details_page(self):
        competition_id = random.randint(1, 6)
        self.client.get(url=f"/competitions/{competition_id}")
    
    @task
    def valid_competitions(self):
        for comp_id in [1, 2, 3, 4, 5, 6]:
            self.client.get(f"/competitions/{comp_id}")

    @task
    def get_notifications(self):
        self.client.get("/notifications")

    # @task                             
    # def post_dummy_results(self):
    #     comp_name = "CodeElite"  # Make sure this exists
    #     payload = {
    #         "team_name": f"team{random.randint(100,999)}",
    #         "student1": "mark",
    #         "student2": "michelle",
    #         "student3": "eric",
    #         "score": random.randint(0, 10)
    #     }
    #     self.client.post(f"/add_results/{comp_name}", data=payload)
