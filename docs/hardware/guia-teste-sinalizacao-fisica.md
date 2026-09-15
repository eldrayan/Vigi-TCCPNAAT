# Guia de teste da sinalização física

Este roteiro valida a implementação da issue #32 em uma Raspberry Pi 5, desde
um clone novo até o ensaio integrado com o sensor E18-D80NK, a câmera, os LEDs
e o buzzer. A execução dos testes automatizados não substitui a validação
elétrica em bancada.

## 1. Pré-requisitos

Use uma Raspberry Pi 5 com Raspberry Pi OS de 64 bits, câmera CSI ou USB, sensor
E18-D80NK, dois LEDs, resistores de 220 a 330 ohms e buzzer ativo. Para um buzzer
de 5 V, use um transistor 2N2222 ou estágio equivalente; não ligue 5 V a uma
GPIO.

Também são necessários:

- acesso ao repositório e à branch do PR;
- acesso autorizado ao remote DVC para baixar o modelo;
- Git, Make, Docker com Compose e `curl`;
- `python3-picamera2` para câmera CSI ou `python3-opencv` para câmera USB;
- uma segunda máquina na mesma rede, opcional, para abrir o preview e a API.

## 2. Clonar e selecionar a implementação

Enquanto o PR estiver aberto, teste diretamente sua branch:

```bash
git clone https://github.com/eldrayan/Vigi-TCCPNAAT.git
cd Vigi-TCCPNAAT
git switch --track origin/feat/sinalizacao-fisica
git status --short --branch
```

O último comando deve mostrar `feat/sinalizacao-fisica` e não deve listar
alterações locais. Depois do merge, use `git switch main && git pull --ff-only`
no lugar do `git switch --track`.

## 3. Instalar as dependências na Raspberry Pi

Com a câmera conectada e a placa desligada, energize a Raspberry e instale os
pacotes de sistema:

```bash
sudo apt update
sudo apt install -y git make curl python3 python3-picamera2 python3-opencv
```

Instale o `uv` pelo instalador oficial e abra um novo terminal, se o comando
ainda não estiver no `PATH`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Confira as demais ferramentas e prepare o ambiente com acesso aos pacotes de
sistema da câmera:

```bash
make --version
docker --version
docker compose version
python3 -c "import cv2; from picamera2 import Picamera2; print('Câmera disponível')"
make setup-rpi
```

O `make setup-rpi` precisa criar a `.venv` pela primeira vez. Se ela já existia
sem acesso aos pacotes de sistema, remova-a conscientemente ou faça o teste a
partir de um clone novo antes de repetir esse comando.

## 4. Executar os testes sem acessar as GPIOs

Instale o grupo de desenvolvimento no mesmo ambiente e execute os testes dos
indicadores, da CLI e do orquestrador:

```bash
uv sync --frozen --group dev
uv run --no-sync python -m pytest -q \
  tests/test_indicators.py \
  tests/test_executar_esteira.py \
  tests/test_conveyor_orchestrator.py
uv run --no-sync ruff check \
  edge/actuation \
  edge/orchestration/conveyor.py \
  scripts/executar_esteira.py
```

O resultado esperado é `18 passed` e `All checks passed!`. Esses testes usam
dublês de hardware: comprovam regras, chamadas não bloqueantes e liberação dos
recursos, mas não comprovam a montagem física.

Valide também que uma colisão com o GPIO 17 é recusada antes de abrir câmera,
sensor ou indicadores:

```bash
uv run --no-sync python scripts/executar_esteira.py \
  --enable-indicators --red-led-pin 17
```

O processo deve terminar com código 2 e informar conflito entre o sensor e o
LED vermelho no GPIO 17.

## 5. Baixar o modelo ativo

Configure a chave SSH autorizada apenas no repositório local e recupere os
artefatos registrados em `models.dvc`:

```bash
uv run --no-sync dvc remote modify --local local_remote keyfile /caminho/para/chave
uv run --no-sync dvc pull models.dvc
test -f models/active/manifest.json
```

Não adicione a chave, o diretório `models/` ou checkpoints binários ao Git. Se o
`dvc pull` falhar, confirme a rede, as credenciais e o acesso ao remote com o
responsável pelos artefatos.

## 6. Montar os indicadores sem conflito

Desligue totalmente a Raspberry antes de alterar a fiação. Use numeração BCM:

| Função | GPIO BCM | Pino físico J8 | Ligação |
| --- | ---: | ---: | --- |
| Sensor E18-D80NK | 17 | 11 | Entrada com condicionamento para lógica de 3,3 V |
| LED verde | 27 | 13 | GPIO, resistor de 220 a 330 ohms, LED e GND |
| LED vermelho | 22 | 15 | GPIO, resistor de 220 a 330 ohms, LED e GND |
| Driver do buzzer | 23 | 16 | GPIO para resistor de base do 2N2222 |

No estágio do buzzer de 5 V, ligue o emissor do 2N2222 ao GND comum, o coletor
ao terminal negativo do buzzer e o terminal positivo do buzzer a 5 V. Para
carga indutiva, use a proteção de retorno especificada pelo fabricante.

Antes de energizar, confira:

- polaridade dos LEDs e presença dos resistores;
- ausência de conexão de 5 V com qualquer GPIO;
- terra comum entre Raspberry, sensor e estágio do buzzer;
- saída do E18-D80NK condicionada para a lógica de 3,3 V;
- inexistência de fios soltos ou curto entre pinos adjacentes.

O esquemático completo está em
[sinalizacao-fisica.md](./sinalizacao-fisica.md).

## 7. Fazer um teste isolado dos LEDs e do buzzer

Com a montagem conferida, energize a Raspberry e execute:

```bash
uv run --no-sync python -c '
import time
from edge.actuation import GPIOStatusIndicators

devices = GPIOStatusIndicators()
try:
    for _ in range(3):
        devices.signal_result("CONFORME")
        time.sleep(0.5)
    for _ in range(3):
        devices.signal_result("NAO_CONFORME")
        time.sleep(0.5)
    devices.signal_critical_alarm()
    time.sleep(3)
    devices.acknowledge_alarm()
finally:
    devices.close()
'
```

Observe, nesta ordem: três pulsos verdes, três pulsos vermelhos, buzzer
intermitente por três segundos e silêncio ao final. Todos os dispositivos devem
ficar desligados depois que o processo terminar.

Se este teste falhar, não prossiga para a esteira. Desligue a placa e revise a
fiação, a numeração BCM e a corrente do buzzer.

## 8. Subir os serviços e conferir a câmera

Inicie Mosquitto e backend:

```bash
make up
make ps
curl -f http://localhost:8000/health
```

Em seguida, alinhe a câmera:

```bash
make preview-camera
```

Abra `http://IP_DA_RASPBERRY:8080` em outro computador. Ajuste enquadramento,
foco e posição do E18-D80NK. Pressione `Ctrl+C` no terminal do preview antes de
iniciar a esteira, pois os dois processos não podem usar a mesma câmera ao mesmo
tempo.

## 9. Executar o fluxo completo

No primeiro terminal, acompanhe toda a árvore MQTT:

```bash
make mqtt-sub TOPIC='vigi/#'
```

No segundo terminal, inicie a esteira com a pinagem padrão:

```bash
make run-esteira-indicators
```

Para mudar apenas o limite de recorrência, por exemplo para duas rejeições:

```bash
make run-esteira-indicators CRITICAL_ALARM_AFTER=2
```

Passe frascos diante do sensor e registre, para cada inspeção, o resultado no
terminal, o indicador físico, a latência e o evento MQTT. Com os padrões da CLI,
os eventos contextualizados usam a estação `ESTACAO_01` e o lote `LOTE_01`.

O comportamento esperado é:

| Estímulo | Resultado esperado |
| --- | --- |
| Inspeção `CONFORME` | Pulso verde de 150 ms; LED vermelho apagado |
| Inspeção `NAO_CONFORME` | Pulso vermelho de 150 ms; LED verde apagado |
| Três `NAO_CONFORME` consecutivos | Buzzer intermitente de 250 ms ligado e 250 ms desligado |
| Falha técnica classificada | Buzzer intermitente imediato |
| Nova inspeção após `CONFORME` | Contador de rejeições consecutivas reiniciado |

Quando o buzzer disparar, copie o PID mostrado pela aplicação e, em um terceiro
terminal, reconheça o alarme:

```bash
kill -USR1 PID
```

O buzzer deve parar sem encerrar o processo. A aplicação deve continuar
respondendo aos próximos disparos do sensor.

## 10. Registrar a evidência de aceitação

Para fechar a validação física da issue #32, guarde uma foto da montagem e um
vídeo contínuo mostrando:

1. o sensor no GPIO 17 e os indicadores nos GPIOs 27, 22 e 23;
2. uma inspeção conforme com pulso verde;
3. uma inspeção não conforme com pulso vermelho;
4. o disparo e o reconhecimento do buzzer;
5. o log com latência total menor que 500 ms no mesmo ciclo observado;
6. o encerramento com `Ctrl+C`, deixando LEDs e buzzer desligados.

Registre também o SHA testado:

```bash
git rev-parse HEAD
git status --short --branch
```

Não marque a validação física como concluída somente com base nos testes
automatizados ou na publicação MQTT.

## 11. Encerrar a bancada

Pressione `Ctrl+C` na execução da esteira. Confirme que câmera, sensor, LEDs e
buzzer foram liberados. Para parar os serviços sem apagar os dados:

```bash
make down
```

## Solução rápida de problemas

| Sintoma | Verificação |
| --- | --- |
| `GPIO busy` ou recurso ocupado | Encerre processos antigos e confirme que nenhuma GPIO está duplicada |
| LED acende invertido ou não acende | Desligue a placa; confira polaridade, resistor, GND e numeração BCM |
| Buzzer fraco ou Raspberry instável | Desligue; confira transistor, alimentação externa adequada e terra comum |
| Manifesto ausente | Execute o `dvc pull models.dvc` e confira `models/active/manifest.json` |
| Câmera ocupada | Encerre o preview com `Ctrl+C` antes de iniciar a esteira |
| MQTT ou API indisponível | Confira `make ps`, `make logs` e `curl -f http://localhost:8000/health` |
| Buzzer não silencia | Use o PID impresso pela CLI e confirme que o sistema oferece `SIGUSR1` |

## Referências

- [Issue #32 — sinalização física](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/32)
- [PR #31 — sensor E18-D80NK](https://github.com/eldrayan/Vigi-TCCPNAAT/pull/31)
- [Instalação oficial do uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Pinagem do GPIO Zero](https://gpiozero.readthedocs.io/en/latest/recipes.html#pin-numbering)
- [Dispositivos de saída do GPIO Zero](https://gpiozero.readthedocs.io/en/latest/api_output.html)
