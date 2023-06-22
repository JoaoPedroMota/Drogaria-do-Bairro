import time
from locust import HttpUser, task, between

class DrogariaDoBairro(HttpUser):

    # @task
    # def home(self):
    #     self.client.get('/')

    @task
    def shop(self):
        self.client.get('/shop/')