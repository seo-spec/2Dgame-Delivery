"""사용자가 변경한 화면 설정을 프로젝트 데이터 폴더에 저장한다."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile


SETTINGS_PATH = Path(__file__).resolve().parents[2] / 'data/user_settings.json'


def save_screen_mode(fullscreen):
    """임시 파일을 완성한 뒤 교체해 저장 도중 기존 파일이 깨지지 않게 한다."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with NamedTemporaryFile(
            mode='w', encoding='utf-8', dir=SETTINGS_PATH.parent,
            prefix='.user_settings-', suffix='.tmp', delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump({'fullscreen': fullscreen}, temporary_file, indent=2)
            temporary_file.write('\n')
        temporary_path.replace(SETTINGS_PATH)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
