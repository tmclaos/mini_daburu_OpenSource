from agent_os.skills.account_creation import AccountCreationSkill
from agent_os.skills.deploy_app import DeployAppSkill
from agent_os.skills.monitor_site import MonitorSiteSkill

DEFAULT_SKILLS = [
    AccountCreationSkill(),
    DeployAppSkill(),
    MonitorSiteSkill(),
]

__all__ = ["DEFAULT_SKILLS", "AccountCreationSkill", "DeployAppSkill", "MonitorSiteSkill"]
