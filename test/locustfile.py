from locust import HttpLocust, TaskSet, task

class MyTaskSet(TaskSet):
    @task(2)
    def index(self):
        self.client.get("/signaligner.html")

    @task(1)
    def about(self):
        for i in range(100):
            self.client.get("/signaligner.html?session=%i&dataset=SPADES_17&zoom=3&zoomi=99&offset=0&iplayer=0&ialgo=0" %i, name="signaligner.html?session=[id]&dataset=SPADES_17&zoom=3&zoomi=99&offset=0&iplayer=0&ialgo=0")
class MyLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 5000
    max_wait = 10000