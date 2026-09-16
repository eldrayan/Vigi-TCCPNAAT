# Vigi

> **Sistema Embarcado para Inspeção e Triagem de Linhas de Envase**
> *Trabalho de Conclusão da Capacitação — PNAAT 2026 (FIT - Instituto de Tecnologia)*

---

## 🎯 Propósito do Sistema

O **Vigi** tem como propósito automatizar a inspeção visual e a triagem em tempo real de recipientes em esteiras de envase rápido, identificando preventivamente anomalias estruturais e defeitos de fechamento antes da etapa de empacotamento, de modo a evitar travamentos mecânicos no maquinário, desperdício de insumos por derramamento e paradas não programadas na linha de produção.

---

## 🏭 Descrição do Minimundo

Em uma fábrica com processo contínuo de envase e empacotamento, recipientes chegam à etapa final de embalagem apresentando anomalias estruturais e falhas de fechamento. A passagem dessas peças defeituosas gera travamentos mecânicos no maquinário de empacotamento secundário, exige paradas não programadas da linha, provoca derramamento de líquidos sobre a esteira e componentes elétricos, e resulta em perda de lotes e redução drástica da Eficiência Global do Equipamento (OEE).

O sistema **Vigi** atua como uma estação intermediária de inspeção não-intrusiva instalada na esteira de transporte. A passagem física de cada recipiente é detectada pelo sensor fotoelétrico infravermelho **E18-D80NK**, disparando a captura instantânea de imagem e a análise automatizada por visão computacional na borda (**Edge AI** com **Raspberry Pi 5**). Ao identificar uma não-conformidade, o sistema grava o evento no banco local **SQLite** e publica a telemetria e os alertas em tempo real via **MQTT** para supervisão no backend **FastAPI** e dashboard **React**.

---

## 🎯 Delimitação de Escopo (*Scope Boundaries*)

### Dentro do Escopo (*In-Scope*):
1. Detecção física determinística da passagem de recipientes na esteira de testes via sensor fotoelétrico infravermelho **E18-D80NK**.
2. Captura sincronizada de imagem do recipiente inspecionado no ponto focal.
3. Classificação automatizada entre recipientes conformes e não-conformes por visão computacional na borda (Edge AI na Raspberry Pi 5).
4. Persistência local transacional de eventos e histórico em banco embutido **SQLite** (*offline-first*).
5. Envio de telemetria e alertas via MQTT para o broker Mosquitto, com consumo pelo **FastAPI** e visualização no dashboard **React**.
6. Operação autônoma com sincronização de eventos pendentes após restabelecimento de conexão.

### Fora do Escopo (*Out-of-Scope*):
1. Atuação mecânica de braços ejetores, cilindros pneumáticos ou comandos de potência na bancada de testes.
2. Instalação e acionamento de atuadores físicos dedicados (torres luminosas e buzzers externos de painel).
3. Substituição de sistemas normatizados de segurança humana (NR-12).
4. Integração direta com sistemas corporativos de gestão (ERP/SAP).
5. Análise de parâmetros físico-químicos ou microbiológicos do líquido envasado.

---

## 🔄 Fluxo de Operação do Protótipo

Abaixo está representado o fluxo integrado de inspeção visual, processamento em borda, comunicação e consumo de dados do sistema **Vigi**:

<p align="center">
  <img src="docs/img/Fluxo.jpeg" alt="Fluxo Atualizado do Protótipo Vigi" width="850">
</p>

1. **Sensor Fotoelétrico (E18-D80NK):** Detecta a presença física do recipiente na esteira e dispara o gatilho de hardware.
2. **Câmera Digital:** Realiza a captura sincronizada do quadro focal do frasco posicionado.
3. **Raspberry Pi 5 (Edge AI):** Executa o pipeline de **Visão Computacional** e modelo de classificação para identificação de não-conformidades.
4. **Comunicação MQTT:** Transmite assincronamente os eventos de inspeção e telemetria para o broker Mosquitto.
5. **Consumo dos Dados:**
   * **SQLite:** Persistência local transacional dos registros de inspeção (*offline-first* com retenção de 30 dias).
   * **Backend Python:** O FastAPI consome MQTT, acessa o SQLite e fornece dados ao dashboard por REST/SSE. A camada de dados permanece em Python para manter o mesmo ecossistema do modelo de visão computacional.
   * **Frontend JavaScript:** O React apresenta indicadores, gráficos e alarmes no navegador, sem acessar diretamente o broker ou o banco de dados.

### Organização em monólito modular

O backend do Vigi adota a organização de um monólito modular: uma única aplicação FastAPI reúne as funções de negócio, separadas em módulos com responsabilidades definidas. O módulo de inspeções concentra rotas, validação dos dados, serviços e persistência em `backend/app/modules/inspections/`. Configuração, banco e comunicação MQTT ficam na infraestrutura compartilhada.

Essa organização permite documentar cada responsabilidade junto do código correspondente e facilita a manutenção, sem exigir um serviço independente para cada função de negócio. A divisão por fluxo de dados dos diagramas complementa essa visão, mostrando como as informações passam entre os componentes.

O Edge é um processo separado que publica eventos, e o Mosquitto é um serviço de infraestrutura. O termo monólito modular descreve a organização do backend; o sistema completo inclui esses componentes e o frontend React no navegador.

### Separação da stack

O processamento de imagens, a inferência do modelo, a comunicação MQTT, a persistência e a API são implementados em **Python**. Essa escolha reduz a quantidade de tecnologias na camada de dados e facilita o compartilhamento de modelos, validações e contratos entre o processamento em borda e o backend.

Somente o frontend é implementado em **JavaScript**, com **React**. O React permite dividir o dashboard em componentes reutilizáveis, atualizar apenas os elementos afetados por novos eventos e integrar bibliotecas maduras como **Chart.js** e **Lucide**. Como o código é executado no navegador, o dashboard não adiciona uma segunda linguagem ao processamento de dados da Raspberry Pi.

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
│   ├── arquitetura/            # Diagramas e especificações arquiteturais (Roger Pressman)
│   │   └── diagrama-arquitetural.md
│   ├── esquematico/            # Engenharia elétrica e esquemático da bancada
│   │   └── esquematico-eletrico.md
│   ├── img/                    # Diagramas visuais e esquemáticos do sistema
│   │   └── Fluxo.jpeg
│   └── requisitos/             # Especificação de Requisitos (IEEE 29148 / PNAAT)
│       ├── 01-regras-de-negocio.md
│       ├── 02-requisitos-funcionais.md
│       ├── 03-requisitos-nao-funcionais.md
│       └── 05-requisitos-tecnicos.md
├── edge/                        # Aplicação executada na Raspberry Pi
│   ├── config.py                # Configuração e argumentos do nó de borda
│   ├── acquisition/             # Contrato e backends de câmera
│   │   └── backends/            # Picamera2 e OpenCV/USB
│   ├── collection/              # Caso de uso de coleta do dataset
│   │   ├── controller.py        # Coordenação do fluxo de captura
│   │   ├── state.py             # Estado da sessão e classes
│   │   ├── image_store.py       # Gravação atômica dos JPEGs
│   │   ├── manifest.py          # Metadados da coleta
│   │   └── views/               # Interfaces OpenCV e terminal/SSH
│   ├── tools/
│   │   └── collect_dataset.py   # Composição da ferramenta
│   └── tests/                   # Testes unitários do Edge
├── model_lifecycle/             # Ciclo de vida do modelo de classificação
│   ├── inspection_classes.py    # Classes e códigos reconhecidos pelo Vigi
│   ├── dataset_validation.py    # Integridade e identificação do dataset
│   ├── model_evaluation.py      # Execução e relatórios da avaliação
│   ├── quality_metrics.py       # Métricas e critérios do quality gate
│   └── manifest.py              # Contrato do modelo promovido
├── scripts/
│   └── coletar_dataset.py       # Entrada compatível para a ferramenta modular
├── .gitignore
└── README.md
```

---

## 📷 Coleta do Dataset na Raspberry Pi

O coletor serve exclusivamente para adquirir e organizar as imagens. Ele não
executa YOLO, inferência, treinamento ou classificação local. O backend padrão
usa a API `Picamera2` para ler diretamente a câmera CSI conectada à Raspberry
Pi; os JPEGs resultantes podem ser enviados posteriormente à plataforma externa
de classificação escolhida.

No Raspberry Pi OS, instale as dependências no Python do sistema:

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv
```

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

As imagens são gravadas em `dataset/raw/<classe>/`. O arquivo
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

Use Python 3.12 e instale os grupos necessários com `uv`:

```bash
uv python install 3.12
uv sync --python 3.12 --extra train --group dev
uv run python scripts/verificar_ambiente.py
```

O preflight confirma a versão do Python, a disponibilidade de CUDA no PyTorch,
o DVC e o cliente DagsHub antes de iniciar um treinamento longo.

### Versionamento dos artefatos

O DagsHub é o único remoto DVC do projeto. Para publicar artefatos ou
baixá-los em um clone, siga [`docs/dvc-dagshub.md`](docs/dvc-dagshub.md).
O login do cliente DagsHub não é repassado automaticamente ao DVC: use o
script indicado no guia.

```ini
[core]
    remote = dagshub
[remote "dagshub"]
    url = s3://dvc
    endpointurl = https://dagshub.com/alan-mendes-ufca/Vigi-TCCPNAAT.s3
```

Para baixar dataset e modelos depois do clone:

```bash
uv sync
uv run dagshub login
uv run python scripts/dvc_dagshub.py pull
```

Somente mantenedores devem publicar novas versões. Para o dataset, valide
e envie nesta ordem:

```bash
uv run python scripts/validar_dataset.py --dataset dataset/vigi-cls
uv run dvc add dataset/vigi-cls
uv run python scripts/dvc_dagshub.py push dataset/vigi-cls.dvc
git add dataset/vigi-cls.dvc .gitignore
```

Depois que modelos candidatos ou o modelo ativo existirem:

```bash
uv run dvc add models
uv run python scripts/dvc_dagshub.py push models.dvc
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

Para câmera CSI, instale os pacotes do sistema conforme a seção do coletor e use o Python de `/usr/bin/python3`, na faixa 3.11 a 3.13 aceita pelo Edge. O backend usa Python 3.12 em seu próprio ambiente/container. O `make setup-rpi` cria `.venv` com acesso aos pacotes do sistema apenas se o diretório ainda não existir; um ambiente criado antes sem esse acesso precisa ser revisto antes de usar Picamera2.

A [documentação do uv](https://docs.astral.sh/uv/reference/cli/#uv-venv) descreve `--system-site-packages`. Instalar outro interpretador não transfere os bindings da câmera. A compatibilidade das bibliotecas deve ser testada na Pi.

Antes de iniciar o fluxo integrado, confira as ferramentas instaladas:

```bash
make --version
docker --version
docker compose version
curl --version
uv --version
```

## Reprodução ponta a ponta

Este roteiro reproduz o fluxo completo na Raspberry Pi: sensor → câmera →
inferência no Edge → MQTT autenticado → FastAPI/SQLite → dashboard React.
Execute todos os comandos a partir da raiz do repositório.

### 1. Preparar a Raspberry e o modelo

Instale Docker com Compose, `uv`, Git e os drivers da câmera CSI. A instalação
do Docker deve seguir a [documentação oficial](https://docs.docker.com/engine/install/).
Depois, prepare o ambiente Python do Edge e recupere os artefatos DVC:

```bash
make setup-rpi
make dvc-pull
```

Confirme que `models/active/manifest.json` existe antes de continuar.

### 2. Configurar as credenciais locais

Crie o arquivo local de configuração. Ele é ignorado pelo Git e nunca deve ser
enviado ao repositório:

```bash
cp .env.example .env
nano .env
```

Mantenha os nomes de usuário distintos e troque as duas senhas de exemplo por
valores fortes:

```env
MQTT_BACKEND_USERNAME=vigi-backend
MQTT_BACKEND_PASSWORD=troque-por-uma-senha-forte
MQTT_EDGE_USERNAME=vigi-edge
MQTT_EDGE_PASSWORD=troque-por-outra-senha-forte
```

O broker não aceita conexões sem credenciais. O Edge publica somente nos tópicos
da `ESTACAO_01`; o backend consome inspeções e estados do dispositivo.

### 3. Subir dashboard, API e broker

```bash
make up
make ps
curl -f http://localhost:8000/health
```

O Compose aplica as migrations automaticamente, mantém o SQLite em volume e
inicia o dashboard, FastAPI e Mosquitto. Na rede local, acesse:

```text
Dashboard: http://leocio-raspberry.local:8080
Swagger:   http://leocio-raspberry.local:8000/docs
```

Se o mDNS não estiver disponível, obtenha o endereço com `hostname -I` e use
`http://IP_DA_RASPBERRY:8080`. O dashboard encaminha API e SSE internamente;
por isso não exige configuração adicional de CORS nesse fluxo em containers.

O CORS só é necessário para desenvolvimento separado com Vite. Nesse caso,
inicie a API com `FRONTEND_ORIGINS=http://IP_DA_RASPBERRY:5173 make backend-up`
e o dashboard com `make frontend-up API_URL=http://IP_DA_RASPBERRY:8000`.

### 4. Iniciar a inspeção contínua

Em outro terminal na Raspberry, conecte o sensor E18-D80NK e a câmera e execute:

```bash
make edge-up HOST=localhost
```

O diagnóstico inicial confirma modelo, sensor, câmera e broker. Depois, cada
detecção do sensor captura uma imagem, executa a inferência, salva o evento na
outbox SQLite do Edge e o publica no MQTT. A migration cria a estação fixa
`ESTACAO_01` e o lote ativo `LOTE_01`.

### 5. Verificar a inspeção no dashboard e na API

Após passar um recipiente na esteira, confira a nova inspeção no dashboard ou
consulte a API:

```bash
curl -f 'http://localhost:8000/api/inspecoes?limit=10&offset=0'
curl -f http://localhost:8000/api/inspecoes/resumo
```

O histórico persistido inclui resultado, confiança e, quando não conforme, o
tipo da não conformidade. O dashboard recebe atualizações por SSE.

### 6. Testar sem o sensor ou a câmera

Para demonstrar o restante da esteira com uma imagem existente, sem hardware
de captura, execute:

```bash
make infer-image IMAGE=/caminho/imagem.jpg HOST=localhost
```

Para inspecionar os tópicos MQTT com autenticação, use:

```bash
make mqtt-sub TOPIC='vigi/estacoes/#' HOST=localhost
```

### 7. Parar com segurança

Interrompa o Edge com `Ctrl+C` e pare os containers sem remover os volumes:

```bash
make down
```

O histórico do backend e a outbox local do Edge são preservados. Para consultar
todos os atalhos disponíveis, execute `make help`.

Para executar somente a inferência local, sem publicação MQTT, use diretamente a CLI:

```bash
uv run python scripts/infer.py \
  --manifest models/active/manifest.json \
  --image imagem.jpg

uv run python scripts/infer.py \
  --manifest models/active/manifest.json \
  --camera 0 --backend picamera2
```

O benchmark descarta o aquecimento das estatísticas, reprova qualquer erro de
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

1. **Lint & Tests:** Ruff, testes e smoke das CLIs.
2. **ML Artifact Check:** recupera dataset/modelos do DagsHub pelo DVC e
   valida a integridade dos artefatos.
3. **Model Quality Gate:** reavalia o modelo ativo no conjunto de teste e
   publica métricas e matriz de confusão como artifact do workflow.

Configure no GitHub o secret `DAGSHUB_TOKEN` com um token do DagsHub para
leitura dos artefatos. Pull requests de forks externos executam apenas o job
de qualidade do código, pois não recebem secrets do repositório. Enquanto
`dataset/vigi-cls.dvc` e `models.dvc` não existirem, os dois gates de ML
informam que aguardam os primeiros artefatos e encerram com sucesso. Não há
Docker, publicação no GHCR ou deploy automático na Raspberry Pi nesta etapa.

---

## Esquema Elétrico da Bancada

O **Vigi** conta com projeto elétrico formal para validação e reprodutibilidade da bancada física:

<p align="center">
  <img src="docs/esquematico/VigiEsquematico.png" alt="Esquemático Elétrico da Bancada Vigi" width="850">
</p>

* **Esquemático Elétrico Detalhado:** Consulte [`docs/esquematico/esquematico-eletrico.md`](docs/esquematico/esquematico-eletrico.md) para ver o detalhamento completo do circuito (desenvolvido no Fritzing), mapeamento de pinagem da Raspberry Pi 5, circuito de proteção por divisor de tensão para o sensor industrial E18-D80NK (3.3V LVTTL), acionamento com isolamento galvânico do módulo relé de ejeção KY-019 e lista de materiais (BOM).

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e educacionais no âmbito do programa PNAAT 2026. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
