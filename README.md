# 💫 Omnixys Product Service

Der **Omnixys Product Service** ist ein modularer Microservice auf Basis von NestJS und GraphQL. Er verwaltet Produktdaten, Varianten, Filteroptionen und unterstützt vollständige Integration in das Omnixys-Ökosystem inklusive Observability, Authentifizierung und Messaging.

> Teil der [OmnixysSphere](https://github.com/omnixys) – *The Fabric of Modular Innovation*

---

## 🚀 Features

* 🧞 Verwaltung von Produkten & Varianten
* 🔎 Filterbare GraphQL-Abfragen
* 🛡️ Rollenbasierte Authentifizierung (Keycloak)
* 📦 Kafka Event Streaming (product.created, product.updated, ...)
* 📊 Prometheus Metrics & Tempo Tracing
* 🧠 Vollständig getestete Services (Jest, SonarCloud)
* 🩵 JSON-basiertes strukturiertes Logging via `LoggerPlus`

---

## 🧰 Tech Stack

| Kategorie         | Technologie                |
| ----------------- | -------------------------- |
| Sprache           | TypeScript (NestJS)        |
| Authentifizierung | Keycloak                   |
| Kommunikation     | GraphQL                    |
| Events            | Kafka (aiokafka)           |
| Monitoring        | Prometheus, Tempo, Grafana |
| Logging           | LoggerPlus, Loki           |
| Testing           | Jest, ESLint, SonarCloud   |

---

## 🧱 Architektur

```text
src/
├── graphql/            # Schema & Resolver
├── modules/            # Produkt-, Variantenmodule etc.
├── services/           # Business-Logik
├── kafka/              # Event-Publisher/Consumer
├── dto/                # Input/Output Objekte
├── utils/              # Logger, Tracing, Kontexte
└── main.ts             # Entry Point
```

---

## 🛠️ Lokale Entwicklung

```bash
git clone https://github.com/omnixys/omnixys-product-service.git
cd omnixys-product-service
npm install
npm run start:dev
```

---

## 🥪 Testen

```bash
npm run test
```

---

## 📈 Monitoring & Observability

* [x] Prometheus unter `/metrics`
* [x] OpenTelemetry-Setup für Tempo
* [x] JSON-basierte Logs (LoggerPlus)
* [x] Kafka Logging Events

---

## 🗒️ API (GraphQL Playground)

> [http://localhost:7301/graphql](http://localhost:7301/graphql)

Beispiel-Query:

```graphql
query {
  findProducts(criteria: { name: "Laptop" }) {
    id
    name
    variants {
      sku
      price
    }
  }
}
```

---

## 🔐 Sicherheit & Zugriff

Authentifizierung via Keycloak:

* `Authorization: Bearer <token>`
* Unterstützt Realm-Rollen: `Admin`, `helper`

---

## 🧉 Integration mit Kafka

Sende Kafka-Events auf:

* `product.created`
* `product.updated`
* `product.deleted`

Header enthalten:

* `x-service`, `x-trace-id`, `x-event-name`, `x-event-version`

---

## 🤝 Contributing

Siehe [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 🧪 Lizenz

Lizensiert unter der [GNU GPL v3.0](./LICENSE.md)
© 2025 Omnixys – *Modular Thinking. Infinite Possibilities.*
