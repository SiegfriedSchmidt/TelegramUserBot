from pathlib import Path
import os

# constants
secret_folder_path = Path(os.environ.get("SECRET_FOLDER", "."))
if str(secret_folder_path) == '.':
    secret_folder_path = Path(os.path.dirname(os.path.realpath(__file__)))
    if os.path.basename(os.path.dirname(os.path.realpath(__file__))) == 'lib':
        secret_folder_path = secret_folder_path.parent
    secret_folder_path = secret_folder_path / 'secret'

telegram_session_path = secret_folder_path / 'telegram_user.session'

llm_task_content = '''Task:
You are an assistant that evaluates Telegram posts to determine if they meet specific requirements.

Inputs:
New Post Content: The full text of the new post to be evaluated.
Previous Posts Information: A brief summary or list of previous posts' key points. (This may be an empty list, e.g., [].)

Requirements for the New Post:
Content Requirement: The post must include interesting information about neural networks or AI.
NSFW Requirement: The post must not contain any NSFW (Not Safe For Work) content.
Originality Requirement: The post must not include information that has already been covered in the previous posts.

Output Instructions:
Your response must include the following two pieces of information:
Meet the requirements: A Boolean value ("True" or "False") indicating whether the new post meets all the requirements.
Brief information: A concise summary or extraction of the key information in the new post that can help identify if similar content appears in future posts.

Output Format:
Meet the requirements: "True/False"
Brief information: "brief info about post"
'''

test_previous_posts = [
    "Интересные факты о развитии нейронных сетей и их применение в медицине",
    "Анализ современных алгоритмов глубокого обучения"
]
