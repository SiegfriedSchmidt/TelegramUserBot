from datetime import time
from typing import List

from lib.post_assistant import Post


class Params:
    def __init__(self):
        self.is_posting = True
        self.is_night_posting = False
        self.is_pending_posting = True
        self.stub_posting_check = False
        self.night_interval = (time(23, 0), time(14, 0))
        self.pending_posts: List[Post] = []

    def __str__(self):
        string = ''
        for key, val in vars(self).items():
            if isinstance(val, bool) or isinstance(val, int) or isinstance(val, str):
                string += f'{key}: {val}\n'
            if isinstance(val, list):
                string += f'{key}: {len(val)}\n'

        return string
