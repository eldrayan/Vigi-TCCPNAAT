# Vigi

> **Sistema Embarcado para Inspeção e Triagem de Linhas de Envase**
> *Trabalho de Conclusão da Capacitação — PNAAT 2026 (FIT - Instituto de Tecnologia)*

---

## 🎯 Propósito do Sistema

O **Vigi** tem como propósito automatizar a inspeção visual e a triagem em tempo real de recipientes em esteiras de envase rápido, identificando preventivamente anomalias estruturais e defeitos de fechamento antes da etapa de empacotamento, de modo a evitar travamentos mecânicos no maquinário, desperdício de insumos por derramamento e paradas não programadas na linha de produção.

---

## 🏭 Descrição do Minimundo

Em uma fábrica com processo contínuo de envase e empacotamento, recipientes chegam à etapa final de embalagem apresentando anomalias estruturais e falhas de fechamento. A passagem dessas peças defeituosas gera travamentos mecânicos no maquinário de empacotamento secundário, exige paradas não programadas da linha, provoca derramamento de líquidos sobre a esteira e componentes elétricos, e resulta em perda de lotes e redução drástica da Eficiência Global do Equipamento (OEE).

Na solução proposta, o sistema **Vigi** atua como uma estação intermediária de inspeção não-intrusiva instalada na esteira de transporte. A passagem física de cada recipiente é detectada pelo sensor fotoelétrico infravermelho **E18-D80NK**, disparando a captura instantânea de imagem e a análise automatizada por visão computacional na borda (**Edge AI** com **Raspberry Pi 5**). Ao identificar uma não-conformidade, o sistema grava o evento no banco local **SQLite** e publica a telemetria e os alertas em tempo real via **MQTT** para supervisão no backend **FastAPI** e dashboard **React**.

---

## 🎯 Delimitação de Escopo (*Scope Boundaries*)

### Dentro do Escopo (*In-Scope*)

1. Detecção física determinística da passagem de recipientes na esteira de testes via sensor fotoelétrico infravermelho **E18-D80NK**.
2. Captura sincronizada de imagem do recipiente inspecionado no ponto focal.
3. Classificação automatizada entre recipientes conformes e não-conformes por visão computacional na borda (Edge AI na Raspberry Pi 5).
4. Persistência local transacional de eventos e histórico em banco embutido **SQLite** (*offline-first*).
5. Envio de telemetria e alertas via MQTT para o broker Mosquitto, com consumo pelo **FastAPI** e visualização no dashboard **React**.
6. Operação autônoma com sincronização de eventos pendentes após restabelecimento de conexão.

### Fora do Escopo (*Out-of-Scope*)

1. Atuação mecânica de braços ejetores, cilindros pneumáticos ou comandos de potência na bancada de testes.
2. Instalação e acionamento de atuadores físicos dedicados (torres luminosas e buzzers externos de painel).
3. Substituição de sistemas normatizados de segurança humana (NR-12).
4. Integração direta com sistemas corporativos de gestão (ERP/SAP).
5. Análise de parâmetros físico-químicos ou microbiológicos do líquido envasado.

---

## 🔄 Fluxo de Operação do Protótipo

Abaixo está representado o fluxo **proposto** de inspeção visual, processamento em borda, comunicação e consumo de dados do sistema **Vigi**. O diagrama descreve a arquitetura pretendida; não comprova a integração de todos os componentes.

```mermaid
flowchart LR
    R["Recipiente na bancada"] --> S["Sensor E18-D80NK"]
    R -->|imagem| C["Câmera CSI ou USB"]
    subgraph PI["Raspberry Pi 5 — processamento e serviços previstos"]
        G["GPIO / debounce"] -->|disparo| A["Aquisição Python / Picamera2 ou OpenCV"]
        A --> I["Pré-processamento / YOLOv8n-cls"]
        I -->|classe e score| D["Decisão / tratamento de baixa confiança"]
        D --> B[("SQLite — eventos locais")]
        D --> M["Publicador MQTT / Paho"]
        B -.->|eventos pendentes| M
        M --> Q["Broker Mosquitto"]
        Q --> F["FastAPI / consumidor MQTT"]
        B -->|histórico| F
    end
    S -->|presença| G
    C -->|quadro| A
    F -->|HTTP / REST / SSE na rede local| W["Navegador — dashboard React"]
```

A entrada é a presença física e a imagem do recipiente; o processamento produz uma classe (`CONFORME`, `SEM_TAMPA`, `TAMPA_TORTA` ou `AMASSADO`) e a decisão correspondente. As saídas previstas são eventos locais e informações de supervisão. A câmera também atende à coleta manual de imagens já disponível. Ver [arquitetura detalhada](docs/arquitetura/diagrama-arquitetural.md), [US01 e demais requisitos funcionais](docs/requisitos/02-requisitos-funcionais.md) e [requisitos técnicos](docs/requisitos/05-requisitos-tecnicos.md).

A figura complementar abaixo representa o fluxo do projeto:

<p align="center">
  <img src="https://github.com/user-attachments/assets/5762b59e-8d0c-4479-9b6d-737bdc7a3731" alt="Fluxo proposto do Vigi: sensor, câmera, Raspberry Pi, inferência, MQTT, persistência e supervisão" width="850">
</p>

A figura apresenta uma visão geral da proposta. O Mermaid acima detalha as relações: a visão computacional roda na Raspberry Pi, e a persistência local em SQLite deve funcionar independentemente da publicação MQTT. Os alertas sonoros e visuais são previstos na interface de supervisão; a ilustração não acrescenta torres luminosas ou buzzers físicos ao escopo.

1. **Sensor Fotoelétrico (E18-D80NK):** Detecta a presença física do recipiente na esteira e dispara o gatilho de hardware.
2. **Câmera Digital:** Realiza a captura sincronizada do quadro focal do frasco posicionado.
3. **Raspberry Pi 5 (Edge AI):** Executa o pipeline de **Visão Computacional** e modelo de classificação para identificação de não-conformidades.
4. **Comunicação MQTT:** Transmite assincronamente os eventos de inspeção e telemetria para o broker Mosquitto.
5. **Consumo dos Dados:**
   * **SQLite:** Persistência local transacional dos registros de inspeção (*offline-first* com retenção de 30 dias).
   * **Backend Python:** O FastAPI consome MQTT, acessa o SQLite e fornece dados ao dashboard por REST/SSE. A camada de dados permanece em Python para manter o mesmo ecossistema do modelo de visão computacional.
   * **Frontend JavaScript:** O React apresenta indicadores, gráficos e alarmes no navegador, sem acessar diretamente o broker ou o banco de dados.

### Separação da stack

A arquitetura prevê **Python** para processamento de imagens, inferência do modelo, comunicação MQTT, persistência e API. Essa escolha reduz a quantidade de tecnologias na camada de dados e facilita o compartilhamento de modelos, validações e contratos entre o processamento em borda e o backend.

Para o frontend, estão previstos **JavaScript** e **React**. O React permite dividir o dashboard em componentes reutilizáveis, atualizar apenas os elementos afetados por novos eventos e integrar bibliotecas maduras como **Chart.js** e **Lucide**. Como o código é executado no navegador, o dashboard não adiciona uma segunda linguagem ao processamento de dados da Raspberry Pi.

---

## 👥 Equipe de Desenvolvimento

* **Alan Mendes Vieira**
* **Elder Rayan Oliveira Silva**
* **Leoncio Ferreira Flores Neto**
* **Samuel Wagner Tiburi Silveira**

---

## 📁 Estrutura do Repositório

```text
├── docs/
│   ├── arquitetura/diagrama-arquitetural.md # Arquitetura proposta
│   ├── img/                               # Fluxo e logos em logos/
│   ├── pitch/01-roteiro-pitch.md           # Entrega 3: pitch de até 15 min
│   ├── poc/01-roteiro-video-poc.md         # Entrega 2: PoC de cerca de 5 min
│   ├── requisitos/                        # Regras e requisitos do sistema
│   └── REPORTS.md                         # Contratos e leitura dos relatórios
├── edge/
│   ├── config.py                          # Configuração do coletor
│   ├── acquisition/backends/              # Picamera2 e OpenCV/USB
│   ├── collection/                        # Controle, estado, imagens e manifesto
│   │   └── views/                         # Interfaces gráfica e terminal
│   ├── inference/                         # Adaptador, motor e decisão da inferência
│   ├── tools/collect_dataset.py           # Composição do coletor
│   └── tests/                             # Testes do coletor
├── model_lifecycle/                       # Dataset, avaliação, métricas e promoção
├── scripts/
│   ├── coletar_dataset.py
│   ├── verificar_ambiente.py
│   ├── validar_dataset.py
│   ├── treinar_modelo.py
│   ├── avaliar_modelo.py
│   ├── quality_gate.py
│   ├── promover_modelo.py
│   ├── inferir.py
│   └── benchmark_modelo.py
├── tests/                                # Testes do modelo e das CLIs
├── training_configuration/               # Configurações baseline e tuned
├── dataset/vigi-cls.dvc                   # Ponteiro do dataset no DVC
├── models.dvc                            # Ponteiro dos modelos no DVC
├── .dvc/config                           # Configuração do armazenamento remoto
├── .github/workflows/mlops-ci.yml         # Qualidade e validação de artefatos
├── pyproject.toml                        # Dependências, extras e ferramentas
├── uv.lock                               # Versões resolvidas do ambiente
├── requirements.txt                      # Entrada pip para o projeto
├── TODO.md                               # Pendências técnicas
├── .gitignore
└── README.md
```

---

## 📦 Dependências e estado da implementação — Entrega 4

O repositório contém o coletor de imagens, o ciclo de treinamento, avaliação e promoção do modelo, além da inferência por imagem ou captura de câmera e do benchmark. Os módulos estão em `edge/`, `model_lifecycle/` e `scripts/`. Dataset e modelos são versionados por DVC; os ponteiros estão no Git, e os arquivos precisam ser recuperados do armazenamento remoto. A existência do código não substitui a validação física da inferência na Raspberry Pi.

A integração do sensor ao ciclo, a persistência das inspeções em SQLite, o MQTT, a API e o dashboard continuam previstos. A captura disponível na CLI é iniciada manualmente e executa uma inspeção por chamada.

### Operação local, case e supervisão

A arquitetura prevê que a Raspberry Pi execute a inspeção, a decisão e o armazenamento dos eventos localmente, com funcionamento independente de internet e sem envio de imagens à nuvem para inferência. Conforme a [RN04](docs/requisitos/01-regras-de-negocio.md), essas funções deverão continuar operando mesmo sem conexão com uma rede externa. A operação offline será testada de acordo com o [RNF03](docs/requisitos/03-requisitos-nao-funcionais.md), incluindo a continuidade das inspeções e a preservação dos registros locais.

Está prevista uma case para acomodar a Raspberry Pi e a câmera na bancada. A instalação também deverá considerar o sensor, a alimentação, os cabos, a fixação e a área necessária à captura das imagens. A disposição dos componentes e as dimensões do conjunto serão registradas durante a validação da montagem.

O dashboard está previsto para reunir resultados, histórico e alarmes para operadores e supervisores. O acesso por outros dispositivos será feito pela rede local, mediante conexão com a Raspberry Pi, sem necessidade de internet. Sua implementação deverá incluir autenticação dos usuários e autorização para controlar o acesso às informações e às funções disponíveis. Esses controles e a integração do painel com os eventos de inspeção serão implementados e verificados nas etapas correspondentes do projeto.

O [roteiro do pitch](docs/pitch/01-roteiro-pitch.md) e o [roteiro da PoC](docs/poc/01-roteiro-video-poc.md) organizam a apresentação dos componentes conforme o andamento da implementação.

### Hardware, plataformas e ferramentas

| Recurso | Função | Preparação / estado |
| --- | --- | --- |
| Raspberry Pi 5, fonte adequada e armazenamento para SO/dataset | Nó de borda | Plataforma alvo; validação física pendente nesta revisão documental |
| Raspberry Pi OS de 64 bits e Python 3.11 ou 3.12 | Ambiente do coletor | Faixa do projeto: `>=3.11,<3.13`; usar Python 3.12 para treinamento e registrar a versão do sistema na Pi |
| Câmera CSI compatível ou webcam USB | Entrada de imagens | Backends implementados em [edge/acquisition](edge/acquisition) |
| Case para Raspberry Pi e câmera | Acomodação do conjunto na bancada | Informada pela equipe; conteúdo, dimensões e montagem a confirmar no ensaio |
| Bancada, recipientes e iluminação estável | Aquisição de amostras | Preparar antes da coleta e dos vídeos |
| E18-D80NK e interface elétrica compatível com GPIO | Gatilho da inspeção | Integração prevista; coletor atual usa comandos manuais |
| Wi-Fi/Ethernet e navegador | Supervisão na rede local | Previstos para acesso ao backend/dashboard |
| Git | Obtenção e versionamento do código | Instalação inicial abaixo |
| uv | Gerenciamento do ambiente Python | Dependências em `pyproject.toml` e versões em `uv.lock` |
| DVC com suporte SSH e acesso ao storage | Recuperação e versionamento de dataset/modelos | Extra `mlops`; acesso e chave configurados localmente |
| GitHub Actions e Tailscale | CI e acesso do workflow aos artefatos | Workflow em `.github/workflows/mlops-ci.yml`; requer os secrets descritos abaixo |
| Google Colab com GPU e dataset particionado | Treinamento do classificador | Ambiente possível de treinamento; scripts e configurações também estão disponíveis para execução local |
| Pesos treinados e imagens de avaliação | Inferência e validação | Ponteiro `models.dvc` disponível; recuperar os arquivos e conferir `models/active/manifest.json` antes do ensaio |
| Node.js e npm | Preparação/build do frontend | Previstos; versão e manifesto serão definidos com o frontend |
| Gravação de tela/bancada e YouTube | Produção do vídeo da PoC | Publicação não listada conforme Entrega 2 |

### Bibliotecas e serviços

| Dependência | Papel / relação com a arquitetura | Situação e forma de obtenção |
| --- | --- | --- |
| OpenCV (`cv2`) | Captura USB, qualidade, gravação e interface do coletor | Coletor via `python3-opencv` no sistema; no ambiente do projeto, `opencv-python` também é dependência transitiva do Ultralytics |
| Picamera2 / libcamera | Captura CSI | Atual, para CSI; `python3-picamera2` via apt e dependências do sistema |
| `unittest`, `csv`, `pathlib` e demais módulos padrão | Testes, manifesto e arquivos | Incluídos no Python, sem instalação pip |
| Ultralytics / YOLOv8n-cls | Treinamento e inferência | Implementados; runtime atual usa checkpoints `.pt`. TFLite não é suportado pelo fluxo atual de promoção |
| NumPy, Pillow e PyYAML | Arrays, imagens e configurações | Dependências diretas em `pyproject.toml` |
| Matplotlib | Gráficos do treinamento | Extra `train` |
| DVC (`dvc[ssh]`) | Artefatos no storage remoto | Extra `mlops` |
| pytest e Ruff | Testes e lint | Grupo `dev` |
| GPIO Zero (`gpiozero`) | Leitura do sensor | Previsto; backend e compatibilidade com Pi 5 a validar na integração |
| SQLite / `sqlite3` | Persistência dos eventos e fila de sincronização | Previsto; módulo incluído no Python, sem pacote pip `sqlite3` |
| Paho MQTT (`paho-mqtt`) | Publicação e consumo dos eventos | Previsto; pacote Python |
| Mosquitto | Broker local de mensagens | Previsto; serviço do sistema, não pacote Python |
| FastAPI e Uvicorn | API e servidor para supervisão | Previstos; pacotes Python |
| React, Chart.js, Lucide e Sass/SCSS | Interface, gráficos, ícones e estilos | Previstos; dependências do futuro manifesto do frontend |

O [pyproject.toml](pyproject.toml) é a fonte das dependências Python do projeto; o [uv.lock](uv.lock) registra as versões resolvidas. O [requirements.txt](requirements.txt) aponta para o projeto local como alternativa de instalação via pip, sem duplicar a lista. Para reproduzir o ambiente, use os comandos com `uv sync --frozen` abaixo. Picamera2 e libcamera continuam sendo pacotes do sistema. As dependências dos serviços futuros serão incorporadas quando seus módulos forem implementados.

### Preparação do coletor na Raspberry Pi

1. Preparar o Raspberry Pi OS de 64 bits e conectar a câmera com a placa desligada.
   Para a coleta atual, o sensor de presença não é necessário.
2. No terminal da Raspberry Pi, instalar as dependências do coletor pelo sistema:

   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-picamera2 python3-opencv
   ```

3. Obter o repositório e entrar na raiz (se já tiver um checkout, usá-lo):

   ```bash
   git clone https://github.com/eldrayan/Vigi-TCCPNAAT.git
   cd Vigi-TCCPNAAT
   ```

4. Conferir o Python, as bibliotecas e os argumentos disponíveis:

   ```bash
   python3 --version
   python3 -c "import cv2; from picamera2 import Picamera2; print('Bibliotecas disponíveis')"
   python3 scripts/coletar_dataset.py --help
   ```

5. Executar a coleta conforme a seção seguinte. Conferir a criação de JPEGs e do manifesto após uma captura válida. A importação acima não valida a câmera fisicamente; a captura na bancada é necessária.

Este caminho usa o Python do sistema. Não é necessário executar `pip install -r requirements.txt` por cima dos pacotes apt da câmera/OpenCV.
A instalação via apt segue a [orientação oficial do Picamera2](https://github.com/raspberrypi/picamera2#installation), que prioriza a compatibilidade com libcamera.

### Verificação local e limites do manual

Na raiz do projeto, os testes existentes podem ser executados com:

```bash
python3 -m unittest discover -s edge/tests -v
```

Para executar a suíte completa sem instalar o runtime de treinamento, com `uv` disponível:

```bash
uv sync --frozen --only-group dev
uv run --no-sync python -m pytest
uv run --no-sync ruff check .
```

Os testes não substituem a captura física, a avaliação do modelo nem o teste do sistema completo. O requisito RNF12 de preparação em até 60 minutos ainda exige um ensaio em ambiente limpo com outra pessoa. A preparação do coletor está acima; treinamento, inferência e recuperação dos artefatos estão nas seções seguintes. As instruções dos serviços de supervisão serão acrescentadas com suas implementações.

---

## 📷 Coleta do Dataset na Raspberry Pi

O coletor serve exclusivamente para adquirir e organizar as imagens. Ele não
executa YOLO, inferência, treinamento ou classificação local. O backend padrão
usa a API `Picamera2` para ler diretamente a câmera CSI conectada à Raspberry
Pi; os JPEGs resultantes podem ser enviados posteriormente à plataforma externa
de classificação escolhida.

Após concluir a preparação inicial, use os comandos abaixo no Python do sistema.

Execute o coletor a partir da raiz do repositório:

```bash
python3 scripts/coletar_dataset.py --width 1280 --height 720
```

Quando executado por SSH ou em outro terminal sem ambiente gráfico, o coletor
detecta a ausência de `DISPLAY`/Wayland e ativa automaticamente o modo terminal.
Nesse modo, as mesmas teclas funcionam sem precisar pressionar `ENTER`, mas a
mira não é exibida. Também é possível forçar esse comportamento:

```bash
python3 scripts/coletar_dataset.py --headless --width 1280 --height 720
```

Para visualizar a mira, execute o comando em um terminal aberto na área de
trabalho gráfica da própria Raspberry Pi.

Para uma webcam USB, use:

```bash
python3 scripts/coletar_dataset.py --backend opencv --camera 0
```

Controles da janela:

| Tecla | Ação |
| :---: | :--- |
| `1`–`4` | Seleciona `conforme`, `sem_tampa`, `tampa_torta` ou `amassado` |
| `ESPAÇO` | Captura uma imagem |
| `B` | Liga ou desliga o modo burst |
| `N` | Inicia o registro de uma nova garrafa física |
| `C` | Alterna entre quadro completo e recorte da região guia |
| `Q` ou `ESC` | Encerra a coleta com segurança |

As imagens são gravadas em `dataset/raw/<classe>/`, nas pastas `01_conforme`,
`02_sem_tampa`, `03_tampa_torta` e `04_amassado`, conforme o
[estado da coleta](edge/collection/state.py). Esses nomes de diretório devem ser
conferidos com o mapeamento de classes do modelo exportado. O arquivo
`dataset/raw/manifest.csv` registra a sessão e a garrafa física de cada imagem.
Pressione `N` sempre que trocar a garrafa real: essa identificação permite que
o particionamento mantenha imagens correlacionadas no mesmo subconjunto e evita
vazamento entre treino e validação.

---

## 🧠 Treinamento e MLOps do classificador

O treinamento consome o dataset que já foi particionado e aumentado na
plataforma externa. Este repositório **não monta splits nem aplica data
augmentation adicional**. A estrutura esperada é:

```text
dataset/vigi-cls/
├── train/{01_conforme,02_sem_tampa,03_tampa_torta,04_amassado}/
├── val/{01_conforme,02_sem_tampa,03_tampa_torta,04_amassado}/
└── test/{01_conforme,02_sem_tampa,03_tampa_torta,04_amassado}/
```

### Ambiente local

Instale o `uv` conforme sua [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/). Para treinamento, use Python 3.12 e instale os grupos necessários:

```bash
uv python install 3.12
uv sync --frozen --python 3.12 --extra train --extra mlops --group dev
uv run python scripts/verificar_ambiente.py
```

O preflight confirma a versão do Python, a disponibilidade de CUDA no PyTorch,
o DVC e o SSH antes de iniciar um treinamento longo.

### Versionamento dos artefatos

O Vigi reutiliza o mesmo storage remoto do `yolo-edge-api`:

```ini
[core]
    remote = local_remote
['remote "local_remote"']
    url = ssh://alan@100.67.236.30/home/alan/dvc-storage
```

Os ponteiros `dataset/vigi-cls.dvc` e `models.dvc` já estão versionados. Para consumir os artefatos, configure uma chave autorizada apenas localmente e recupere os arquivos:

```bash
uv run dvc remote modify --local local_remote keyfile /caminho/para/chave
uv run dvc pull dataset/vigi-cls.dvc models.dvc
```

O acesso ao storage exige conectividade com o endereço configurado e credenciais válidas. Para atualizar o dataset como responsável pela publicação, valide e envie os artefatos:

```bash
uv run dvc remote modify --local local_remote keyfile /caminho/para/chave
uv run python scripts/validar_dataset.py --dataset dataset/vigi-cls
uv run dvc add dataset/vigi-cls
uv run dvc push dataset/vigi-cls.dvc
git add dataset/vigi-cls.dvc .gitignore
```

Depois que modelos candidatos ou o modelo ativo existirem:

```bash
uv run dvc add models
uv run dvc push models.dvc
git add models.dvc .gitignore
```

Os arquivos binários nunca devem ser adicionados diretamente ao Git.

### Fine-tuning e avaliação

Execute a baseline e a configuração ajustada separadamente:

```bash
uv run python scripts/treinar_modelo.py \
  --dataset dataset/vigi-cls \
  --config training_configuration/training-baseline.yaml

uv run python scripts/treinar_modelo.py \
  --dataset dataset/vigi-cls \
  --config training_configuration/training-tuned.yaml
```

Calibre o limiar somente no split de validação e depois avalie uma única vez no
teste. A opção escolhida define o split automaticamente, sem permitir que o
usuário combine modos e splits incompatíveis:

```bash
uv run python scripts/avaliar_modelo.py \
  --model models/candidates/vigi-yolov8n-cls-tuned.pt \
  --dataset dataset/vigi-cls \
  --calibrate \
  --output reports/calibration

uv run python scripts/avaliar_modelo.py \
  --model models/candidates/vigi-yolov8n-cls-tuned.pt \
  --dataset dataset/vigi-cls \
  --calibration-report reports/calibration/metrics.json \
  --output reports/model-gate
```

`--calibrate` usa internamente o split `val`. `--calibration-report` usa o split
`test` e reaproveita automaticamente o limiar produzido pela calibração. O gate
exige acurácia de pelo menos 90%, falsos negativos de no máximo 10% e falsos
positivos de no máximo 15%. Com menos de 200 imagens de teste, o relatório é
marcado como provisório.

Promova somente um modelo aprovado:

```bash
uv run python scripts/promover_modelo.py \
  --model models/candidates/vigi-yolov8n-cls-tuned.pt \
  --metrics reports/model-gate/metrics.json
```

A promoção suporta somente checkpoints PyTorch `.pt` e usa obrigatoriamente o
`quality_gate.confidence_threshold` registrado no relatório final.

### Inferência e benchmark na Raspberry Pi 5

Para câmera CSI, o ambiente precisa acessar Picamera2 e libcamera instalados no SO. Use o Python do sistema, na faixa 3.11 ou 3.12 exigida pelo projeto. Se a versão do SO estiver fora dessa faixa, a compatibilidade precisa ser resolvida antes da execução; instalar outro interpretador não transfere os bindings da câmera.

Em um checkout novo na Pi, sem `.venv`, após instalar os pacotes de câmera e o `uv`:

```bash
/usr/bin/python3 --version
uv venv --python /usr/bin/python3 --system-site-packages
uv sync --frozen --extra mlops
uv run --no-sync python -c "import cv2; from picamera2 import Picamera2; print('Bibliotecas disponíveis')"
```

Se já existir um ambiente de treinamento, use outro checkout para preparar o ambiente da câmera. A opção `--system-site-packages` permite acessar os pacotes do sistema, conforme a [documentação do uv](https://docs.astral.sh/uv/reference/cli/#uv-venv). A importação e a compatibilidade entre as bibliotecas devem ser verificadas na Pi; estes comandos ainda precisam de ensaio físico.

Recupere os artefatos pelo DVC como descrito acima. Com `models/active/manifest.json` e os pesos disponíveis, classifique uma imagem ou capture um quadro da câmera CSI:

```bash
uv run python scripts/inferir.py \
  --manifest models/active/manifest.json \
  --image imagem.jpg

uv run python scripts/inferir.py \
  --manifest models/active/manifest.json \
  --camera 0 --backend picamera2
```

A CLI executa uma inspeção por chamada e imprime a decisão em JSON. Ela não inicia um fluxo contínuo, uma janela de preview ou um dashboard.

O benchmark mede o tempo da chamada de predição do classificador, sem a detecção pelo sensor, a captura da câmera e a entrega ao dashboard. Portanto, é uma medição parcial e não comprova sozinho o RNF01 ponta a ponta. Ele descarta o aquecimento das estatísticas, reprova qualquer erro de
inferência e exige que pelo menos 95% das medições terminem em até 500 ms, sem
nenhuma ultrapassar 1.000 ms:

```bash
uv run python scripts/benchmark_modelo.py \
  --manifest models/active/manifest.json \
  --images dataset/vigi-cls/test \
  --runs 100 --warmup 10 \
  --output reports/benchmark-pi.json
```

### Relatórios e artefatos gerados

| Artefato | Finalidade |
| --- | --- |
| `best.pt` | Melhor estado aprendido pelo modelo durante o treinamento |
| `vigi-training-summary.json` | Registra como o treinamento foi executado |
| `predictions.csv` | Resultado individual da classificação de cada imagem |
| `metrics.json` | Qualidade agregada e limiar de confiança avaliado |
| `confusion-matrix.png` | Diagnóstico visual dos erros entre classes |
| `manifest.json` | Contrato do modelo que será usado em produção |
| `benchmark-pi.json` | Desempenho temporal do modelo no hardware de borda |

Consulte [`docs/REPORTS.md`](docs/REPORTS.md) para entender como cada arquivo é
produzido e utilizado no ciclo de treinamento, avaliação e promoção do modelo.

### Pipeline do GitHub Actions

O workflow `.github/workflows/mlops-ci.yml` executa três gates encadeados:

1. **Lint & Tests:** Ruff, testes e smoke das CLIs, sem acessar o Pi.
2. **ML Artifact Check:** conecta ao Tailscale, recupera dataset/modelos pelo
   DVC e valida a integridade dos artefatos.
3. **Model Quality Gate:** reavalia o modelo ativo no conjunto de teste e
   publica métricas e matriz de confusão como artifact do workflow.

Configure no GitHub os secrets `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`,
`RPI_SSH_KEY` e `RPI_KNOWN_HOSTS`. O primeiro secret SSH contém a chave privada
do cliente de CI; o segundo contém a chave pública de host da Raspberry Pi no
formato de `known_hosts`. Enquanto `dataset/vigi-cls.dvc` e `models.dvc` ainda não
existirem, os dois gates de ML informam que aguardam os primeiros artefatos e
encerram com sucesso. Não há Docker, publicação no GHCR ou deploy automático na
Raspberry Pi nesta etapa.

---

## 🎬 Entregas e documentação

| Entrega | Artefato / localização | Estado nesta revisão |
| --- | --- | --- |
| 2 — Apresentação da PoC | [Roteiro da demonstração de cerca de 5 min](docs/poc/01-roteiro-video-poc.md) | Roteiro preparado; ensaio, vídeo não listado e link pendentes |
| 3 — Esboço do vídeo pitch | [Roteiro textual do vídeo final de até 15 min](docs/pitch/01-roteiro-pitch.md) | Quatro partes com conteúdo, tempo e demonstração reservada; validação da equipe pendente |
| 4 — Esboço da documentação | Este README, [pyproject.toml](pyproject.toml), [uv.lock](uv.lock), [requirements.txt](requirements.txt), [arquitetura](docs/arquitetura/diagrama-arquitetural.md) e [requisitos](docs/requisitos) | Estrutura, blocos, dependências e preparação inicial documentados; validação física pendente |

**São dois vídeos diferentes:** a demonstração da PoC e o pitch final. A Entrega 3 solicita o texto que planeja o pitch; sua demonstração ocupa um bloco próprio dentro dos 15 minutos. Os documentos integram o trabalho da [issue #13](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13), sem declarar sua conclusão ou a validação pelo squad. A menção a Node-RED no texto da issue não corresponde à arquitetura atual, que prevê FastAPI e React.

Para localizar os materiais por tópico: regras em [01-regras-de-negocio.md](docs/requisitos/01-regras-de-negocio.md), comportamento em [02-requisitos-funcionais.md](docs/requisitos/02-requisitos-funcionais.md), critérios de validação em [03-requisitos-nao-funcionais.md](docs/requisitos/03-requisitos-nao-funcionais.md) e recursos em [05-requisitos-tecnicos.md](docs/requisitos/05-requisitos-tecnicos.md).
Os módulos de aquisição, coleta e inferência estão em `edge/`, e o ciclo do modelo está em `model_lifecycle/`. As imagens brutas da coleta são geradas em execução; o dataset de classificação e os modelos têm ponteiros DVC versionados, com binários fora do Git. Não há pastas de backend ou frontend implementadas neste checkout.

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e educacionais no âmbito do programa PNAAT 2026. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
