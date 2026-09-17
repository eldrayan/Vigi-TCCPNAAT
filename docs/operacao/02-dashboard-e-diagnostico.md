# Operação do dashboard e diagnóstico

Complete a instalação do [README](../../README.md). Os endereços padrão são
`http://IP_DO_NO_CENTRAL:8081` para o dashboard e
`http://IP_DO_NO_CENTRAL:8000` para a API; substitua o endereço e portas conforme
seu `.env`. O dashboard consome REST e atualizações SSE do backend.

## Preparar estação e lote

Cadastre a estação pela API e ative um lote seguindo o
[guia de múltiplas estações](01-multiplas-estacoes.md). Os códigos do cadastro,
`.env` do Edge e ACL precisam ser coerentes. Não coloque credenciais do backend
em uma estação remota.

Em **Configurações**, a interface atual mostra a **primeira estação retornada
pela API**, em campo somente leitura. Digite o nome do lote e clique em
**Salvar configuração**: o cliente procura/cria o lote nessa estação e o ativa.
A confirmação esperada é “Lote salvo com sucesso”. Para configurar outras
estações, use a API indicada no guia; a tela não oferece seletor de estação para
essa operação. Ao trocar o lote, pare o Edge com `Ctrl+C`, atualize `BATCH_CODE`
no `.env` e reinicie `make edge-up`: o processo contínuo carrega o contexto nos
argumentos ao iniciar e não acompanha alterações retidas no MQTT. A mesma tela ajusta a fonte entre
100% e 120%.

## Acompanhar a inspeção

- **Visão geral:** confira totais, taxa de conformidade, distribuição de não
  conformidades e inspeções recentes. Os números representam registros recebidos
  pelo backend; não são medição de acurácia do classificador.
- **Estações:** confira conexão, sensor, câmera e processamento. `ONLINE`
  representa status reportado pelo software; observe também o horário informado
  pela API. `IDLE` durante espera do sensor é normal. Status não substitui ensaio
  físico do sensor e da câmera.
- **Inspeções:** use **Pesquisa avançada** para filtrar estação, lote, período,
  resultado e tipo de não conformidade; use paginação para percorrer o histórico.
  Remova filtros se um registro esperado não aparecer. Falhas técnicas devem ser
  interpretadas pelo campo `technical_failure_type`, não como defeito visual
  confirmado do recipiente.

Para confirmar um ciclo, registre o horário, estação e lote; dispare uma inspeção
somente após validar a montagem. Confira a decisão no terminal, a captura local
se habilitada e, por último, o registro na API:

```bash
vigi_api_url=http://IP_DO_NO_CENTRAL:8000
curl --fail --silent --show-error "$vigi_api_url/health"
curl --fail --silent --show-error "$vigi_api_url/api/estacoes"
curl --fail --silent --show-error \
  "$vigi_api_url/api/inspecoes?limit=10&offset=0"
curl --fail --silent --show-error "$vigi_api_url/api/inspecoes/resumo"
```

A saúde HTTP confirma disponibilidade da API. A lista de inspeções deve conter o
novo registro com `inspection_id`, `timestamp`, `station_code`, `batch_code`,
resultado e tempo de processamento. Consulte novamente após atualizar a página
para confirmar recuperação pelo backend. Um ACK MQTT confirma entrega ao
broker; **não comprova persistência no banco do backend**. A outbox SQLite local
retém eventos para entrega MQTT e é separada do banco central. Não apague esses
arquivos para resolver indisponibilidade de rede.

## Alarmes

Em **Alarmes**, clique em configurar, selecione a estação, dê um nome e informe
um limite entre 0 e 100 (%). O limite se aplica ao lote ativo da estação escolhida;
é necessário ativar o lote primeiro. O backend avalia a taxa do lote ao receber
uma inspeção não conforme e dispara quando a taxa é **maior** que o limite.
Há também alarme de três inspeções não conformes consecutivas no lote.

Ao reconhecer um alarme aberto, informe o responsável e confirme. Reconhecimento
registra o atendimento no sistema, sem corrigir o defeito, alterar inspeções ou
acionar a esteira. A implementação automática não recria o mesmo tipo de alarme
em um lote que já teve esse tipo registrado, mesmo após reconhecimento; não use
essa tela como promessa de alertas repetidos a cada nova ocorrência. O alarme de
recorrência tem prioridade quando as duas condições coincidem na mesma avaliação.

## Diagnóstico por etapa

| Sintoma | Verificação e ação |
| --- | --- |
| API indisponível | No nó central: `docker compose ps` e `docker compose logs --tail=100 backend`; confira a porta do `.env` e `/health`. |
| Dashboard vazio ou resposta inválida | Confira backend, proxy do frontend e filtros; consulte `/api/inspecoes` diretamente. Ausência de registros pode ser normal antes da primeira inspeção. |
| Erro MQTT de autenticação/autorização | Compare usuário/senha Edge com o broker e `MQTT_STATION_CODES` com os códigos cadastrados. Recrie apenas `mqtt` após mudar a ACL. Não imprima senhas. |
| Terminal mostra publicação, API não mostra registro | Confira logs do backend, tópico por estação, validação do payload e cadastro de estação/lote. ACK do broker não é ACK do banco. |
| Modelo ausente/inválido | Execute a recuperação explícita e a checagem do [guia DVC](../dvc-dagshub.md). |
| `Pipeline handler in use` | Encerre preview, coletor ou outro processo que detenha a câmera. Só um processo deve controlá-la. Não pare serviços desconhecidos por tentativa. |
| Picamera2 não encontrado | Confira instalação do pacote do sistema e `.venv` com acesso a `system-site-packages`, conforme README. |
| Sensor não dispara | Com alimentação desligada, confira montagem e pinagem pelo [manual elétrico](../esquematico/esquematico-eletrico.md); `GPIO_PIN` é BCM. Validação elétrica precede o ensaio físico. |
| Estado `OFFLINE` ou antigo | Compare horário do status, processo Edge, rede e identificação. Consulte `/api/estacoes/ID_DA_ESTACAO/status`, substituindo o ID pelo retornado no cadastro. |
| Imagem escura, borrada ou fora de posição | Use preview, ajuste iluminação/enquadramento e parâmetros de captura; encerre preview antes do Edge. Aumentar confiança do classificador não corrige a captura. |

## Encerrar e retomar

No terminal da estação, encerre `make edge-up` com `Ctrl+C`. No nó central,
`make down` encerra a pilha Compose. Não execute `make reset-data` ou remova os
diretórios de dados durante uma parada operacional: isso não faz parte do fluxo
de encerramento. Para retomar, inicie `make up` no central e `make edge-up` nas
estações; confira saúde, contexto e status novamente.

Os ciclos físicos descritos aqui são procedimentos de aceitação a executar na
bancada, não resultados já comprovados por esta revisão documental.
