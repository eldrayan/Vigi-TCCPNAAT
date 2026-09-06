> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.4.0  
> **Responsável:** Squad Vigi (Lead: Elder Rayan Oliveira Silva)  
> **Milestone:** Estruturação de Requisitos

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Squad Vigi | 06/09/2026 | Levantamento preliminar de requisitos técnicos e componentes. |
| **0.2.0** | Squad Vigi | 06/09/2026 | Simplificação de escopo e foco na inspeção e telemetria. |
| **0.3.0** | Squad Vigi | 06/09/2026 | Inclusão formal do sensor fotoelétrico infravermelho E18-D80NK. |
| **0.4.0** | Squad Vigi | 06/09/2026 | Definição do SQLite para persistência local e do Node-RED para supervisão e dashboard. |

---

## 🛠️ Levantamento de Requisitos Técnicos

Os requisitos técnicos estabelecem os blocos de sensoriamento físico, aquisição de imagem, processamento em borda, persistência de dados e conectividade IoT necessários para o funcionamento do sistema Vigi.

### 1. Especificação de Componentes e Recursos

| Categoria | Recurso / Tecnologia | Função na Arquitetura | Requisitos Atendidos |
| :--- | :--- | :--- | :--- |
| **Processamento em Borda (*Edge Node*)** | **Raspberry Pi 5 (8GB RAM)** | Orquestração da GPIO de entrada, captura pontual de frames, execução do pipeline de visão computacional/IA, gravação no SQLite e publicação MQTT. | [RN01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RN04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RNF01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md), [RNF02](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |
| **Sensoriamento de Presença (*Gatilho*)** | **Sensor Fotoelétrico Infravermelho E18-D80NK (NPN, 3 a 80 cm)** | Detecção determinística da passagem física do frasco na esteira para disparar o gatilho de captura na câmera via GPIO. | [RN01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RNF08](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |
| **Aquisição de Imagem** | **Câmera Digital (Raspberry Pi Camera Module v2/v3 ou Câmera USB HD)** | Captura instantânea e sincronizada da imagem do recipiente posicionado no plano focal de teste. | [US01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [RNF05](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md), [RNF09](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |
| **Visão Computacional & IA** | **Python 3, OpenCV e Modelo Classificador (TensorFlow Lite / YOLOv8n / MobileNet)** | Pré-processamento e inferência da imagem capturada para identificação de defeitos estruturais e de vedação (sem tampa, tampa inclinada, amassado). | [US01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [RNF06](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md), [RNF07](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |
| **Persistência Local (*Offline-First*)** | **SQLite (Banco de Dados Relacional Embutido / ACID)** | Armazenamento persistente e transacional de todos os eventos de inspeção, métricas de lote e fila de sincronização em caso de queda de rede. | [RN04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RN08](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RN10](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md), [RNF03](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |
| **Protocolo de Comunicação IoT** | **MQTT (Paho-MQTT client via Wi-Fi TCP/IP)** | Publicação assíncrona orientada a eventos e telemetria dos dados inspecionados para o broker central e dashboard. | [RNF04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md), [US03](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [US05](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md) |
| **Supervisão e Dashboard** | **Node-RED Dashboard (Interface Web Industrial em Tempo Real)** | Interface gráfica baseada em nós conectada ao MQTT para exibição de OEE, contagem de refugo por categoria, histórico e alarmes visuais. | [US02](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [US03](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [US04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/02-requisitos-funcionais.md), [RNF11](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md) |

---

## 🔍 Justificativa das Escolhas Tecnológicas

### 1. Gatilho Físico com Sensor Fotoelétrico E18-D80NK
* **Desafio:** Garantir que a câmera capture a foto no instante milimétrico em que a peça passa pelo centro do foco, sem sobrecarregar a CPU com processamento contínuo de vídeo.
* **Justificativa:** O sensor **E18-D80NK** é o padrão de esteiras industriais. Por possuir saída digital NPN direta e tempo de resposta inferior a 2 ms, ele gera uma interrupção precisa na GPIO da Raspberry Pi 5. Com o potenciômetro de calibração traseiro e um filtro de *debounce* de 30-100 ms ([RNF08](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md)), ele ignora reflexões do fundo da bancada e vibrações mecânicas da esteira.

### 2. Processamento em Borda (*Edge AI*) com Raspberry Pi 5
* **Desafio:** A esteira opera a 30 recipientes por minuto, exigindo latência ponta a ponta menor que 500 ms ([RNF01](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md)).
* **Justificativa:** A inferência local na Raspberry Pi 5 elimina o tráfego de imagens em tempo real na rede da fábrica, garantindo decisão instantânea e imunidade total a oscilações ou quedas de internet ([RN04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md)).

### 3. Persistência Local com Banco Embutido SQLite
* **Desafio:** Assegurar a integridade transacional dos registros de inspeção durante paradas bruscas de energia e reter eventos por no mínimo 30 dias durante quedas de rede ([RNF03](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md), [RN10](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/01-regras-de-negocio.md)).
* **Justificativa:** O **SQLite** é um banco de dados relacional embutido (*serverless*), que opera em arquivo único na memória flash e oferece total conformidade **ACID**. Ele garante que nenhuma gravação seja corrompida em quedas repentinas de energia (usando *Write-Ahead Logging - WAL*), permite consultas SQL rápidas para consolidação de OEE e mantém uma flag de controle de sincronização (`sync_status: PENDENTE | SINCRONIZADO`) para retransmissão ordenada ao broker MQTT ([RNF04](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md)).

### 4. Protocolo de Comunicação MQTT vs API REST (HTTP)
* **Desafio:** Transmitir métricas de produção e alarmes de falha sem reter o ciclo de inspeção da esteira.
* **Justificativa:** O padrão *Publish/Subscribe* assíncrono do MQTT (cabeçalho de apenas 2 bytes e suporte nativo a *LWT* e reconexão em background) impede que operações de rede causem bloqueios no laço de inspeção.

### 5. Supervisão e Interface com Node-RED Dashboard
* **Desafio:** Prover um painel visual ágil, de fácil implantação e integração nativa com o ecossistema IoT da bancada industrial.
* **Justificativa:** O **Node-RED** é amplamente utilizado na Indústria 4.0. Ele se conecta nativamente ao broker MQTT e disponibiliza um dashboard web responsivo com gráficos de tendência, medidores de OEE, contadores de rejeito por tipo de anomalia e painéis de alarme em tempo real com tempo de resposta $< 2\text{ s}$ ([RNF11](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/requisitos/03-requisitos-nao-funcionais.md)).

---

## 🔗 Relação com a Arquitetura do Sistema

Para visualização do fluxo de dados e camadas de software, consulte o documento:
* [Diagrama Arquitetural do Vigi](file:///home/rayanoliveira/Desktop/Workspace/Vigi-TCCPNAAT/docs/arquitetura/diagrama-arquitetural.md)
