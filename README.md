# IoT Smart Waste Management System

# Table of Contents

- [Scenario - Smart Urban Waste Management](#scenario---smart-urban-waste-management)
  - [Main Components](#main-components)
  - [Communication](#communication)
    - [MQTT Topics & Data](#mqtt-topics--data)
    - [MQTT Topics & Service Mapping](#mqtt-topics--service-mapping)

---

# Scenario - Smart Urban Waste Management

Il progetto **IoT Smart Waste Management** simula un'infrastruttura cittadina intelligente per la gestione della raccolta rifiuti. L'obiettivo è ottimizzare i percorsi di raccolta, monitorare lo stato di salute dei cassonetti (Smart Bins) e garantire la sicurezza pubblica rilevando anomalie come incendi o livelli critici di inquinamento dell'aria.

## Main Components

- **Edge Layer (Smart Bin)**
  Il cassonetto intelligente è dotato di sensori e attuatori per l'interazione autonoma con l'ambiente e gli utenti.
  - **Sensors:**
    - **Fill Level Sensor**: Misura la percentuale di riempimento del cassonetto.
    - **Smoke Detector**: Rileva la presenza di fumo (in ppm) per prevenire incendi.
    - **IAQ Sensor**: Monitora la qualità dell'aria (Indoor Air Quality) per rilevare cattivi odori o sostanze nocive.
    - **Battery Level**: Monitora lo stato energetico del dispositivo IoT.
  - **Actuators:**
    - **Smart Lid**: Coperchio che si blocca se il cassonetto è pieno o c'è un pericolo (fumo).
    - **Display/QR Code**: Un'interfaccia dinamica che cambia URL per indirizzare l'utente verso il cassonetto libero più vicino in caso di disservizio.

- **Cloud Layer (Data Manager)**
  Il servizio centrale che agisce come coordinatore del sistema.
  - **Digital Twin Manager**: Mantiene lo stato aggiornato di tutti i cassonetti attivi (`SmartBinDigitalTwin`).
    - **Alert**: per generare allerte specifiche:
      - **Collection Alert**: Cassonetto pieno o aria insalubre.
      - **Maintenance Alert**: Batteria scarica.
      - **Safety Check**: Rilevamento fumo/incendio.
  - **Re-routing Logic**: In caso di cassonetto pieno, calcola il cassonetto libero più vicino e aggiorna il display del cassonetto saturo.
  - **New configs**: può mandare nuove configurazioni al cestino

---

**Smart Bin Telemetry Model (SenML+JSON)**

Utilizzato per l'invio periodico dei dati dai sensori al cloud.

| **Field (`n`)** | **Unit (`u`)** | **Type** | **Description** |
|-----------------|----------------|----------|-----------------|
| `battery`       | `/` (%)        | Double   | Livello batteria (0.0 - 1.0) |
| `fill`          | `/` (%)        | Double   | Livello riempimento (0.0 - 1.0) |
| `smoke`         | `ppm`          | Double   | Concentrazione fumo |
| `iaq`           | N/A            | Integer  | Indice qualità dell'aria (VOC) |
| `lid_opened`    | Boolean        | Boolean  | Stato del coperchio (True=Aperto) |

---

## Communication

Il sistema utilizza il protocollo **MQTT** per tutte le comunicazioni: la scelta è motivata dalle poche risorse del nodo e dalla quantità potenzialmente elevata di essi 

### MQTT Topics & Data

**1. Telemetry & State (Edge -> Cloud)**
- **Topic**: `bin/{bin_id}/telemetry`
- **Payload**: Array JSON in formato SenML.
- **QoS**: 1.

**2. Bin Info (Edge -> Cloud)**
- **Topic**: `bin/{bin_id}/info`
- **Payload**: JSON custom.
- **QoS**: 1
- **Retain**: `True` (Il Manager riceve l'info anche se si connette dopo).

**3. Alerts (Cloud -> Employees)**
- **Topic**: `smart_waste/alert/{alert_type}/{bin_id}`
- **Payload**: JSON custom.
- **QoS**: 1
- **Retain**: `True` (L'addetto riceve l'alert anche se si connette dopo).

**4. Control & Configuration (Cloud -> Edge)**
- **Action**: `bin/{bin_id}/action` (Comandi attuatori: "close_lid", "open_lid").
- **Config**: `bin/{bin_id}/config` (Aggiornamento remoto soglie).
- **Display**: `bin/{bin_id}/display` (Invio nuovo URL per QR code dinamico).
- **QoS**: 1

### MQTT Topics & Service Mapping

| Topic Pattern | Publisher | Subscriber | Purpose |
|---------------|-----------|------------|---------|
| `bin/+/telemetry` | Smart Bin | Data Manager | Monitoraggio continuo stato e sensori. |
| `bin/+/info` | Smart Bin | Data Manager | Discovery e registrazione nuovi cassonetti. |
| `alert/+/+` | Data Manager | Dashboard/App | Notifica operatori ecologici o vigili del fuoco. |
| `bin/<bin_id>/display` | Data Manager | Smart Bin | Re-indirizzamento utenti verso cassonetti liberi. |
| `bin/<bin_id>/action` | Data Manager | Smart Bin | Attuazione remota di emergenza (es. blocco coperchio). |
