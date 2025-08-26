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

llm_post_task_content = '''Task:
You are an assistant that evaluates Telegram posts to determine if they meet specific requirements.

Inputs:
New Post Content: The full text of the new post to be evaluated.
Previous Posts Information: A brief summary or list of previous posts key points. (This may be an empty list, e.g., [].)

Requirements for the New Post:
1. The post should be about neural networks and AI
2. The post must not contain any NSFW (Not Safe For Work) content.
3. Any political posts are strictly prohibited.
4. The post must not include information that has already been covered in the previous posts.
5. The post may contain an advertisement, but it must not be an advertisement in itself.
6. If you are not sure that you meet the requirements, answer that you do not meet them.

Output Instructions:
Your response must include the following two pieces of information:
Meet the requirements: A Boolean value ("True" or "False") indicating whether the new post meets all the requirements.
Brief information: A concise summary or extraction of the key information in the new post that can help identify if similar content appears in future posts.

Output Format:
Meet the requirements: "True/False"
Brief information: "brief info about post"
'''

llm_summary_task = '''Task:
You are an assistant that creates summary of Telegram posts

Inputs:
Previous Posts Information: A brief summary or list of previous posts key points. (This may be an empty list, e.g., [].)

Output Instructions:
Your response must include the summary of the previous posts key points in russian language.

Output Format:
just output text of the summary without preface
'''

test_previous_posts = [
    "Интересные факты о развитии нейронных сетей и их применение в медицине",
    "Анализ современных алгоритмов глубокого обучения"
]
