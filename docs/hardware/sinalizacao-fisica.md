# Sinalização física local

Esta montagem opcional acrescenta dois LEDs e um buzzer ativo ao fluxo contínuo
introduzido pelo PR #31. Todos os números abaixo são **GPIO BCM**, que é a
numeração padrão do GPIO Zero; os números físicos do conector J8 aparecem apenas
como referência de montagem.

Para preparar um clone novo e executar a validação completa, siga o
[guia passo a passo de teste](./guia-teste-sinalizacao-fisica.md).

## Pinagem sem conflito

| Função | GPIO BCM | Pino físico J8 | Estado |
| --- | ---: | ---: | --- |
| Sensor E18-D80NK | 17 | 11 | Entrada, ativo em nível baixo |
| LED verde | 27 | 13 | Saída, pulso para `CONFORME` |
| LED vermelho | 22 | 15 | Saída, pulso para `NAO_CONFORME` |
| Driver do buzzer | 23 | 16 | Saída, alarme crítico intermitente |

A CLI rejeita a inicialização quando duas funções recebem a mesma GPIO. Isso
protege, em particular, o GPIO 17 já ocupado pelo E18-D80NK no PR #31.

## Esquemático de bancada

```text
Raspberry Pi 5 (J8)

GPIO27, pino 13 ── resistor 220–330 Ω ──>| LED verde ── GND
GPIO22, pino 15 ── resistor 220–330 Ω ──>| LED vermelho ── GND

GPIO23, pino 16 ── resistor de base ── B  2N2222
                                           C ── negativo do buzzer ativo 5 V
GND comum ─────────────────────────────── E
5 V, pino 2 ou 4 ─────────────────────────── positivo do buzzer
```

Use o transistor para o buzzer de 5 V. Um buzzer de 3,3 V só deve ser ligado
diretamente se a corrente declarada pelo componente estiver dentro da capacidade
segura da GPIO. Em caso de buzzer magnético/indutivo, adicione a proteção contra
retorno indicada pelo fabricante. Nunca aplique 5 V a uma GPIO da Raspberry Pi.
Desligue a alimentação antes de alterar a montagem e mantenha terra comum entre
a Raspberry Pi e o estágio do buzzer.

O E18-D80NK deve usar interface elétrica compatível com lógica de 3,3 V. A saída
NPN do sensor não autoriza aplicar sua tensão de alimentação diretamente à GPIO;
use o condicionamento/pull-up adequado ao módulo efetivamente instalado.

## Operação

```bash
make run-esteira-indicators
```

- `CONFORME`: pulso de 150 ms no LED verde.
- `NAO_CONFORME`: pulso de 150 ms no LED vermelho.
- Três não conformidades consecutivas, por padrão: buzzer de 250 ms ligado e
  250 ms desligado, repetindo até reconhecimento.
- Falha técnica classificada pelo motor: buzzer crítico imediato.
- Reconhecimento em bancada: execute `kill -USR1 PID`, usando o PID impresso no
  log da aplicação.

O limite é configurável com `CRITICAL_ALARM_AFTER`. O requisito US02 não define
percentual nem tamanho do lote para a taxa de refugo; por isso essa regra não é
inferida pelo driver. Uma futura integração no processo Edge poderá chamar
`ConveyorOrchestrator.trigger_critical_alarm()` e
`ConveyorOrchestrator.acknowledge_alarm()`. O canal de comando entre
backend/dashboard e Edge ainda não está implementado.

## Validação física pendente

Os testes automatizados usam dispositivos simulados e verificam chamadas não
bloqueantes, pinagem exclusiva, recorrência e liberação dos recursos. Antes de
marcar o critério elétrico da issue como homologado, a equipe ainda deve conferir
na Raspberry Pi 5 real: polaridade dos LEDs, valores dos resistores, corrente do
buzzer, saturação do 2N2222, terra comum e resposta de `SIGUSR1`.

## Referências

- [Issue #32 — sinalização física](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/32)
- [PR #31 — sensor e orquestrador](https://github.com/eldrayan/Vigi-TCCPNAAT/pull/31)
- [GPIO Zero — dispositivos de saída](https://gpiozero.readthedocs.io/en/latest/api_output.html)
- [GPIO Zero — numeração dos pinos](https://gpiozero.readthedocs.io/en/latest/recipes.html#pin-numbering)
