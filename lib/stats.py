class Stats:
    def __init__(self):
        self.__total_requests = 0
        self.__successful_requests = 0
        self.__failed_row_requests = 0
        self.__total_posts = 0
        self.__chosen_posts = 0

    def get_requests(self):
        return f"requests: {self.__successful_requests}/{self.__total_requests} (successful/total)\nfailed requests in a row: {self.__failed_row_requests}"

    def add_total_requests(self, count: int):
        self.__total_requests += count

    def add_failed_row_requests(self, count: int):
        self.__failed_row_requests += count

    def add_successful_requests(self, count: int):
        self.__successful_requests += count

    def get_posts(self):
        return f"posts: {self.__chosen_posts}/{self.__total_posts} (chosen/total)"

    def add_total_posts(self, count: int):
        self.__total_posts += count

    def add_chosen_posts(self, count: int):
        self.__chosen_posts += count

    def reset(self):
        self.__class__.__init__(self)

    def __str__(self):
        return f'{self.get_requests()}\n{self.get_posts()}'
