import logging
import os
import pickle

from configparser import ConfigParser, ExtendedInterpolation
from threading import Lock

from depend.provided_users import ProvidedUser
from depend.common_helpers import get_project_root
from depend.ip_utils import find_unused_ip_from_range


logger = logging.getLogger()


class Singleton(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigManager(metaclass=Singleton):
    _path_configs_service1 = get_project_root() / "configs/service1"
    _path_configs_service2 = get_project_root() / "configs/atlantia"

    def __init__(self):
        if version := os.environ.get("SERVICE_VERSION"):
            config_file = os.environ.get("CONFIG_FILE")
            if version == "service1":
                if not config_file:
                    logger.info("CONFIG_FILE not found. Falling back to variables.ini file")
                    config_file = "variables"

                logger.debug(f"Running tests against '{config_file}' config file")
                self._load_config(config_file, ConfigManager._path_configs_service1)
            elif version == "service2":
                if config_file:
                    config_file = f"{config_file}.ini"
                else:  # default file used for FQA testing
                    config_file = "atlantia_ci_pipeline_variables.ini"

                logger.debug(f"Running tests against '{config_file}' config file")
                self._load_config(config_file, ConfigManager._path_configs_service2)
        else:
            logger.warning("Service not specified! Falling back to service2 as default!")
            config_file = "atlantia_ci_pipeline_variables.ini"

            logger.debug(f"Running tests against '{config_file}' config file")
            self._load_config(config_file, ConfigManager._path_configs_service2)

    def _load_config(self, config: str, path) -> None:
        if ".ini" in config:
            config = config.replace(".ini", "")
        self.config = ConfigParser(interpolation=ExtendedInterpolation())
        try:
            with open(f"{path}/{config}.ini") as file:
                self.config.read(file)
        except Exception:
            raise FileNotFoundError(f"File {config}.ini is not found!")
        self.config_path = self.config.read(f"{path}/{config}.ini")
        self.config_name = config + ".ini"
        logger.debug(f"Loaded config {path}/{config}")

    def _deep_copy(self) -> ConfigParser:
        """deep copy config"""
        temp = pickle.dumps(self.config)
        new_config = pickle.loads(temp)
        return new_config

    @classmethod
    def get_config(cls) -> ConfigParser:
        instance = cls()
        config = instance._deep_copy()
        return config

    @classmethod
    def write_and_save_config(cls) -> None:
        instance = cls()
        with open(f"{instance.config_path[0]}", "w") as configfile:
            instance.config.write(configfile)

    @classmethod
    def get_config_path(cls) -> str:
        instance = cls()
        return instance.config_path[0]

    @classmethod
    def get_config_name(cls) -> str:
        instance = cls()
        return instance.config_name

    @classmethod
    def read_config_as_dict(cls) -> dict:
        """Read variables.ini given and return them as dictionary

        Returns:
            dict: variables ini sections will be stored as dictionary.
                  elements under each section will be dictionary key values.

        """
        # config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        # config.read("/workspaces/qa_automation/Medusa/configs/atlantia/atlantia_ci_pipeline_variables.ini")
        instance = cls()
        config_as_dict = {}
        # Read a section such as CLUSTER,VDBENCH and etc
        for section in instance.config.sections():
            config_as_dict[section] = {}
            # Each element in section (like atlas-url element in CLUSTER section)
            for element in instance.config.options(section):
                # Some config file elements are separated by '-' ,
                # to convert them to class property we replace it with '_'.
                # For ex: atlantia-url in variables.ini will be atlantia_url in Cluster class(snake_case)
                snake_case_element = element.replace("-", "_")
                config_as_dict[section][snake_case_element] = instance.config.get(section, element)
        return config_as_dict

    @classmethod
    def check_and_update_unused_ip_for_psg(cls, config) -> None:
        """
        Updates unused IP for the user data fields 'name' and 'secondary_psgw_ip'
        """
        for user in ProvidedUser:
            # Todo: User object for S1 & S2 improved.
            if not user.value.startswith("USER"):
                continue
            key = f"TEST-DATA-FOR-{user.value}"
            instance = cls()
            user_data = instance.config[key]
            unused_ip = find_unused_ip_from_range(user_data["network"])
            if not unused_ip:
                raise Exception(f"Failed to find unused IP from '{user_data['network']}'")
            config.set(key, "network", unused_ip)
            logger.info(f"Updated {key}.network = {unused_ip}")
            unused_ip = find_unused_ip_from_range(user_data["secondary_psgw_ip"], exclude_ip_list=[unused_ip])
            if not unused_ip:
                raise Exception(f"Failed to find unused IP from '{user_data['secondary_psgw_ip']}'")
            config.set(key, "secondary_psgw_ip", unused_ip)
            logger.info(f"Updated {key}.secondary_psgw_ip = {unused_ip}")
