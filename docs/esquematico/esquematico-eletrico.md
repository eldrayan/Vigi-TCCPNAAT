> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase
> **Revisão:** 1.2.0
> **Responsável:** Squad Vigi (Lead: Elder Rayan Oliveira Silva)
> **Milestone:** Engenharia de Hardware e Esquemático Elétrico

> [!CAUTION]
> **Artefato candidato, ainda não aprovado para montagem.** O nível lógico e o
> dimensionamento da interface precisam ser conferidos contra o modelo exato do
> E18-D80NK, medições da bancada e documentação técnica dos componentes antes de
> energizar a GPIO. A versão final deverá registrar evidências do circuito
> realmente montado.

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **1.0.0** | Squad Vigi | 15/09/2026 | Elaboração inicial do circuito e dimensionamento de proteção GPIO. |
| **1.1.0** | Squad Vigi | 15/09/2026 | Atualização do esquemático da bancada PoC. |
| **1.2.0** | Squad Vigi | 16/09/2026 | Alinhamento ao escopo final: Raspberry Pi, câmera, sensor E18-D80NK e interface elétrica. |

---

## Visão Geral do Sistema Elétrico da Bancada (PoC)

O sistema elétrico da bancada de testes (Prova de Conceito - PoC) do **Vigi** integra os elementos do fluxo de inspeção em tempo real:
1. **Unidade Central de Processamento:** Raspberry Pi 5 (8GB), responsável pela execução do pipeline de inferência de visão computacional e pela orquestração da inspeção.
2. **Sensoriamento de Presença Industrial:** Sensor fotoelétrico infravermelho reflexivo **E18-D80NK** (saída NPN coletor aberto alimentada a 5V).
3. **Condicionamento de Nível Lógico (3,3V LVTTL):** Divisor resistivo ($R_{10} = 1\text{ k}\Omega$ e $R_{11} = 2.2\text{ k}\Omega$) para proteção da entrada digital da Raspberry Pi contra sobretensão.

---

## Esquemático Elétrico Oficial da Bancada

O circuito foi documentado no **Fritzing** para comparação com a montagem real.
A validação elétrica e física ainda precisa ser registrada antes da entrega final.

![Esquemático Elétrico Oficial](./VigiEsquematico.png)

* Arquivo de projeto Fritzing editável: [`VigiEsquematico.fzz`](./VigiEsquematico.fzz)

---

## Mapeamento de Conexões da Raspberry Pi 5 (Header de 40 Pinos)

Abaixo está o mapeamento detalhado de cada conexão realizada no header da Raspberry Pi 5:

| Pino Físico | Nome / Função BCM | Direção | Conexão de Destino | Função Técnica |
| :---: | :---: | :---: | :--- | :--- |
| **04** | **5.0V Power** | Saída | Alimentação do sensor E18-D80NK | Barramento de alimentação 5V DC |
| **09** | **GND** | Referência | Terminal 2 do Resistor $R_{11}$ ($2.2\text{ k}\Omega$) | Referência de terra do divisor de tensão |
| **11** | **GPIO 17** | **Entrada Digital** | Nó central do divisor (Terminal 2 de $R_{10}$ e Terminal 1 de $R_{11}$) | Sinal de gatilho do sensor com debounce de 50 ms (RNF08) |
| **34** | **GND** | Referência | Pino 2 do Sensor E18-D80NK | Referência de terra do sensor fotoelétrico |
| **Porta CSI / USB** | **Interface de Câmera** | Entrada de Dados | Módulo de Câmera (RPi Cam / USB) | Captura instantânea sincronizada da garrafa |

> [!NOTE]
> Conforme as diretrizes das páginas 19 e 20 da Apostila do PNAAT 2026, a documentação visual deve refletir estritamente o hardware funcional entregue na PoC para garantir total reprodutibilidade. Periféricos como o Display OLED SSD1306 e LEDs auxiliares de status constam na arquitetura conceitual para a fase de industrialização, não estando conectados nesta montagem para evitar inconsistência com o código em execução.

---

## Circuito de Proteção da GPIO (Divisor de Tensão)

### Dimensionamento Elétrico
O sensor **E18-D80NK** opera alimentado em **5V**. Sua saída NPN com pull-up envia sinal de 5V quando o feixe não está obstruído. Como as entradas GPIO da Raspberry Pi 5 toleram apenas **3,3V**, a ligação direta causaria queima do circuito de entrada do chip de I/O RP1 / Broadcom.

O divisor resistivo implementado utiliza resistores de precisão com os seguintes valores:
* $R_{10} = 1\text{ k}\Omega$ (ligado entre a saída do sensor e a GPIO 17)
* $R_{11} = 2.2\text{ k}\Omega$ (ligado entre a GPIO 17 e o terra GND)

$$V_{\text{GPIO17}} = V_{\text{IN}} \times \frac{R_{11}}{R_{10} + R_{11}} = 5\text{V} \times \frac{2.2\text{ k}\Omega}{1.0\text{ k}\Omega + 2.2\text{ k}\Omega} = 5\text{V} \times \frac{2.2}{3.2} \approx 3.43\text{V}$$

Com $R_{11} = 2.0\text{ k}\Omega$, a tensão resultante é de $3.33\text{V}$. Ambos os valores situam a tensão de nível alto perfeitamente dentro da margem de segurança do padrão LVTTL de 3,3V.

### Comportamento Lógico
* **Sem objeto (feixe livre):** A saída do sensor permanece em nível alto (5V). O divisor entrega aproximadamente 3,4V na GPIO 17 (Nível Lógico 1).
* **Com objeto (presença do frasco):** O transistor NPN do sensor satura, puxando a linha para 0V. A GPIO 17 detecta a borda de descida (Nível Lógico 0), disparando a interrupção determinística de captura (RN01).

---

## Lista de Componentes da Bancada (Bill of Materials - BOM)

| Item | Componente | Especificação | Qtd. | Função no Sistema |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **Raspberry Pi 5 (8GB)** | SBC ARM Cortex-A76 quad-core @ 2.4GHz | 1 | Processamento central, inferência Edge AI e orquestração |
| 2 | **Sensor E18-D80NK** | Sensor fotoelétrico reflexivo infravermelho NPN (3 a 80 cm) | 1 | Gatilho determinístico de posicionamento milimétrico do frasco |
| 3 | **Resistor 1.0 kΩ** | Resistor de precisão 1/4W (R10) | 1 | Resistor série da interface da GPIO |
| 4 | **Resistor 2.2 kΩ** | Resistor de precisão 1/4W (R11) | 1 | Resistor ligado ao GND na interface da GPIO |
| 5 | **Câmera RPi / USB** | Módulo de câmera compatível | 1 | Captura ótica no plano focal |
| 6 | **Fonte USB-C PD 27W** | Fonte regulada compatível com Raspberry Pi 5 | 1 | Alimentação primária da placa e periféricos |
| 7 | **Protoboard e jumpers** | Placa de prototipagem e cabos de conexão | 1 | Distribuição dos sinais e barramentos da bancada |

---

## Relação com os Requisitos do Projeto

* **RN01 — Disparo Determinístico:** Garantido pelo sensor E18-D80NK conectado na GPIO 17, permitindo capturar o frame exatamente quando o centro da garrafa cruza a linha de visão.
* **RN02 — Decisão Preventiva de Fail-Safe:** Em caso de falha de leitura ou baixa confiança, o software registra a inspeção como não conforme e publica o evento para supervisão.
* **RNF01 — Latência Ponta a Ponta < 500 ms:** Deve ser comprovada no hardware alvo considerando sensor, captura, inferência, persistência e publicação.
* **RNF08 — Filtro de Debounce de 30 a 100 ms:** Configurado em 50 ms no módulo `edge/acquisition/sensor.py`, eliminando falsos positivos originados por reflexos ou trepidação mecânica.
