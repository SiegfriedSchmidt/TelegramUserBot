from pathlib import Path
import os

secret_folder_path = Path(os.path.dirname(os.path.realpath(__file__)))
if os.path.basename(os.path.dirname(os.path.realpath(__file__))) == 'lib':
    secret_folder_path = secret_folder_path.parent
secret_folder_path = secret_folder_path / 'secret'

telegram_session_path = secret_folder_path / 'telegram_user.session'
