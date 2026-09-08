> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase  
> **Revisão:** 0.5.0
> **Responsável:** Squad Vigi (Lead: Elder Rayan Oliveira Silva)  
> **Milestone:** Estruturação de Requisitos

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **0.1.0** | Squad Vigi | 06/09/2026 | Levantamento preliminar de requisitos técnicos e componentes. |
| **0.2.0** | Squad Vigi | 06/09/2026 | Simplificação de escopo e foco na inspeção e telemetria. |
| **0.3.0** | Squad Vigi | 06/09/2026 | Inclusão formal do sensor fotoelétrico infravermelho E18-D80NK. |
| **0.4.0** | Squad Vigi | 06/09/2026 | Definição do SQLite para persistência local e do FastAPI e React para supervisão e dashboard. |
| **0.5.0** | Squad Vigi | 08/09/2026 | Alinhamento das classes do modelo com o coletor do dataset. |

---

## 🛠️ Levantamento de Requisitos Técnicos

Os requisitos técnicos estabelecem os blocos de sensoriamento físico, aquisição de imagem, processamento em borda, persistência de dados e conectividade IoT necessários para o funcionamento do sistema Vigi.

### 1. Especificação de Componentes e Recursos

| Categoria | Recurso / Tecnologia | Função na Arquitetura | Requisitos Atendidos |
| :--- | :--- | :--- | :--- |
| **Processamento em Borda (*Edge Node*)** | **Raspberry Pi 5 (8GB RAM)** | Orquestração da GPIO de entrada, captura pontual de frames, execução do pipeline de visão computacional/IA, gravação no SQLite e publicação MQTT. | [RN01](01-regras-de-negocio.md), [RN04](01-regras-de-negocio.md), [RNF01](03-requisitos-nao-funcionais.md), [RNF02](03-requisitos-nao-funcionais.md) |
| **Sensoriamento de Presença (*Gatilho*)** | **Sensor Fotoelétrico Infravermelho E18-D80NK (NPN, 3 a 80 cm)** | Detecção determinística da passagem física do frasco na esteira para disparar o gatilho de captura na câmera via GPIO. | [RN01](01-regras-de-negocio.md), [RNF08](03-requisitos-nao-funcionais.md) |
| **Aquisição de Imagem** | **Câmera Digital (Raspberry Pi Camera Module v2/v3 ou Câmera USB HD)** | Captura instantânea e sincronizada da imagem do recipiente posicionado no plano focal de teste. | [US01](02-requisitos-funcionais.md), [RNF05](03-requisitos-nao-funcionais.md), [RNF09](03-requisitos-nao-funcionais.md) |
| **Visão Computacional & IA** | **Python 3, OpenCV e Modelo Classificador (TensorFlow Lite / YOLOv8n / MobileNet)** | Classificação nas classes `CONFORME`, `SEM_TAMPA`, `TAMPA_TORTA` e `AMASSADO`, alinhadas ao coletor do dataset. | [US01](02-requisitos-funcionais.md), [RNF06](03-requisitos-nao-funcionais.md), [RNF07](03-requisitos-nao-funcionais.md) |
| **Persistência Local (*Offline-First*)** | **SQLite (Banco de Dados Relacional Embutido / ACID)** | Armazenamento persistente e transacional de todos os eventos de inspeção, métricas de lote e fila de sincronização em caso de queda de rede. | [RN04](01-regras-de-negocio.md), [RN08](01-regras-de-negocio.md), [RN10](01-regras-de-negocio.md), [RNF03](03-requisitos-nao-funcionais.md) |
| **Protocolo de Comunicação IoT** | **MQTT (Paho-MQTT client via Wi-Fi TCP/IP)** | Publicação assíncrona orientada a eventos e telemetria dos dados inspecionados para o broker central e dashboard. | [RNF04](03-requisitos-nao-funcionais.md), [US03](02-requisitos-funcionais.md), [US05](02-requisitos-funcionais.md) |
| **Backend e dados** | **Python 3 + FastAPI + Paho-MQTT + SQLite** | Mantém em Python o consumo MQTT, a validação, a persistência, as consultas e a entrega de eventos por REST/SSE, no mesmo ecossistema do modelo de visão computacional. | [US02](02-requisitos-funcionais.md), [US03](02-requisitos-funcionais.md), [US04](02-requisitos-funcionais.md), [RNF11](03-requisitos-nao-funcionais.md) |
| **Frontend web** | **JavaScript + React + Chart.js + Lucide + SCSS** | Exibe indicadores, gráficos, histórico e alarmes consumindo exclusivamente a API do backend. | [US02](02-requisitos-funcionais.md), [US03](02-requisitos-funcionais.md), [US04](02-requisitos-funcionais.md), [RNF11](03-requisitos-nao-funcionais.md) |

---

## 🔍 Justificativa das Escolhas Tecnológicas

### 1. Gatilho Físico com Sensor Fotoelétrico E18-D80NK
* **Desafio:** Garantir que a câmera capture a foto no instante milimétrico em que a peça passa pelo centro do foco, sem sobrecarregar a CPU com processamento contínuo de vídeo.
* **Justificativa:** O sensor **E18-D80NK** é o padrão de esteiras industriais. Por possuir saída digital NPN direta e tempo de resposta inferior a 2 ms, ele gera uma interrupção precisa na GPIO da Raspberry Pi 5. Com o potenciômetro de calibração traseiro e um filtro de *debounce* de 30-100 ms ([RNF08](03-requisitos-nao-funcionais.md)), ele ignora reflexões do fundo da bancada e vibrações mecânicas da esteira.

### 2. Processamento em Borda (*Edge AI*) com Raspberry Pi 5
* **Desafio:** A esteira opera a 30 recipientes por minuto, exigindo latência ponta a ponta menor que 500 ms ([RNF01](03-requisitos-nao-funcionais.md)).
* **Justificativa:** A inferência local na Raspberry Pi 5 elimina o tráfego de imagens em tempo real na rede da fábrica, garantindo decisão instantânea e imunidade total a oscilações ou quedas de internet ([RN04](01-regras-de-negocio.md)).

### 3. Persistência Local com Banco Embutido SQLite
* **Desafio:** Assegurar a integridade transacional dos registros de inspeção durante paradas bruscas de energia e reter eventos por no mínimo 30 dias durante quedas de rede ([RNF03](03-requisitos-nao-funcionais.md), [RN10](01-regras-de-negocio.md)).
* **Justificativa:** O **SQLite** é um banco de dados relacional embutido (*serverless*), sem processo de servidor separado e com baixo consumo de memória, armazenamento e processamento. O acesso local evita latência de rede e oferece desempenho adequado ao volume do protótipo em uma Raspberry Pi. Sua conformidade **ACID** e o modo *Write-Ahead Logging* (WAL) preservam a integridade das gravações e permitem que o dashboard consulte dados enquanto novas inspeções são registradas. O campo `sync_status` (`PENDENTE | SINCRONIZADO`) controla a retransmissão ordenada ao broker MQTT ([RNF04](03-requisitos-nao-funcionais.md)).
* **Alternativa de evolução:** O **PostgreSQL** deve ser avaliado caso o Vigi passe a centralizar dados de várias linhas ou tenha muitos acessos e gravações simultâneos. Ele oferece boa eficiência sob concorrência, controle de usuários e permissões, autenticação, conexões protegidas por TLS e recursos mais completos de administração e auditoria. Em contrapartida, exige um serviço de banco separado, configuração, manutenção e mais recursos computacionais. Por isso, o SQLite permanece mais adequado ao protótipo local e offline, enquanto o PostgreSQL é uma alternativa para uma implantação centralizada e de maior escala.

### 4. Protocolo de Comunicação MQTT vs API REST (HTTP)
* **Desafio:** Distribuir métricas de produção e alarmes sem reter o ciclo de inspeção e permitir que vários dispositivos consumam os mesmos eventos simultaneamente.
* **Escolha:** O **MQTT** foi escolhido para a comunicação entre os componentes IoT porque seu padrão *Publish/Subscribe* desacopla quem produz de quem consome os dados. O modelo publica cada resultado uma única vez no broker, que o distribui aos clientes inscritos. Assim, o backend FastAPI, um painel físico OLED e outros consumidores futuros podem receber o mesmo evento sem exigir alterações no código do modelo ou uma chamada HTTP separada para cada destino.
* **Justificativa:** Além de facilitar a inclusão de novos dispositivos, o MQTT possui baixo overhead, entrega assíncrona, níveis de qualidade de serviço (QoS), mensagem de última vontade (*LWT*) e reconexão. Essas características são adequadas à telemetria de dispositivos com recursos e conectividade limitados.
* **Papel do HTTP:** HTTP continua sendo utilizado entre o backend e o frontend. O FastAPI centraliza os eventos MQTT, aplica as regras de acesso e fornece REST/SSE ao dashboard React. Dessa forma, o navegador não precisa conhecer o broker nem as credenciais MQTT.

### 5. Backend Python com FastAPI
* **Desafio:** Integrar o resultado da inferência, a comunicação MQTT, a persistência e a API sem fragmentar a camada de dados entre linguagens diferentes.
* **Justificativa:** O **FastAPI** mantém o backend no ecossistema Python já utilizado pelo modelo de visão computacional. O backend concentra o cliente Paho-MQTT, as regras de validação, o acesso ao SQLite e a entrega de dados por REST/SSE. Isso reduz a duplicação de contratos e simplifica a integração entre o modelo e a API.

### 6. Frontend JavaScript com React
* **Desafio:** Construir um dashboard responsivo, atualizável em tempo real e fácil de evoluir sem acoplar a interface ao broker MQTT ou ao banco de dados.
* **Justificativa:** O **React** executa diretamente no navegador e permite organizar o dashboard em componentes reutilizáveis para indicadores, filtros, tabelas, gráficos e alertas. Seu ecossistema oferece integração madura com **Chart.js** para visualizações e **Lucide** para ícones SVG. O frontend utiliza apenas JavaScript e consome a API REST/SSE do FastAPI, preservando no backend Python toda a lógica e o acesso aos dados, com tempo de resposta $< 2\text{ s}$ ([RNF11](03-requisitos-nao-funcionais.md)).

---

## 🔗 Relação com a Arquitetura do Sistema

Para visualização do fluxo de dados e camadas de software, consulte o documento:
* [Diagrama Arquitetural do Vigi](../arquitetura/diagrama-arquitetural.md)
