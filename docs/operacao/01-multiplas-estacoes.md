# Configuração de múltiplas estações Edge

Este guia descreve como conectar duas ou mais Raspberry Pi ao mesmo broker
MQTT do Vigi. A topologia recomendada possui um nó central com Mosquitto,
backend, banco e dashboard, enquanto cada estação executa somente câmera,
sensor, inferência e publicação MQTT.

```text
Estação 01 ─┐
            ├── MQTT central ── Backend/SQLite ── Dashboard
Estação 02 ─┘
```

Não execute `make up` nas estações Edge. Esse comando inicia outra pilha de
broker, backend e frontend. Em cada estação, o processo correto é
`make preview-camera` para ajuste e `make edge-up` para inspeção.

## 1. Definir identificadores únicos

Cada estação precisa de código e `device_id` exclusivos. Prefira letras
minúsculas, números e hífens, pois a API normaliza os identificadores nesse
formato.

| Nó | `STATION_CODE` | `DEVICE_ID` | Lote de exemplo |
| --- | --- | --- | --- |
| Raspberry central/estação 1 | `estacao-01` | `estacao-01` | `LOTE_01` |
| Raspberry estação 2 | `estacao-02` | `estacao-02` | `LOTE_02` |

O `DEVICE_ID` também compõe o identificador dos clientes MQTT. Reutilizá-lo em
duas Raspberrys faz uma conexão substituir a outra.

## 2. Escolher a rede

Na mesma rede local, use o IP privado do nó central, por exemplo
`10.1.30.5`. Em redes diferentes, conecte as Raspberrys ao mesmo Tailnet e use
o IP Tailscale do nó central, por exemplo `100.67.236.30`.

Não exponha a porta MQTT `1883` diretamente à internet. De cada estação Edge,
valide o caminho até o broker:

```bash
nc -vz 100.67.236.30 1883
```

## 3. Autorizar as estações no broker central

No `.env` do nó central, liste todos os códigos autorizados, separados por
vírgula e exatamente no mesmo formato usado pelas estações:

```env
MQTT_BIND_HOST=0.0.0.0
MQTT_STATION_CODES=estacao-01,estacao-02
```

O Mosquitto gera a ACL durante a inicialização. Depois de alterar a lista,
recrie somente o broker:

```bash
docker compose up --detach --force-recreate mqtt
```

As estações usam atualmente o mesmo par `MQTT_EDGE_USERNAME` e
`MQTT_EDGE_PASSWORD`. O backend usa credenciais próprias `MQTT_BACKEND_*`.
Transfira apenas as credenciais Edge para as estações remotas e nunca registre
senhas reais no Git.

## 4. Cadastrar estação e lote no backend

O exemplo abaixo deve ser executado contra a API central. Ajuste
`vigi_api_url` caso o backend esteja em outro endereço:

```bash
vigi_api_url=http://100.67.236.30:8000

vigi_station_id=$(curl --fail --silent --show-error \
  -X POST "$vigi_api_url/api/estacoes" \
  -H 'Content-Type: application/json' \
  -d '{
    "code": "estacao-02",
    "name": "Estação 02",
    "device_id": "estacao-02"
  }' | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')

vigi_batch_id=$(curl --fail --silent --show-error \
  -X POST "$vigi_api_url/api/estacoes/$vigi_station_id/lotes" \
  -H 'Content-Type: application/json' \
  -d '{"code": "LOTE_02"}' \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')

curl --fail --silent --show-error \
  -X PUT "$vigi_api_url/api/estacoes/$vigi_station_id/lote-ativo" \
  -H 'Content-Type: application/json' \
  -d "{\"batch_id\": $vigi_batch_id}"
```

Se a estação já existir, a API retorna `409`. Consulte os identificadores em:

```bash
curl --fail --silent --show-error "$vigi_api_url/api/estacoes"
curl --fail --silent --show-error \
  "$vigi_api_url/api/estacoes/ID_DA_ESTACAO/lotes"
```

A ativação publica uma configuração retida no tópico do dispositivo. O
`make edge-up` atual também recebe estação e lote pelo `.env`; mantenha os dois
valores iguais ao contexto ativo no backend.

## 5. Configurar cada Raspberry Edge

Prepare o ambiente e o modelo em cada estação:

```bash
make setup-rpi
make model-pull
```

Exemplo de `.env` para a estação 2:

```env
HOST=100.67.236.30
PORT=1883

MQTT_EDGE_USERNAME=vigi-edge
MQTT_EDGE_PASSWORD=SUBSTITUA_PELA_SENHA_DO_BROKER

STATION_CODE=estacao-02
DEVICE_ID=estacao-02
BATCH_CODE=LOTE_02

GPIO_PIN=17
DEBOUNCE_MS=50
CAMERA=0
CAMERA_BACKEND=picamera2
CAPTURE_DELAY_MS=350

WIDTH=1296
HEIGHT=972
FPS=40
EXPOSURE_US=12000
ANALOGUE_GAIN=8.0
AWB_MODE=auto

SAVE_CAPTURES=true
CAPTURE_DIR=captures
PREVIEW_PORT=8090
```

Uma estação Edge não precisa receber `MQTT_BACKEND_USERNAME` nem
`MQTT_BACKEND_PASSWORD`.

## 6. Ajustar a câmera e iniciar manualmente

Primeiro, ajuste o enquadramento sem iniciar o sensor:

```bash
make preview-camera
```

Abra `http://IP_DA_ESTACAO:8090`. Encerre com `Ctrl+C` antes da próxima etapa,
pois somente um processo pode controlar a câmera.

Quando a montagem estiver pronta, inicie a inspeção:

```bash
make edge-up
```

O projeto não precisa iniciar a esteira automaticamente no boot. Se existir um
serviço de testes anterior, desabilite-o:

```bash
systemctl --user disable --now vigi-edge-estacao-02.service
```

## 7. Verificar a operação

No broker central, acompanhe conexões e autorizações:

```bash
docker compose logs --follow mqtt
```

Consulte o estado publicado pela estação:

```bash
curl --fail --silent --show-error \
  "$vigi_api_url/api/estacoes/$vigi_station_id/status"
```

O resultado esperado após `make edge-up` contém conexão, sensor e câmera
`ONLINE`. Durante a espera, o processamento pode aparecer como `IDLE`.

Valide também um ciclo físico completo:

1. passe um recipiente pelo sensor;
2. confirme a captura em `captures/`, quando `SAVE_CAPTURES=true`;
3. verifique a decisão no terminal da estação;
4. confirme a inspeção na API ou no dashboard central.

```bash
curl --fail --silent --show-error \
  "$vigi_api_url/api/inspecoes?limit=10&offset=0"
```

## 8. Diagnóstico rápido

| Sintoma | Causa provável | Verificação/correção |
| --- | --- | --- |
| `not authorised` no MQTT | Código ausente na ACL | Atualize `MQTT_STATION_CODES` e recrie o broker |
| `Connection refused` | IP, rota ou porta incorretos | Execute `nc -vz HOST 1883` |
| Uma estação derruba a outra | `DEVICE_ID`/client ID repetido | Use um `DEVICE_ID` exclusivo em cada Raspberry |
| Continua `OFFLINE` após reiniciar o broker | Edge antigo não republica o status retido | Reinicie `make edge-up` e atualize o checkout para obter a correção de reconexão |
| Backend repete `Dispositivo sem estação cadastrada` | Status retido usa identificador legado, como `ESTACAO_01` | Atualize o backend; identificadores recebidos agora são normalizados e mensagens descartadas recebem ACK |
| `Pipeline handler in use` | Preview, coletor ou serviço usando a câmera | Encerre o outro processo; use apenas um por vez |
| `Address already in use` | Porta do preview ocupada | Use `PREVIEW_PORT=8090` ou outra porta livre |
| Estação/lote ausente offline | Contexto operacional não configurado | Cadastre estação, crie o lote e mantenha o `.env` consistente |
| `make ps/down` pede credenciais backend | Checkout antigo do projeto | Atualize o código; estações Edge não precisam desses segredos |

Em Raspberry Pi OS com desktop, o WirePlumber pode reservar a câmera CSI. Para
uma estação dedicada, desabilite apenas o perfil de captura de vídeo no arquivo
`~/.config/wireplumber/wireplumber.conf.d/10-vigi-disable-video-capture.conf`:

```text
wireplumber.profiles = {
  main = {
    hardware.video-capture = disabled
  }
}
```

Depois, reinicie o gerenciador multimídia:

```bash
systemctl --user restart wireplumber.service
```

## Checklist para adicionar uma nova estação

- [ ] Escolher `STATION_CODE` e `DEVICE_ID` exclusivos.
- [ ] Garantir rota local ou Tailscale até o broker.
- [ ] Adicionar o código em `MQTT_STATION_CODES` e recriar o Mosquitto.
- [ ] Cadastrar estação e lote no backend central.
- [ ] Copiar somente as credenciais MQTT Edge.
- [ ] Configurar câmera, GPIO e atraso de captura no `.env`.
- [ ] Executar o preview e liberar a câmera com `Ctrl+C`.
- [ ] Iniciar `make edge-up` manualmente.
- [ ] Confirmar status `ONLINE` e realizar um ciclo físico completo.
