from dataclasses import dataclass, field

from google.cloud.firestore import AsyncClient

from .qc_logs_repository import QCLogsRepository
from .qc_settings_repository import QCSettingsRepository
from .qc_stats_repository import QCStatsRepository
from .user_settings_repository import UserSettingsRepository


@dataclass
class RepositoryManager:
    db: AsyncClient
    user_settings_repo: UserSettingsRepository = field(init=False)
    qc_settings_repo: QCSettingsRepository = field(init=False)
    qc_logs_repo: QCLogsRepository = field(init=False)
    qc_stats_repo: QCStatsRepository = field(init=False)

    def __post_init__(self):
        self.user_settings_repo = UserSettingsRepository(self.db)
        self.qc_settings_repo = QCSettingsRepository(self.db)
        self.qc_logs_repo = QCLogsRepository(self.db)
        self.qc_stats_repo = QCStatsRepository(self.db)
