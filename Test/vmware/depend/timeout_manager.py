from depend.config_manager import ConfigManager


class TimeoutManager:
    first_time_psgw_creation: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("first_time_psgw_creation")) else 0
    )
    create_psgw_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("create_psgw_timeout")) else 0
    )
    create_backup_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("create_backup_timeout")) else 0
    )
    standard_task_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("standard_task_timeout")) else 0
    )
    health_status_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("health_status_timeout")) else 0
    )
    v_center_manipulation_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("v_center_manipulation_timeout")) else 0
    )
    resize_psg_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("resize_psg_timeout")) else 0
    )
    resize_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("resize_timeout")) else 0
    )
    psg_shutdown_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("psg_shutdown_timeout")) else 0
    )
    psg_powered_off_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("psg_powered_off_timeout")) else 0
    )
    create_local_store_timeout: int = (
        int(timeout) if (timeout := ConfigManager.get_config()["TIMEOUTS"].get("create_psgw_timeout")) else 0
    )
    task_timeout = 100
