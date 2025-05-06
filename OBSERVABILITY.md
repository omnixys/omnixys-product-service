# 📊 Observability-Konzept – GentleCorp-Ecosystem

Dieses Dokument beschreibt das zentrale Observability-Konzept des GentleCorp-Ecosystems. Ziel ist es, Logs, Metriken und Traces aus allen Microservices zentral und effizient zu erfassen, darzustellen und auszuwerten.

---

## 🧱 Architekturüberblick

### Zentrale Komponenten

| Komponente     | Aufgabe                                         | Tool             |
|----------------|--------------------------------------------------|------------------|
| Tracing        | Distributed Tracing aller Services               | OpenTelemetry + Tempo |
| Logging        | Zentrale Log-Verarbeitung über Kafka             | Kafka + Loki     |
| Metriken       | Service Metrics (HTTP, DB, etc.)                 | Prometheus       |
| Visualisierung | UI für alles: Traces, Logs, Metrics              | Grafana          |

---

## 🔁 Konfiguration: Jeder Microservice

### 1. Logging → Kafka
- Verwendung von `LoggerPlus`, `Pino` oder `Loguru`
- Logs werden als JSON-Event an `logs.{service}`-Topic gesendet
- Keine direkte Verbindung zu Loki nötig

### 2. Tracing → Tempo
- OpenTelemetry SDK (NestJS, Spring Boot, FastAPI)
- Export im OTLP-Format an Tempo (`http://tempo:4318`)

### 3. Metrics → Prometheus
- Jeder Service exponiert `/metrics`
- Prometheus scraped regelmäßig die Endpoints

---

## 🧩 Konfiguration: Logging-Service

### Aufgaben:
- Kafka-Consumer für alle `logs.*` Topics
- Anreicherung (trace_id, hostname, env, ...)
- Transformation ins Loki Line Protocol
- Push an `http://loki:3100/loki/api/v1/push`

### Vorteile:
- Entkopplung der Services von Loki
- Leichte Erweiterung und Fehlerbehandlung
- Reduzierte Komplexität je Service

---

## 🧠 Vorteile der Architektur

- ✅ **Zentralisierte Verwaltung**
- ✅ **Leichte horizontale Skalierung**
- ✅ **Weniger Fehler durch vereinheitlichte Schnittstellen**
- ✅ **Leistungsfähige Dashboards und Alerting über Grafana**
- ✅ **Saubere Trennung der Verantwortlichkeiten**

---

## 🔧 Servicespezifische Konfigurationen (Beispiele)

### NestJS (TypeScript)
```ts
OpenTelemetryModule.forRoot({
  serviceName: 'product-service',
  otelExporterConfig: {
    url: 'http://tempo:4318',
    type: 'otlp'
  }
});
```

### Spring Boot (Java)
```yaml
otel:
  service:
    name: account-service
  exporter:
    otlp:
      endpoint: http://tempo:4318
```

### FastAPI (Python)
```py
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

---

## Zusammenfassung: Konfigurationsübersicht

| Komponente   | Jeder Service               | Nur Logging-Service         |
| -------------| ----------------------------| ----------------------------|
| Logging      | Kafka Producer (LoggerPlus) | Kafka Consumer, Loki-Pusher |
| Tracing      | OpenTelemetry SDK           | ❌                          |
| Metrics      | Prometheus /metrics         | ❌                          |
| Loki         | ❌                          | ✅ Push via HTTP            |
| Tempo        | OTLP Export (Tracing)       | ❌                          |
| Prometheus   | /metrics exposen            | ❌                          |
| Kafka Topics | logs.{service} schreiben    | logs.* lesen                |

---

## 🧭 Nächste Schritte (optional)

- [ ] `docker-compose.yml` mit Tempo, Loki, Prometheus, Grafana erstellen
- [ ] Logging-Service implementieren (Kafka-Consumer → Loki)
- [ ] LoggerPlus / Pino / Loguru Wrapper vereinheitlichen
- [ ] Grafana-Dashboards definieren (Traces, Errors, Performance)

---

Ich kann dir fertige Grafana Dashboards exportieren für:
Tempo (Traces visualisieren)
Prometheus (Metriken)
Loki (Logs durchsuchen)

📁 **Datei:** `OBSERVABILITY.md`

✍️ Autor: GentleCorp Core Engineering

🕓 Letzte Aktualisierung: 25.04.2025

