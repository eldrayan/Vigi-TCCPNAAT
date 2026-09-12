> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.5.0  
> **Responsável:** Squad Vigi (Lead: Elder Rayan Oliveira Silva)  
> **Milestone:** Estruturação de Requisitos e Design Arquitetural

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Squad Vigi | 06/09/2026 | Elaboração inicial do Diagrama Arquitetural orientado a Fluxo de Dados (Pressman). |
| **0.2.0** | Squad Vigi | 06/09/2026 | Simplificação de atuadores físicos e inclusão de buffer offline. |
| **0.3.0** | Squad Vigi | 06/09/2026 | Integração do sensor fotoelétrico infravermelho E18-D80NK. |
| **0.4.0** | Squad Vigi | 08/09/2026 | Atualização do armazenamento local para banco SQLite e dashboard de supervisão para FastAPI e React. |
| **0.5.0** | Squad Vigi | 08/09/2026 | Alinhamento da topologia embarcada (All-in-One na Raspberry Pi 5), esquemas de dados e payloads. |

---

## 🏛️ Visão Geral da Arquitetura

### Organização do software

O backend é organizado como um monólito modular: uma aplicação FastAPI com responsabilidades separadas em módulos, compartilhando a infraestrutura de configuração, banco e MQTT. O módulo de inspeções está em `backend/app/modules/inspections/`, com rotas, DTOs, serviços, repositório e modelo de persistência. Essa separação facilita localizar, documentar e manter cada responsabilidade.

A implantação da PoC também inclui o processo de inferência no Edge e o broker Mosquitto, executados separadamente. Portanto, monólito modular descreve o backend, não a execução de todo o sistema em um único processo. O dashboard React permanece previsto para o navegador.

### Visão por fluxo de dados

Os blocos abaixo descrevem a arquitetura proposta. O fluxo já implementado e as integrações pendentes estão detalhados no [README](../../README.md), incluindo a persistência atual pelo consumidor MQTT e a fila local no Edge ainda prevista.

A arquitetura do sistema **Vigi** adota o modelo de **Design Orientado ao Fluxo de Dados** (*Roger S. Pressman*), estruturada em três camadas modulares e desacopladas:

1. **Camada de Entradas (*Inputs*):** Detecção de presença física pelo sensor fotoelétrico infravermelho **E18-D80NK** e aquisição instantânea de imagem sob demanda pela câmera digital.
2. **Camada de Processamento e Serviços (*Edge Node — Raspberry Pi 5*):** 
   * Tratamento de sinal digital com filtro de *debounce* (30-100 ms);
   * Captura sincronizada de quadro no plano focal de inspeção;
   * Inferência de Inteligência Artificial (*Edge AI*);
   * Lógica de decisão preventiva (*Fail-Safe*);
   * Gravação transacional segura no banco de dados local **SQLite** (modo WAL);
   * Broker **Mosquitto** e backend **FastAPI** executando localmente na Raspberry Pi via loopback (*localhost*).
3. **Camada de Saídas e Supervisão (*Outputs*):** Publicação assíncrona orientada a eventos via protocolo **MQTT**, consumo pelo FastAPI e entrega de indicadores ao **Dashboard React** no navegador via **HTTP / SSE** através da rede local (Wi-Fi/Ethernet).

---

## 📊 Diagrama Arquitetural (Fluxo de Dados)

<p align="center">
  <img src="../img/Fluxo.jpeg" alt="Fluxo Atualizado do Protótipo Vigi" width="850">
</p>

### Representação em Bloco Lógico (Mermaid)

```mermaid
flowchart LR
    subgraph ENTRADAS["1. Camada de Entradas (Ambiente Físico)"]
        direction TB
        S1["Sensor Fotoelétrico IR E18-D80NK<br/><i>(Gatilho Digital NPN via GPIO)</i>"]
        S2["Câmera Digital / RPi Cam<br/><i>(Captura de Frame sob Demanda)</i>"]
    end

    subgraph RASPBERRY["2. Nó de Borda Integrado (Raspberry Pi 5)"]
        direction TB
        subgraph PROCESSAMENTO["Pipeline de Decisão & Persistência"]
            direction TB
            P1["Filtro de Debounce & Sincronização<br/><i>(30 ms a 100 ms / RNF08)</i>"]
            P2["Motor de Visão & Inferência Edge AI<br/><i>(OpenCV + Modelo Classificador)</i>"]
            P3["Motor de Decisão & Fail-Safe<br/><i>(Conforme vs. Não-Conforme / RN02)</i>"]
            P4["Banco de Dados Local SQLite<br/><i>(Modo WAL / Transações ACID / 30 dias)</i>"]
            
            P1 -->|Disparo de Captura| P2
            P2 -->|Score de Confiança| P3
            P3 -->|Gravação do Evento| P4
        end

        subgraph SAIDAS_LOCAIS["Serviços Locais Embarcados"]
            direction TB
            O1["Cliente Publicador MQTT<br/><i>(Payloads JSON Assíncronos)</i>"]
            O2["Broker Mosquitto Local<br/><i>(Distribuição em Localhost)</i>"]
            O3["Backend FastAPI<br/><i>(Consumidor MQTT, API REST e SSE)</i>"]
            
            O1 -->|Localhost TCP:1883| O2
            O2 -->|Localhost MQTT| O3
        end
    end

    subgraph SUPERVISAO["3. Camada de Supervisão (Navegador Web)"]
        direction TB
        O4["Dashboard Web React<br/><i>(Chart.js, Lucide e SCSS)</i>"]
    end

    S1 -->|Interrupção Digital| P1
    S2 -->|Frame Sincronizado| P2
    P3 -->|Evento de Inspeção| O1
    P4 -.->|Sincronização Pós-Queda| O1
    P4 <-->|Consultas REST e Histórico| O3
    O3 -->|Wi-Fi / LAN (HTTP e SSE)| O4
```

---

## 🔍 Detalhamento das Camadas

### 1. Camada de Entradas (*Inputs*)
* **Sensor Fotoelétrico Infravermelho E18-D80NK:** Instalado na lateral da esteira. Ao detectar a passagem da garrafa, fecha contato para nível lógico baixo (NPN), gerando uma interrupção na GPIO da Raspberry Pi 5.
* **Câmera Digital (RPi Camera Module / USB HD):** Acionada sob demanda apenas no instante em que o frasco está centralizado no plano de teste.

### 2. Camada de Processamento (*Edge Node — Raspberry Pi 5*)
* **Debounce & Sincronização:** Filtra oscilações eletromecânicas do sinal do sensor E18-D80NK (30 a 100 ms, conforme [RNF08](../requisitos/03-requisitos-nao-funcionais.md)).
* **Pipeline de Visão & Edge AI:**
  * Pré-processamento e normalização do frame;
  * Classificação visual (`CONFORME`, `SEM_TAMPA`, `TAMPA_TORTA` ou `AMASSADO`) com acurácia mínima de 90% ([RNF06](../requisitos/03-requisitos-nao-funcionais.md)).
* **Mecanismo de Decisão & *Fail-Safe*:**
  * Em caso de baixa confiança ou falha de leitura, o recipiente é preventivamente marcado como não-conforme, registrado sob a categoria `FALHA_TECNICA` e segregado do Pareto de defeitos do produto ([RN02](../requisitos/01-regras-de-negocio.md), [RN11](../requisitos/01-regras-de-negocio.md)).
* **Persistência Local com SQLite (*Offline-First*):**
  * Cada ciclo de inspeção é gravado em banco relacional SQLite local com garantia ACID em modo *Write-Ahead Logging* (WAL), permitindo gravações concorrentes com leituras do dashboard sem corrupção e retido por até 30 dias ([RN04](../requisitos/01-regras-de-negocio.md), [RN10](../requisitos/01-regras-de-negocio.md), [RNF03](../requisitos/03-requisitos-nao-funcionais.md)). O campo `sync_status` gerencia a fila de envio e retransmissão ordenada ao broker MQTT ([RNF04](../requisitos/03-requisitos-nao-funcionais.md)).

### 3. Camada de Saídas (*IoT & Supervisão*)
* **Publicador MQTT Local:** Envia assincronamente as mensagens JSON para o broker Mosquitto em *localhost* sem bloquear o laço de inspeção. O broker também aceita inscrições de clientes remotos via Wi-Fi (ex: painéis OLED ou supervisórios de linha).
* **Backend FastAPI:** Executa na Raspberry Pi, consome os eventos do broker Mosquitto local, consulta diretamente o SQLite para métricas históricas de OEE e relatórios ([US07](../requisitos/02-requisitos-funcionais.md), [US08](../requisitos/02-requisitos-funcionais.md)) e disponibiliza API REST e eventos via SSE.
* **Dashboard React:** Interface web executada no navegador do cliente (notebook, tablet ou terminal do operador), consumindo exclusivamente a API do FastAPI via Wi-Fi/LAN com tempo de resposta $< 2\text{ s}$ ([US02](../requisitos/02-requisitos-funcionais.md), [US03](../requisitos/02-requisitos-funcionais.md), [RNF11](../requisitos/03-requisitos-nao-funcionais.md)).

### Separação entre backend e frontend

O **backend e toda a camada de dados** rodam inteiramente na Raspberry Pi em Python: processamento de imagens, inferência, publicação e consumo MQTT, persistência SQLite, validações e API FastAPI. Manter essas responsabilidades no mesmo ecossistema simplifica a comunicação com o modelo e evita duplicar regras em linguagens diferentes.

O **frontend** utiliza JavaScript com React e não acessa diretamente MQTT nem SQLite. Ele é servido e executado no navegador do usuário, consumindo o FastAPI por REST/SSE. O React favorece a composição de telas por componentes, atualizações incrementais em tempo real e a integração com Chart.js e Lucide, recursos adequados ao dashboard operacional do Vigi.

---

## ⏱️ Pipeline Temporal de Inspeção

```text
[T0: Presença Física] ──> [T1: Gatilho & Captura] ──> [T2: Inferência Edge AI] ──> [T3: Decisão & SQLite] ──> [T4: Publicação MQTT Local] ──> [T5: FastAPI + React via Wi-Fi]
   (Sensor E18-D80NK)       (Câmera + Debounce)          (Raspberry Pi 5)             (Persistência Local)           (Broker Localhost)          (Dashboard no Navegador)
       
|<─────────────────────────────────────────────────── Latência Total < 500 ms (RNF01) ───────────────────────────────────────────────────>|
```

---

## 🗄️ Estrutura da Tabela de Persistência Local (SQLite)

```sql
CREATE TABLE IF NOT EXISTS inspecoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resultado VARCHAR(20) NOT NULL,            -- 'CONFORME' | 'NAO_CONFORME'
    categoria VARCHAR(30),                     -- 'ANOMALIA_PRODUTO' | 'FALHA_TECNICA' | NULL
    codigo VARCHAR(50),                        -- 'SEM_TAMPA', 'TAMPA_TORTA', 'AMASSADO', 'ERRO_CAPTURA', etc. | NULL
    confianca REAL,                            -- Ex: 0.96 (NULL ou 0.0 em falhas técnicas sem inferência)
    tempo_processamento_ms INTEGER,           -- Ex: 185
    sync_status VARCHAR(20) DEFAULT 'PENDENTE' -- 'PENDENTE' | 'SINCRONIZADO'
);
```

---

## 📡 Mapeamento de Tópicos MQTT

### 1. Tópico de Inspeções: `vigi/esteira/inspecoes`

* **Exemplo 1: Não-Conformidade (Anomalia do Produto):**
```json
{
  "id_inspecao": 1042,
  "timestamp": "2026-09-06T14:30:01.250Z",
  "resultado": "NAO_CONFORME",
  "categoria": "ANOMALIA_PRODUTO",
  "codigo": "SEM_TAMPA",
  "confianca": 0.94,
  "tempo_processamento_ms": 180
}
```

* **Exemplo 2: Recipiente Conforme (Aprovado):**
```json
{
  "id_inspecao": 1043,
  "timestamp": "2026-09-06T14:30:03.100Z",
  "resultado": "CONFORME",
  "categoria": null,
  "codigo": null,
  "confianca": 0.98,
  "tempo_processamento_ms": 175
}
```

* **Exemplo 3: Falha Técnica (*Fail-Safe* Preventivo — RN02):**
```json
{
  "id_inspecao": 1044,
  "timestamp": "2026-09-06T14:30:05.300Z",
  "resultado": "NAO_CONFORME",
  "categoria": "FALHA_TECNICA",
  "codigo": "ERRO_CAPTURA",
  "confianca": null,
  "tempo_processamento_ms": 210
}
```

### 2. Tópico de Alarmes de Linha: `vigi/esteira/alarmes`
```json
{
  "id_alarme": "ALM-20260906-0042",
  "tipo_alarme": "FALHAS_RECORRENTES",
  "contagem_consecutiva": 4,
  "severidade": "ALTA",
  "timestamp": "2026-09-06T14:32:00.100Z"
}
```

### 3. Tópico de Status do Dispositivo (*LWT*): `vigi/esteira/status`
```json
{
  "status": "ONLINE",
  "uptime_segundos": 3600,
  "registros_pendentes_sync": 0
}
```

---

## 📄 Documentos Relacionados

* [01. Regras de Negócio](../requisitos/01-regras-de-negocio.md)
* [02. Requisitos Funcionais](../requisitos/02-requisitos-funcionais.md)
* [03. Requisitos Não-Funcionais](../requisitos/03-requisitos-nao-funcionais.md)
* [05. Requisitos Técnicos e Justificativas](../requisitos/05-requisitos-tecnicos.md)
