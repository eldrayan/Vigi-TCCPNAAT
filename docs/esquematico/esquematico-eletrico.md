> **Projeto:** Vigi — Sistema Embarcado para Inspeção e Triagem de Linhas de Envase
> **Revisão:** 1.1.0
> **Responsável:** Squad Vigi (Lead: Elder Rayan Oliveira Silva)
> **Milestone:** Engenharia de Hardware e Esquemático Elétrico

> [!CAUTION]
> **Artefato candidato, ainda não aprovado para montagem.** A imagem e o arquivo
> Fritzing atuais incluem módulo relé KY-019 e atuação por solenoide, componentes
> fora do escopo da Entrega 6 e sem implementação correspondente na `main`.
> As afirmações de validação física, nível lógico e dimensionamento elétrico
> abaixo precisam ser revistas contra o modelo exato do E18-D80NK, medições da
> bancada e documentação técnica dos componentes antes de energizar a GPIO.
> A versão final deverá remover o circuito de atuação e registrar evidências do
> circuito realmente montado.

---

### Registro de Alterações

| Versão | Responsável | Data | Alterações |
| :--- | :--- | :--- | :--- |
| **1.0.0** | Squad Vigi | 15/09/2026 | Elaboração inicial do circuito e dimensionamento de proteção GPIO. |
| **1.1.0** | Squad Vigi | 15/09/2026 | Atualização do esquemático oficial da bancada PoC (Raspberry Pi, E18-D80NK com divisor resistivo e módulo relé KY-019). Adequação de reprodutibilidade conforme Apostila PNAAT (páginas 19 e 20). Remoção de componentes não implementados nesta fase. |

---

## Visão Geral do Sistema Elétrico da Bancada (PoC)

O sistema elétrico da bancada de testes (Prova de Conceito - PoC) do **Vigi** integra os elementos do laço de controle crítico de inspeção e ejeção em tempo real:
1. **Unidade Central de Processamento:** Raspberry Pi 5 (8GB), responsável pela execução do pipeline de inferência de visão computacional, orquestração e acionamento de GPIO.
2. **Sensoriamento de Presença Industrial:** Sensor fotoelétrico infravermelho reflexivo **E18-D80NK** (saída NPN coletor aberto alimentada a 5V).
3. **Condicionamento de Nível Lógico (3,3V LVTTL):** Divisor resistivo ($R_{10} = 1\text{ k}\Omega$ e $R_{11} = 2.2\text{ k}\Omega$) para proteção da entrada digital da Raspberry Pi contra sobretensão.
4. **Atuação de Triagem Mecânica:** Módulo Relé de 5V (**KY-019**) acionado pela GPIO 23, provendo isolamento galvânico para disparo de solenoide ou atuador pneumático de descarte.

---

## Esquemático Elétrico Oficial da Bancada

O circuito foi desenvolvido e validado no software **Fritzing**, garantindo coerência estrita entre as conexões físicas e a lógica programada no firmware (`edge/acquisition/sensor.py` e orquestrador).

![Esquemático Elétrico Oficial](./VigiEsquematico.png)

* Arquivo de projeto Fritzing editável: [`VigiEsquematico.fzz`](./VigiEsquematico.fzz)
* Componente do Módulo Relé: [`parts/Modulo_Rele_5V.fzpz`](./parts/Modulo_Rele_5V.fzpz)

---

## Mapeamento de Conexões da Raspberry Pi 5 (Header de 40 Pinos)

Abaixo está o mapeamento detalhado de cada conexão realizada no header da Raspberry Pi 5:

| Pino Físico | Nome / Função BCM | Direção | Conexão de Destino | Função Técnica |
| :---: | :---: | :---: | :--- | :--- |
| **04** | **5.0V Power** | Saída | Pino 1 do Sensor E18 e Pino `+` do Módulo Relé KY-019 | Barramento principal de alimentação 5V DC |
| **06** | **GND** | Referência | Pino `-` do Módulo Relé KY-019 | Retorno de corrente da bobina do relé |
| **09** | **GND** | Referência | Terminal 2 do Resistor $R_{11}$ ($2.2\text{ k}\Omega$) | Referência de terra do divisor de tensão |
| **11** | **GPIO 17** | **Entrada Digital** | Nó central do divisor (Terminal 2 de $R_{10}$ e Terminal 1 de $R_{11}$) | Sinal de gatilho do sensor com debounce de 50 ms (RNF08) |
| **16** | **GPIO 23** | **Saída Digital** | Pino `S` (Sinal) do Módulo Relé KY-019 | Sinal de comando de ejeção do frasco reprovado |
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

## Módulo Relé de Descarte (Isolamento Galvânico)

O módulo **KY-019** conta com isolamento elétrico e diodo de proteção flyback integrado na placa.
* O sinal de acionamento em nível alto proveniente da GPIO 23 satura o transistor do módulo, energizando a bobina de 5V.
* Os contatos secos de saída (`COM`, `NO` e `NC`) permitem chavear cargas de potência externa (ex: 12V/24V de válvulas solenoides pneumáticas) sem qualquer acoplamento de corrente ou ruído elétrico na Raspberry Pi.

---

## Lista de Componentes da Bancada (Bill of Materials - BOM)

| Item | Componente | Especificação | Qtd. | Função no Sistema |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **Raspberry Pi 5 (8GB)** | SBC ARM Cortex-A76 quad-core @ 2.4GHz | 1 | Processamento central, inferência Edge AI e orquestração |
| 2 | **Sensor E18-D80NK** | Sensor fotoelétrico reflexivo infravermelho NPN (3 a 80 cm) | 1 | Gatilho determinístico de posicionamento milimétrico do frasco |
| 3 | **Módulo Relé 5V (KY-019)** | Relé de 1 canal com transistor de disparo e diodo flyback | 1 | Chaveamento isolado para o mecanismo de descarte |
| 4 | **Resistor 1.0 kΩ** | Resistor de precisão 1/4W (R10) | 1 | Resistor série do divisor de tensão protetor da GPIO |
| 5 | **Resistor 2.2 kΩ** | Resistor de precisão 1/4W (R11) | 1 | Resistor shunt (para o GND) do divisor de tensão |
| 6 | **Câmera RPi / USB** | Módulo de Câmera de alta velocidade | 1 | Captura ótica de alta velocidade no plano focal |
| 7 | **Fonte USB-C PD 27W** | Fonte regulada 5V / 5A | 1 | Alimentação primária da Raspberry Pi e periféricos |
| 8 | **Protoboard e Jumpers** | Placa de prototipagem e cabos de conexão | 1 | Distribuição dos sinais e barramentos da bancada |

---

## Relação com os Requisitos do Projeto

* **RN01 — Disparo Determinístico:** Garantido pelo sensor E18-D80NK conectado na GPIO 17, permitindo capturar o frame exatamente quando o centro da garrafa cruza a linha de visão.
* **RN02 — Ação Preventiva de Fail-Safe:** Em caso de falha de leitura, detecção de baixa confiança ou desconexão, o relé na GPIO 23 é acionado para rejeição preventiva da peça.
* **RNF01 — Latência Ponta a Ponta < 500 ms:** Sensor com resposta inferior a 2 ms, inferência otimizada com TFLite INT8 em 23,4 ms e acionamento mecânico inferior a 50 ms.
* **RNF08 — Filtro de Debounce de 30 a 100 ms:** Configurado em 50 ms no módulo `edge/acquisition/sensor.py`, eliminando falsos positivos originados por reflexos ou trepidação mecânica.
