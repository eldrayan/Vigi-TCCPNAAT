# Entrega 2: Roteiro de demonstração da PoC do Vigi

Duração prevista: 5 minutos.

Versão: rascunho inicial para validação, 11/09/2026.

Vínculo: [issue #13](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13), entregável de roteiro da demonstração prática.

Dependência de execução: [issue #11](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11), modelo e pipeline de inferência na Raspberry Pi 5.

## 1. Objetivo e recorte

Mostrar a classificação visual de recipientes em funcionamento. Quem assistir deve conseguir identificar a entrada, acompanhar a inferência e relacionar o resultado à amostra apresentada.

Este vídeo é a PoC da Entrega 2, com publicação prevista como não listado no YouTube. O [pitch final de até 15 minutos: Entrega 3](../pitch/01-roteiro-pitch.md) é outro vídeo, com roteiro próprio. O [README: Entrega 4](../../README.md) organiza o esboço da documentação. Esses materiais também fazem parte da issue #13.

A sequência proposta começa com o recipiente na bancada. A câmera fornece a imagem ao modelo na Raspberry Pi 5, e a decisão aparece no terminal. Essa montagem mostra a inferência funcionando com outro elemento da arquitetura, a câmera, e pode ser demonstrada antes da integração completa do sistema.

O repositório já contém a CLI `scripts/infer.py`, que executa uma inspeção por imagem ou captura de câmera e imprime um evento em JSON e pode publicá-lo por MQTT. O coletor continua separado e não executa inferência. Para gravar, recupere os artefatos DVC, confira o manifesto do modelo ativo e teste a execução na bancada conforme o [README](../../README.md). A disponibilidade do código não comprova a validação física.

O backend já recebe eventos MQTT, grava no SQLite e oferece consultas pela API. Para esta PoC, a demonstração mínima continua sendo câmera e inferência; a consulta do mesmo evento na API pode ocupar o bloco de leitura do resultado, se ensaiada. A página `/docs` é a documentação interativa da API, não o dashboard React.

A case pode aparecer na apresentação da montagem. O dashboard cabe como saída adicional se já receber a inferência; sua ausência não impede este recorte da PoC. A explicação mais ampla sobre autonomia local, montagem compacta e supervisão fica no pitch final.

## 2. Preparação da bancada e da tela

- Separar um recipiente conforme e outro com um defeito visível pertencente às classes efetivamente disponíveis no modelo. Preferir `sem_tampa` pela facilidade de identificação visual, se essa classe estiver operacional.
- Manter iluminação, fundo e enquadramento consistentes. Identificar as amostras como A e B para relacionar cada entrada à respectiva saída.
- Mostrar a case e confirmar como a Raspberry Pi e a câmera estão acomodadas. Apontar também os elementos externos, sem dizer que toda a instalação ocupa apenas a case. Explicar onde o processamento acontece. Se houver notebook conectado por acesso remoto, identificá-lo como tela de acesso, quando esse for seu papel real.
- Organizar a gravação para mostrar a bancada e a saída legível, por enquadramento conjunto ou captura de tela com imagem da bancada sobreposta. Mostrar o quadro realmente usado pelo modelo, quando disponível.
- Usar o terminal da CLI de inferência. Cada chamada produz uma decisão JSON, sem preview ou janela de inferência. Para tornar a entrada identificável, filmar o recipiente e o momento da captura, ou mostrar o arquivo de imagem usado. O vídeo pode ser gravado sem criar um dashboard.
- Ensaiar o acionamento manual da CLI, com uma chamada por amostra. Só apresentar captura contínua ou acionada pelo sensor E18-D80NK se essa integração estiver implementada e funcionando na versão usada.

### Dados a confirmar antes da gravação

| Item | Registro para o ensaio |
| --- | --- |
| Responsável pela apresentação e pela operação | A definir com a equipe |
| Modelo, versão e caminho dos pesos usados | A confirmar |
| Classes presentes no modelo exportado | A confirmar |
| Equipamento que executa a inferência | Confirmar Raspberry Pi 5; registrar se for outro |
| Câmera e forma de captura/acionamento | A confirmar |
| Comando real de execução e diretório de trabalho | A preencher após teste na bancada |
| Saída disponível | Conferir `inspection_id`, `timestamp`, `result`, `category`, `nonconformity_type`, `technical_failure_type`, `confidence`, `processing_time_ms` e `model_format` no JSON |
| Evidência do ensaio | Registrar amostras, saídas reais e limitações observadas |
| Case e montagem | Confirmar componentes internos e externos; medir dimensões se forem citadas |
| Dashboard | Registrar se está integrado, se é interface com dados simulados ou se ainda está previsto |
| Conectividade no ensaio | Registrar uso de internet, rede local e acesso remoto; só declarar offline para as funções testadas |

### Escolha da execução no ensaio

Seguir a preparação do README antes de gravar. Para a demonstração de inferência sem broker, executar `uv run --no-sync python scripts/infer.py --manifest models/active/manifest.json --camera 0 --backend picamera2`, sem `--mqtt-host`. Esse modo imprime o resultado sem persistir no banco.

Se for mostrar o caminho até a API, iniciar os serviços com `make up`, verificar `http://localhost:8000/health` e executar `make infer-camera`. O alvo Make habilita MQTT. Anotar o `inspection_id` retornado e consultar `/api/inspecoes/{id_inspecao}` com esse valor. Uma publicação confirmada no broker ainda precisa ser conferida na API para comprovar a persistência. Os serviços devem estar prontos antes de iniciar os cinco minutos do vídeo.

## 3. Roteiro de gravação: 00:00 a 05:00

Adapte as falas ao ensaio e preencha os campos entre colchetes com informações verificadas. O tempo de cada bloco inclui a narração, a operação da bancada, a troca de amostras e as pausas para leitura da tela.

### 00:00 a 00:30: Apresentação e objetivo (30 s)

Imagem/ação: apresentador e bancada, com o nome Vigi e a identificação "Entrega 2: Prova de Conceito".

> Este é o Vigi, um projeto de inspeção visual de recipientes em linhas de envase. Queremos distinguir recipientes conformes de outros com defeitos visíveis, como a falta de tampa. Nesta prova de conceito, vamos testar esse funcionamento inicial: fornecer uma imagem ao modelo, executar a inferência e mostrar a classificação na tela.

### 00:30 a 01:10: Elementos e caminho da informação (40 s)

Imagem/ação: mostrar a case na bancada e apontar o recipiente, a câmera, a Raspberry Pi e a tela. Exibir brevemente o fluxo `Câmera → Inferência na Raspberry Pi → Resultado`.

Após confirmar a montagem, adaptar a fala:

> Esta case acomoda [componentes confirmados]. A câmera fornece a imagem do recipiente, e a Raspberry Pi 5 executa localmente o modelo [nome e versão], treinado para distinguir [classes disponíveis]. O resultado aparece neste terminal. A captura é [manual na CLI; adaptar se outra integração tiver sido validada]. Assim, acompanhamos a câmera e a inferência funcionando juntas.

Usar apenas a modalidade real de captura e as informações exibidas. Processamento local não comprova segurança nem funcionamento offline. Se o resultado for visualizado por acesso remoto, informar que essa visualização usa a rede local.

### 01:10 a 02:20: Primeiro ciclo: recipiente conforme (70 s)

Imagem/ação, em sequência contínua:

1. Mostrar a amostra A e explicar por que ela é visualmente conforme.
2. Posicioná-la diante da câmera, mantendo o recipiente visível na gravação até a captura. Se usar arquivo, abrir a imagem que será processada.
3. Iniciar uma chamada da CLI pelo comando validado, mostrando o momento da execução.
4. Acompanhar o processamento e manter o resultado legível por alguns segundos, sem corte entre entrada e saída.

> Esta é a amostra A, com a tampa posicionada e sem o defeito que vamos mostrar depois. Vamos capturar a imagem deste recipiente. [Se usar arquivo: esta é a imagem que será processada.] Agora [ação real que inicia o ciclo]. O programa passa a imagem ao modelo e mostra a decisão [resultado observado] para essa amostra. [Se disponível: o score exibido foi valor observado.]

Compare a previsão com a condição da amostra. Se houver divergência, descreva o erro em vez de ler a fala prevista para um acerto. O score de uma previsão não é a acurácia do modelo.

### 02:20 a 03:30: Segundo ciclo: defeito visível (70 s)

Imagem/ação, em sequência contínua:

1. Retirar A, mostrar a amostra B e apontar o defeito visível.
2. Apresentar B à câmera, preservando as condições da bancada.
3. Repetir o ciclo e mostrar a nova saída, distinguindo-a do resultado anterior.
4. Comparar a classe retornada com o defeito apresentado.

> Esta é a amostra B, que apresenta [defeito visível]. Vamos fazer uma nova inferência com a mesma câmera e o mesmo enquadramento. Para esta imagem, a saída informa [resultado observado e código, quando houver]. [Se houver acerto: a classificação corresponde ao defeito mostrado.]

Em caso de erro ou instabilidade, descreva o que ocorreu e a limitação observada. Ao repetir o teste, mostre novamente a entrada e a execução. Preserve a saída real na gravação, sem substituí-la por texto na edição.

### 03:30 a 04:15: Leitura do resultado e alcance da prova (45 s)

Imagem/ação: manter a saída real visível e apontar seus campos. Se a publicação estiver habilitada, consultar na API o `inspection_id` de uma amostra e mostrar o registro correspondente dentro destes 45 segundos. Identificar a tela como API, e não como dashboard. Se o dashboard vier a ser integrado, ele poderá ocupar esse espaço. Caso contrário, usar a saída da CLI ou repetir A, sem tratar a repetição como avaliação estatística.

Se o painel tiver apenas dados simulados, reservá-lo para a explicação do pitch, onde será identificado como protótipo de interface. Na PoC, preservar a saída real da inferência. Se ainda estiver previsto, citar o dashboard no encerramento como parte a integrar.

> A decisão resume a previsão para a imagem apresentada. [Se disponível: este score acompanha a previsão; ele não representa a acurácia global.] Nos ciclos que mostramos, observamos [resumo fiel dos resultados]. Esses testes mostram o funcionamento inicial da captura com a inferência nesta bancada. Para avaliar a qualidade do modelo, ainda precisamos considerar os testes com imagens que ficaram fora do treinamento.

Na CLI atual, `result` informa conformidade, `nonconformity_type` identifica o defeito do produto, `technical_failure_type` identifica a falha técnica, e `confidence` informa o score. Em um resultado conforme, `nonconformity_type` pode ser nulo. `processing_time_ms` mede a predição, sem a captura da câmera. Ajuste a leitura das falas a esses campos; baixa confiança é uma decisão de falha técnica, não uma classe de defeito. O RNF01 considera toda a inspeção, da detecção à disponibilização do resultado; medir apenas a inferência não comprova esse requisito. Os dois exemplos do vídeo também não bastam para comprovar a meta de acurácia do RNF06.

### 04:15 a 05:00: Limites e próxima etapa técnica (45 s)

Imagem/ação: voltar à bancada ou ao fluxo simplificado. Identificar visualmente o trecho demonstrado e as integrações futuras.

Adaptar a fala ao que estiver funcionando:

> Nesta PoC, usamos [componentes realmente usados] e mostramos os resultados das amostras. O próximo passo é [integração ainda pendente, por exemplo: ligar o gatilho do sensor à captura e à inferência]. O código já permite enviar eventos por MQTT, gravá-los no SQLite e consultá-los pela API. [Informar se esse caminho foi demonstrado.] Ainda estão previstos o dashboard e a fila persistente no Edge para lidar com falhas de comunicação. [Citar somente o que de fato falta integrar.] Também precisamos ampliar os testes de classificação e medir o tempo do ciclo.

Os atuadores estão fora do escopo atual do projeto. Por isso, a rejeição mecânica de recipientes não deve ser anunciada como próxima entrega.

## 4. Alternativa se a captura integrada ainda não estiver disponível

Se a captura integrada ainda não funcionar, use uma imagem já capturada. Mostre qual arquivo será usado, inicie o processamento e mantenha a gravação até a saída, sem cortes no ciclo. Informe que a entrada é um arquivo e em qual equipamento a inferência está rodando.

O teste com arquivo demonstra a inferência sobre uma imagem. Para mostrar a câmera funcionando com o modelo e buscar o nível Avançado, será preciso gravar o ciclo com captura integrada ou usar outro elemento da arquitetura conectado à inferência. Uma execução apenas em notebook ou ambiente remoto não valida a inferência embarcada na Raspberry Pi.

## 5. Conferência com os critérios da atividade

| Critério informado pela plataforma | Evidência planejada no vídeo |
| --- | --- |
| Entrada ou início da execução identificável | Amostras A e B, imagem de entrada e acionamento visível |
| Tecnologia principal funcionando | Execução real do modelo durante os dois ciclos |
| Resultado produzido | Decisão JSON legível e vinculada à amostra correspondente |
| Entrada, execução e resultado em uma sequência acompanhável | Ciclos contínuos de 01:10 a 03:30, sem cortes internos |
| Tecnologia central com outro elemento da arquitetura | Câmera fornecendo a imagem ao pipeline de inferência |
| Explicação da entrada, funcionamento, resultado e função dos elementos | Apresentação da montagem e narração dos ciclos |
| Próxima etapa ou função ainda não integrada/implementada | Encerramento com pendências concretas verificadas no ensaio |
| Artefato solicitado | Link do vídeo não listado no YouTube, com cerca de 5 minutos |

Para atender ao nível Avançado, a gravação precisa mostrar as evidências planejadas na tabela.

## 6. Checklist do ensaio e da entrega

- [ ] Confirmar com o responsável pela issue #11 os pesos, classes, comando e ambiente de execução.
- [ ] Executar os dois ciclos na bancada e preencher os dados pendentes deste roteiro.
- [ ] Validar o roteiro e dividir apresentação/operação com a equipe.
- [ ] Conferir se a imagem mostrada corresponde à entrada real da inferência.
- [ ] Confirmar a câmera integrada, ou declarar explicitamente a alternativa utilizada.
- [ ] Ajustar as falas de resultado, limitações e próxima etapa ao estado observado.
- [ ] Confirmar a apresentação da case e a função de cada componente mostrado.
- [ ] Se usar a API ou, futuramente, o dashboard, relacionar o registro ao `inspection_id` da inferência gravada.
- [ ] Identificar a conexão usada e evitar afirmações de segurança, acesso restrito ou autonomia offline sem verificação.
- [ ] Ensaiar com cronômetro para aproximadamente 5 minutos, preservando o tempo de leitura das saídas.
- [ ] Conferir áudio e legibilidade; manter cada ciclo sem cortes entre entrada e resultado.
- [ ] Revisar a gravação completa e confirmar que não há métricas ou integrações apresentadas sem evidência.
- [ ] Publicar o vídeo como não listado no YouTube e testar o acesso pelo link sem a conta do autor.
- [ ] Registrar o link final e enviá-lo à plataforma da atividade.

Link do vídeo: pendente de gravação e publicação.

## 7. Referências e alinhamento da issue

- [Issue #13: documentação e roteiros](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13).
- [Issue #11: treinamento e inferência](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11).
- [Arquitetura do Vigi](../arquitetura/diagrama-arquitetural.md).
- [Requisitos funcionais: US01](../requisitos/02-requisitos-funcionais.md).
- [Requisitos não funcionais: RNF01 e RNF06](../requisitos/03-requisitos-nao-funcionais.md).
- Critérios da Entrega 2 fornecidos na solicitação desta atividade.

A issue #13 pede uma demonstração com sensor e SQLite/MQTT/Node-RED. Para a Entrega 2, este roteiro cobre a inferência inicial; a validação física do fluxo completo da issue continua pendente. A apresentação segue a arquitetura documentada, com FastAPI e React para supervisão, sem Node-RED. Para concluir a issue #13, também será preciso finalizar os demais entregáveis e validá-los com a equipe.
