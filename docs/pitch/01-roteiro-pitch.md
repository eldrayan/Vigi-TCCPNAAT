# Entrega 3: Esboço do vídeo pitch final do Vigi

Versão: 0.2, roteiro para ensaio, 11/09/2026.

Duração máxima: 15 minutos, incluindo demonstração e transições.

Issue: [#13: Documentação Técnica, Roteiro do Pitch e Demonstração da PoC](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13).

## 1. Proposta narrativa

A apresentação começa pelos desperdícios e pelas interrupções que recipientes defeituosos podem causar no empacotamento. Em seguida, explica como a estação de inspeção proposta usa imagens para classificar os recipientes e gerar eventos para supervisão. A demonstração mostra esse processo na bancada. Na conclusão, a equipe compara os resultados com o benefício esperado e explica o que falta fazer.

Este roteiro é para o vídeo final de até 15 minutos. O [vídeo da PoC da Entrega 2](../poc/01-roteiro-video-poc.md), de aproximadamente 5 minutos, é uma gravação separada. O pitch reserva um bloco para a demonstração dentro do tempo total. Nesse bloco, a equipe pode aproveitar a sequência ensaiada para a PoC, atualizando-a conforme o estado final do projeto.

O código atual já inclui publicação MQTT, backend, SQLite e consultas HTTP. O dashboard React e o gatilho físico ainda estão previstos. Antes de gravar, preencha os campos entre colchetes com os dados verificados. As falas descrevem a arquitetura proposta; anuncie como implementados e integrados apenas os componentes demonstrados.

### Argumentos que orientam a apresentação

| Argumento | O que explicar | Evidência ou limite |
| --- | --- | --- |
| Autonomia local | A arquitetura prevê inspeção, decisão e armazenamento na Raspberry Pi, sem depender de internet ou de rede externa para essas funções | Verificar o funcionamento offline antes de anunciá-lo como demonstrado. Processamento local não comprova, por si só, a segurança do sistema |
| Montagem compacta | A case reúne a Raspberry Pi e a câmera, conforme a montagem informada pela equipe | Mostrar a case real e confirmar seu conteúdo. O espaço da instalação também inclui sensor, alimentação, cabos, fixação e área de captura; dimensões precisam ser medidas |
| Acompanhamento da operação | O dashboard reúne resultados, histórico e alarmes para operadores e supervisores | O acesso por outros dispositivos precisa de conexão com a Raspberry Pi. Identificar se o painel está integrado, se usa dados simulados ou se ainda é uma proposta |

A operação offline está prevista na [RN04](../requisitos/01-regras-de-negocio.md) e tem critérios de teste no [RNF03](../requisitos/03-requisitos-nao-funcionais.md). Acesso pela rede local e acesso pela internet são situações diferentes: a inspeção deve continuar sem rede externa, enquanto o painel remoto depende da conexão entre os dispositivos. Um teste apenas sem internet não comprova funcionamento sem rede local.

Use “destinado aos responsáveis pela operação” para identificar o público do dashboard. Só afirme que o acesso é restrito a essas pessoas se houver autenticação e autorização implementadas e verificadas. Da mesma forma, apresente o processamento local como característica da solução, sem transformá-lo em uma garantia geral de segurança.

## 2. Distribuição do tempo

| Parte obrigatória | Intervalo | Duração | Conteúdo e apoio visual |
| --- | --- | --- | --- |
| Introdução | 00:00 a 02:30 | 2 min 30 s | Problema, exemplos de defeitos, público e consequências; recipientes e esquema da linha |
| Solução | 02:30 a 06:00 | 3 min 30 s | Papel do Vigi, case, autonomia local, dashboard e classificador; montagem e diagrama de blocos |
| Demonstração | 06:00 a 11:00 | 5 min | Bancada e captura de tela; entrada → processamento → resultado e integrações disponíveis |
| Conclusão | 11:00 a 15:00 | 4 min | Evidências, limitações, próximos passos e impacto esperado; síntese dos resultados |
| Total | 00:00 a 15:00 | 15 min | Transições já incluídas nos intervalos |

## 3. Introdução: 00:00 a 02:30

### 00:00 a 00:40: Identificação e contexto

Mostrar: nome Vigi, equipe e uma visão da bancada ou esquema da linha de envase.

> Somos a equipe do Vigi, um sistema embarcado para inspeção visual de recipientes em linhas de envase. O problema que estamos tratando aparece entre o envase e o empacotamento: recipientes com defeitos seguem pela linha sem que a falha seja identificada a tempo.

### 00:40 a 01:40: Problema concreto

Mostrar: exemplos de recipiente conforme, sem tampa, com tampa torta e amassado. Identificar exemplos ilustrativos como tais.

> Uma garrafa sem tampa pode derramar o conteúdo. Um recipiente deformado pode atrapalhar o empacotamento. Além da perda de produto, esses defeitos podem exigir intervenção e interromper a produção. O operador precisa identificar a ocorrência, e o supervisor precisa saber quais defeitos se repetem para investigar suas causas.

Desenvolver: explicar com os recipientes o que distingue cada defeito e em que ponto uma inspeção intermediária poderia ajudar. Não atribuir perdas quantitativas a uma fábrica sem dados reais.

### 01:40 a 02:30: Necessidade e transição

Mostrar: posição proposta da inspeção entre envase e empacotamento.

> Precisamos identificar esses defeitos a tempo e disponibilizar o resultado para acompanhamento. A proposta é colocar uma estação de inspeção entre o envase e o empacotamento. Ela combina a captura de imagens com inteligência artificial na borda e o registro das ocorrências.

## 4. Solução: 02:30 a 06:00

### 02:30 a 03:20: Inspeção e montagem com a case

Mostrar: fluxo simplificado, case real e posição do conjunto na bancada. Apontar a Raspberry Pi e a câmera, confirmando o que está dentro da case; mostrar também os elementos externos. Usar este bloco para a montagem, sem acrescentar tempo ao vídeo.

> A proposta é que o Vigi classifique a imagem de cada recipiente para apoiar a intervenção do operador e o acompanhamento dos defeitos recorrentes. A case reúne [componentes confirmados na montagem]. Aqui podemos ver como ela acomoda a Raspberry Pi e a câmera. A instalação também precisa de espaço para o sensor, a alimentação, os cabos e o ponto de captura. O protótipo não inclui ejeção mecânica.

### 03:20 a 04:50: Arquitetura, autonomia local e dashboard

Mostrar: [diagrama de blocos no README](../../README.md), destacando cada ligação durante a fala.

> A Raspberry Pi processa a imagem e executa o classificador. No fluxo atual, iniciamos a captura manualmente e podemos enviar o resultado por MQTT ao Mosquitto. O backend FastAPI recebe esse evento, grava no SQLite e permite consultá-lo pela API. O sensor E18-D80NK deverá automatizar o disparo. Também estão previstos o dashboard React e a fila local para preservar eventos quando houver falha de comunicação. A proposta é operar sem internet; o acesso pela rede local permite que os responsáveis consultem os dados em outro dispositivo.

Dividir os 90 segundos deste bloco: cerca de 40 segundos para percorrer o fluxo, 20 para explicar a autonomia local e 30 para o papel do dashboard. Ao apontar cada componente, explicar sua função e indicar o que ainda falta integrar. Não é necessário recitar nomes de bibliotecas além dos que ajudam a entender o caminho dos dados.

A fala sobre offline descreve a proposta. Hoje, o banco é alimentado pelo consumidor MQTT: a gravação depende do broker, e o Edge ainda não guarda uma fila persistente quando a publicação falha. A inferência sem `--mqtt-host` gera apenas a saída local. Se houver teste, informar quais funções continuaram funcionando e qual conexão estava indisponível. O processamento local dispensa o envio de imagens à nuvem para inferência na arquitetura proposta; isso não equivale a comprovar segurança ou controle de acesso.

### 04:50 a 06:00: Tecnologia central e transição à prática

Mostrar: classes do modelo efetivamente usado e identificação dos pesos; distinguir treinamento de inferência. A CLI `scripts/infer.py` já está disponível e executa uma inspeção por chamada, com decisão em JSON. Recuperar o modelo pelo DVC e validar a câmera antes da gravação. A saída não inclui preview; filmar a entrada na bancada ou mostrar o arquivo usado.

> O classificador previsto na issue 11 é o YOLOv8n-cls. No treinamento, usamos imagens rotuladas. Na inferência, o modelo recebe uma imagem e retorna uma previsão. As classes previstas são conforme, sem tampa, tampa torta e amassado. [Confirmar as classes e o modelo exportado.] Na bancada, vamos acompanhar a entrada e o resultado de duas amostras.

Desenvolver: informar onde o modelo foi treinado e onde roda a inferência, após confirmação. Não apresentar score como acurácia nem classificação como detecção de objetos com caixas, se o modelo não produzir caixas.

## 5. Demonstração: 06:00 a 11:00

Reserve a bancada com câmera, Raspberry Pi e amostras. A tela de execução deve ficar legível, no mesmo enquadramento ou em uma captura de tela com a imagem da bancada sobreposta. Use os cinco minutos deste bloco para demonstrar o funcionamento e explicar as ações enquanto elas acontecem.

### 06:00 a 06:40: Montagem e início

Ação: mostrar a case na bancada e identificar equipamento, câmera, modelo e modo de captura. Informar onde o processamento roda e qual é a conexão usada para visualizar a saída. Mostrar o comando validado; a CLI atual inicia uma inspeção por chamada.

> Esta é a montagem usada no teste. [Identificar os elementos reais.] A captura é [modo real], e o processamento roda em [equipamento real]. A entrada e o resultado correspondente vão ficar visíveis durante a execução.

### 06:40 a 08:00: Amostra conforme

Ação: mostrar a amostra A e mantê-la visível diante da câmera durante a captura; se usar arquivo, abrir a imagem de entrada. Executar a CLI e manter a saída JSON visível. Preservar a continuidade entre entrada e resultado.

> Esta amostra apresenta [condição observada]. Vamos usar a imagem deste recipiente neste ciclo. [Se usar arquivo: mostrar a imagem de entrada.] O modelo retornou [resultado real]. [Explicar se corresponde ou diverge da condição da amostra.]

### 08:00 a 09:20: Amostra com defeito

Ação: trocar pela amostra B, apontar o defeito e repetir todo o ciclo. Distinguir a nova saída da anterior.

> Esta outra amostra apresenta [defeito]. Vamos repetir o processo nas mesmas condições da bancada para observar como o modelo responde a esse caso. A saída foi [resultado real].

### 09:20 a 10:20: Evento na API e leitura do resultado

Ação: explicar os campos `result`, `nonconformity_type` e `confidence` da saída JSON. O tipo de não conformidade é nulo para uma amostra conforme; baixa confiança aparece em `technical_failure_type`. O tempo exibido mede a predição, sem a captura. Se os serviços estiverem prontos, priorizar a consulta do evento na API: usar `make infer-camera` nos ciclos anteriores e consultar `/api/inspecoes/{id_inspecao}` com o `inspection_id` impresso. Esse registro comprova a passagem pelo MQTT e a gravação no banco. Mostrar `/docs` como documentação interativa da API, sem chamá-la de dashboard.

O dashboard React continua previsto. Se seu estado mudar até a gravação, usar este minuto conforme a situação:

| Estado na gravação | O que mostrar e dizer |
| --- | --- |
| Integrado à inferência | Mostrar no painel o resultado de um ciclo recém-executado, relacionando amostra e evento por identificador ou horário. Dizer: “Este resultado veio da inspeção que acabamos de executar” apenas se isso for verificável |
| Interface pronta com dados simulados | Apresentar como protótipo de interface e identificar os dados simulados na tela e na fala. Explicar o que o operador poderá consultar e que a ligação com a inferência ainda falta |
| Ainda previsto | Explicar sua função no diagrama e usar o restante do minuto para repetir uma inferência ou mostrar uma integração existente |

O fluxo MQTT, SQLite e API já está implementado, mas precisa ser ensaiado na montagem. Se o sensor também vier a ser integrado, seu gatilho poderá ser mostrado. O painel é opcional na demonstração: mantenha os dois ciclos de inferência e o limite de cinco minutos do bloco.

> O resultado deste ciclo é [resultado]. [Mostrar a evidência da integração disponível.] Aqui, [lista verificada] estão funcionando juntos. Os demais blocos do diagrama estão em [estado real].

### 10:20 a 11:00: Síntese e transição

Ação: manter a evidência visível e resumir o que acabou de ocorrer.

> Acompanhamos a entrada, a execução e o resultado de [quantidade real] ciclos. Nesses testes, observamos [observação sustentada pela gravação]. Com esses resultados, podemos avaliar o que já atende ao objetivo do projeto e o que ainda precisa de trabalho.

Se usar um trecho gravado anteriormente, avise e informe a montagem utilizada. Se a inferência aceitar apenas arquivos, mostre o arquivo, a execução e o resultado, explicando que a captura ainda não está integrada. Apresente apenas integrações que funcionam. Em caso de falha, relate o ocorrido e encerre a tentativa dentro deste bloco para manter o tempo da conclusão.

## 6. Conclusão: 11:00 a 15:00

### 11:00 a 12:00: Resultado observado e evidência

Mostrar: síntese dos ciclos e, se disponíveis, métricas verificadas da issue #11 com conjunto avaliado e ambiente.

> O problema é a passagem de recipientes defeituosos para o empacotamento. Propomos classificar suas imagens e registrar os resultados para acompanhamento. Na demonstração, observamos [resultados reais]. Nas condições apresentadas, conseguimos verificar [alcance efetivamente validado].

Desenvolver: separar exemplos demonstrativos de avaliação do modelo. Se citar acurácia, informar o conjunto não usado no treinamento e sua dimensão. Se citar tempo, informar se é de inferência ou do ciclo completo. Sem medições, apresentar as metas como metas.

### 12:00 a 13:00: Limitações e próxima etapa

Mostrar: quadro "demonstrado / pendente", preenchido antes da gravação.

> Ainda precisamos [pendências verificadas]. O próximo passo é [ação concreta]. Depois, vamos verificar isso com [teste que verificará o resultado]. Também precisamos testar mais amostras, variar a iluminação e medir o tempo do ciclo completo.

Exemplos para selecionar conforme o estado final: integrar o gatilho do sensor; implementar fila persistente e reenvio no Edge; ligar a API ao dashboard; implementar autenticação e autorização; testar baixa confiança e medir inspeções ponta a ponta. Não anunciar essas funções como ausentes se já tiverem sido concluídas.

### 13:00 a 14:20: Resultado esperado e impacto no OEE

Mostrar: relação qualitativa entre defeitos identificados, ação do operador e redução esperada de desperdícios/paradas.

> Esperamos que as informações de inspeção ajudem a identificar não conformidades e a investigar as causas dos defeitos recorrentes. Com isso, a proposta é melhorar a qualidade e reduzir as interrupções causadas por esses defeitos. Qualidade e interrupções afetam a eficiência global do equipamento, o OEE. Ainda precisamos avaliar o projeto em operação para medir qualquer ganho nesse indicador.

Explique que a classificação depende da resposta operacional e da integração prevista para trazer benefícios: ela não corrige o processo nem remove fisicamente a peça. Percentuais de melhoria, retorno financeiro e ganhos industriais só devem aparecer se tiverem sido medidos.

### 14:20 a 15:00: Fechamento

Mostrar: nome do projeto, equipe e endereço do repositório.

> O Vigi propõe identificar defeitos antes do empacotamento, com processamento local e uma montagem que reúne a placa e a câmera na case. Mostramos [escopo real] e o que ainda falta validar. Com o dashboard, esperamos facilitar o acompanhamento pelos responsáveis e apoiar decisões com os registros das inspeções. O código e a documentação estão no repositório do projeto. Obrigado.

## 7. Preparação e verificação da Entrega 3

- [ ] Distribuir as falas entre os integrantes, incluindo as trocas no tempo de cada bloco.
- [ ] Preencher modelo, equipamento, comandos, resultados e pendências com evidências atuais.
- [ ] Selecionar os apoios visuais e preparar a bancada e a captura de tela.
- [ ] Conferir o conteúdo da case e registrar suas dimensões, se forem citadas; mostrar os elementos externos da instalação.
- [ ] Ensaiar a consulta por `inspection_id` com backend e broker ativos; identificar `/docs` como documentação da API.
- [ ] Registrar o estado do dashboard e escolher a apresentação correspondente: integrado, interface com dados simulados ou proposta.
- [ ] Para qualquer afirmação de operação offline, registrar o teste, as funções verificadas e a conexão indisponível. Se houver acesso remoto, planejar a captura local antes de interromper a rede.
- [ ] Conferir as falas sobre segurança e acesso: processamento local não comprova segurança; público previsto não comprova restrição de acesso.
- [ ] Ensaiar as quatro partes, buscando terminar em 14 min 30 s para absorver pequenas pausas sem ultrapassar 15 minutos.
- [ ] Preservar os cinco minutos reservados à demonstração; ajustar primeiro repetições na narração.
- [ ] Conferir as transições: problema → solução → demonstração → conclusão.
- [ ] Confirmar que a conclusão retoma problema, solução e resultado esperado.
- [ ] Validar este esboço com a equipe antes da gravação definitiva.

| Critério de nível Avançado | Localização neste documento |
| --- | --- |
| Conteúdo e tempo de cada parte | Distribuição do tempo e roteiro detalhado das quatro partes |
| Problema conduz à solução | Fechamento da introdução e abertura da solução |
| Solução conduz à demonstração | Tecnologia central e transição às amostras reais |
| Conclusão retoma problema, solução e resultado previsto | Síntese da evidência, impacto esperado e fechamento |
| Quatro partes dentro de 15 minutos | Cronograma de 00:00 a 15:00, com demonstração de 06:00 a 11:00 |

O esboço textual está preparado. Faltam o ensaio, a validação da equipe e a gravação. O funcionamento do hardware e a conclusão da issue #13 precisam de evidências próprias.
