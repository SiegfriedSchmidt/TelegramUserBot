class Stats:
    def __init__(self):
        self.__total_requests = 0
        self.__successful_requests = 0
        self.__total_posts = 0
        self.__chosen_posts = 0

    @property
    def total_requests(self):
        return self.__total_requests

    @property
    def successful_requests(self):
        return self.__successful_requests

    @property
    def total_posts(self):
        return self.__total_posts

    @property
    def chosen_posts(self):
        return self.__chosen_posts

    def get_requests(self):
        return f"{self.successful_requests}/{self.total_requests} (successful/total)"

    def add_total_requests(self, count: int):
        self.__total_requests += count

    def add_successful_requests(self, count: int):
        self.__successful_requests += count

    def get_posts(self):
        return f"{self.chosen_posts}/{self.total_posts} (chosen/total)"

    def add_total_posts(self, count: int):
        self.__total_posts += count

    def add_chosen_posts(self, count: int):
        self.__chosen_posts += count

    def reset(self):
        self.__total_requests = 0
        self.__successful_requests = 0
        self.__total_posts = 0
        self.__chosen_posts = 0
