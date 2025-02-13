from datetime import time, datetime
from typing import List
from pydantic import SecretStr
from lib.post_assistant import Post
from collections import deque


class Keys:
    def __init__(self, openrouter_api_keys: List[SecretStr]):
        self.queue = deque(zip(openrouter_api_keys, range(1, len(openrouter_api_keys) + 1)))

    def rotate_keys(self):
        self.queue.rotate(1)

    def get_key(self):
        return self.queue[0][0]

    def get_key_number(self):
        return self.queue[0][1]

    def __len__(self):
        return len(self.queue)


class Params:
    def __init__(self, openrouter_api_keys: List[SecretStr]):
        self.is_posting = True
        self.is_night_posting = False
        self.is_pending_posting = True
        self.stub_posting_check = False
        self.start_time = datetime.now()
        self.night_interval = (time(23, 0), time(10, 0))
        self.pending_posts: List[Post] = []
        self.keys = Keys(openrouter_api_keys)

    def __str__(self):
        string = ''
        for key, val in vars(self).items():
            if isinstance(val, bool) or isinstance(val, int) or isinstance(val, str):
                string += f'{key}: {val}\n'
            if isinstance(val, list) or isinstance(val, Keys):
                string += f'{key}: {len(val)}\n'
            if isinstance(val, datetime):
                string += f'{key}: {val.isoformat()}\n'

        cur_time = datetime.now()
        string += f'Uptime: {(cur_time - self.start_time).days} days\n'

        return string
