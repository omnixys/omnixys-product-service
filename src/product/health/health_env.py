from pydantic_settings import BaseSettings, SettingsConfigDict


class HealthSettings(BaseSettings):
    PROMETHEUS_HEALTH_URL: str = "http://localhost:9090/-/healthy"
    TEMPO_HEALTH_URL: str = "http://localhost:3200/metrics"
    MONGODB_HEALTH_URL: str = "mongodb://localhost:27017"
    KEYCLOAK_HEALTH_URL: str

    model_config = SettingsConfigDict(env_file=".health.env")


health_settings = HealthSettings()
