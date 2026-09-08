# Vigi

> **Sistema Embarcado para Inspeção e Triagem de Linhas de Envase**  
> *Trabalho de Conclusão da Capacitação — PNAAT 2026 (FIT - Instituto de Tecnologia)*

---

## 🎯 Propósito do Sistema

O **Vigi** tem como propósito automatizar a inspeção visual e a triagem em tempo real de recipientes em esteiras de envase rápido, identificando preventivamente anomalias estruturais e defeitos de fechamento antes da etapa de empacotamento, de modo a evitar travamentos mecânicos no maquinário, desperdício de insumos por derramamento e paradas não programadas na linha de produção.

---

## 🏭 Descrição do Minimundo

Em uma fábrica com processo contínuo de envase e empacotamento, recipientes chegam à etapa final de embalagem apresentando anomalias estruturais e falhas de fechamento. A passagem dessas peças defeituosas gera travamentos mecânicos no maquinário de empacotamento secundário, exige paradas não programadas da linha, provoca derramamento de líquidos sobre a esteira e componentes elétricos, e resulta em perda de lotes e redução drástica da Eficiência Global do Equipamento (OEE).

O sistema **Vigi** atua como uma estação intermediária de inspeção não-intrusiva instalada na esteira de transporte. A passagem física de cada recipiente é detectada por sensoriamento, disparando a captura de imagem e a análise automatizada por visão computacional na borda (**Edge AI** com **Raspberry Pi 5**). Ao identificar uma não-conformidade, o sistema aciona a sinalização local, comanda o mecanismo de descarte da esteira e envia os dados do evento via MQTT para monitoramento em tempo real.

---

## 🎯 Delimitação de Escopo (*Scope Boundaries*)

### Dentro do Escopo (*In-Scope*):
1. Detecção física da passagem de recipientes na bancada de esteira de testes.
2. Captura sincronizada de imagem do recipiente inspecionado no ponto focal.
3. Classificação automatizada entre recipientes conformes e não-conformes por visão computacional na borda.
4. Atuação local de sinalização e envio de comando para mecanismo de descarte na bancada de testes.
5. Envio de telemetria de produção e eventos de refugo via MQTT para dashboard gerencial.
6. Operação autônoma com retenção local de eventos em caso de indisponibilidade de rede.

### Fora do Escopo (*Out-of-Scope*):
1. Atuação direta em circuitos de potência trifásica ou comandos de parada de motores industriais.
2. Substituição de sistemas normatizados de segurança humana (NR-12).
3. Integração direta com sistemas corporativos de gestão (ERP/SAP).
4. Análise de parâmetros físico-químicos ou microbiológicos do líquido envasado.

---

## 👥 Equipe de Desenvolvimento

* **Alan Mendes Vieira**
* **Elder Rayan Oliveira Silva**
* **Leoncio Ferreira Flores Neto**
* **Samuel Wagner Tiburi Silveira**

---

## 📁 Estrutura do Repositório

```text
├── .github/
│   └── workflows/              # Automações de CI e gerenciamento de dependências
├── docs/
│   └── requisitos/             # Especificação de Requisitos (IEEE 29148 / PNAAT)
│       ├── 01-regras-de-negocio.md
│       ├── 02-requisitos-funcionais.md
│       └── 03-requisitos-nao-funcionais.md
├── scripts/
│   └── coletar_dataset.py       # Captura assistida das imagens na Raspberry Pi
├── tests/
│   └── test_coletar_dataset.py  # Testes das regras do coletor
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
sudo apt install -y python3-picamera2 python3-opencv python3-numpy rpicam-apps
```

Teste primeiro se a câmera CSI está disponível:

```bash
rpicam-hello -t 3000
```

Execute o coletor a partir da raiz do repositório:

```bash
python3 scripts/coletar_dataset.py --width 1280 --height 720
```

O backend `rpicam` permanece disponível somente como alternativa caso a API
Picamera2 não possa ser utilizada. Para uma webcam USB, use:

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

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e educacionais no âmbito do programa PNAAT 2026. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
