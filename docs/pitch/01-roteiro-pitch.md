# Entrega 3 — Esboço do vídeo pitch final do Vigi

**Versão:** 0.1 — roteiro para ensaio, 11/09/2026.  
**Duração máxima:** 15 minutos, incluindo demonstração e transições.  
**Issue:** [#13 — Documentação Técnica, Roteiro do Pitch e Demonstração da PoC](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13).

## 1. Proposta narrativa

Recipientes defeituosos podem causar desperdícios e interrupções no empacotamento. Isso motiva uma estação de inspeção visual; sua arquitetura transforma imagens em classificações e eventos para supervisão. A demonstração torna esse caminho observável. A conclusão confronta o que foi demonstrado com o benefício esperado e explicita o trabalho restante.

Este documento planeja o **vídeo final de até 15 minutos**. O [vídeo da PoC da Entrega 2](../poc/01-roteiro-video-poc.md) é outro artefato, de aproximadamente 5 minutos. O pitch tem seu próprio bloco de demonstração: ele pode aproveitar a sequência ensaiada para a PoC, atualizada ao estado final, sem acrescentar mais cinco minutos ao limite total.

As falas abaixo orientam a apresentação. Dados entre colchetes devem ser preenchidos com evidências antes da gravação. A arquitetura é proposta; somente os componentes efetivamente demonstrados devem ser anunciados como implementados e integrados.

## 2. Distribuição do tempo

| Parte obrigatória | Intervalo | Duração | Conteúdo e apoio visual |
| --- | --- | --- | --- |
| Introdução | 00:00–02:30 | 2 min 30 s | Problema, exemplos de defeitos, público e consequências; recipientes e esquema da linha |
| Solução | 02:30–06:00 | 3 min 30 s | Papel do Vigi, arquitetura, classificação e limites; diagrama de blocos |
| Demonstração | 06:00–11:00 | 5 min | Bancada e captura de tela; entrada → processamento → resultado e integrações disponíveis |
| Conclusão | 11:00–15:00 | 4 min | Evidências, limitações, próximos passos e impacto esperado; síntese dos resultados |
| **Total** | **00:00–15:00** | **15 min** | Transições já incluídas nos intervalos |

## 3. Introdução — 00:00–02:30

### 00:00–00:40 — Identificação e contexto

**Mostrar:** nome Vigi, equipe e uma visão da bancada ou esquema da linha de envase.

> “Somos a equipe do Vigi, um sistema embarcado para inspeção visual de recipientes em linhas de envase. Nosso projeto trata de um problema na passagem do envase para o empacotamento: recipientes com defeitos que seguem adiante sem que a não conformidade seja identificada a tempo.”

### 00:40–01:40 — Problema concreto

**Mostrar:** exemplos de recipiente conforme, sem tampa, com tampa torta e amassado. Identificar exemplos ilustrativos como tais.

> “Uma garrafa sem tampa pode derramar o conteúdo; um recipiente deformado pode prejudicar o fluxo no empacotamento. Além da perda de produto, essas ocorrências podem exigir intervenção e interromper a produção. O operador precisa identificar a ocorrência, enquanto o supervisor precisa saber quais defeitos se repetem para orientar a investigação.”

**Desenvolver:** explicar com os recipientes o que distingue cada defeito e em que ponto uma inspeção intermediária poderia ajudar. Não atribuir perdas quantitativas a uma fábrica sem dados reais.

### 01:40–02:30 — Necessidade e transição

**Mostrar:** posição proposta da inspeção entre envase e empacotamento.

> “A necessidade é transformar a observação do recipiente em uma informação de inspeção disponível no momento certo. Por isso, propomos uma estação que reconheça defeitos visuais e disponibilize o resultado para acompanhamento. Essa necessidade conduz à solução que vamos apresentar: combinar aquisição de imagem, inteligência artificial na borda e registro dos eventos.”

## 4. Solução — 02:30–06:00

### 02:30–03:20 — Como o Vigi atua sobre o problema

**Mostrar:** fluxo simplificado e local da estação de inspeção.

> “O Vigi foi concebido para inspecionar cada recipiente no ponto de captura. O modelo classifica a imagem e produz uma informação sobre a condição observada. Esse resultado pode apoiar a intervenção do operador e, com o registro das ocorrências, a análise dos defeitos recorrentes. O protótipo não inclui um mecanismo físico de ejeção.”

### 03:20–04:50 — Elementos e relações da arquitetura

**Mostrar:** [diagrama de blocos no README](../../README.md), destacando cada ligação durante a fala.

> “Na arquitetura proposta, o sensor E18-D80NK detecta a passagem e dispara a captura da câmera. A Raspberry Pi 5 recebe a imagem e executa o processamento e o classificador. O resultado alimenta a decisão e o registro local no SQLite. Os eventos também seguem por MQTT ao broker Mosquitto e ao backend FastAPI. O dashboard React, executado no navegador, consulta o backend para apresentar as informações ao usuário.”

**Desenvolver:** apontar entrada física, imagem, processamento, saída da classificação e consumo dos eventos. Explicar que câmera adquire a imagem, modelo faz a previsão, banco guarda eventos e comunicação distribui informações. Identificar os blocos ainda não integrados, usando o estado verificado antes da gravação.

### 04:50–06:00 — Tecnologia central e transição à prática

**Mostrar:** classes do modelo efetivamente usado e identificação dos pesos; distinguir treinamento de inferência.

> “O núcleo de visão previsto na issue 11 é o classificador YOLOv8n-cls. O treinamento utiliza imagens rotuladas; na inferência, o modelo recebe uma imagem e retorna uma previsão. As classes previstas são conforme, sem tampa, tampa torta e amassado. [Confirmar as classes e o modelo exportado.] Para verificar esse núcleo, vamos acompanhar a entrada e o resultado de duas amostras na montagem real.”

**Desenvolver:** informar onde o modelo foi treinado e onde roda a inferência, após confirmação. Não apresentar score como acurácia nem classificação como detecção de objetos com caixas, se o modelo não produzir caixas.

## 5. Demonstração — 06:00–11:00

**Espaço reservado:** bancada física com câmera, Raspberry Pi e amostras; tela de execução legível. Usar enquadramento conjunto ou captura de tela com a bancada sobreposta. A demonstração ocupa cinco minutos dentro do pitch, com áudio explicando cada ação.

### 06:00–06:40 — Montagem e início

**Ação:** identificar equipamento, câmera, modelo e modo de captura. Mostrar o comando real validado, ou o processo já iniciado com identificação de um novo ciclo.

> “Esta é a montagem usada no teste. [Identificar os elementos reais.] A captura é [modo real], e o processamento ocorre em [equipamento real]. Vamos manter visíveis a entrada utilizada e o resultado correspondente.”

### 06:40–08:00 — Amostra conforme

**Ação:** mostrar a amostra A, posicioná-la, mostrar a imagem, executar a inferência e manter a saída visível. Preservar a continuidade entre entrada e resultado.

> “Esta amostra apresenta [condição observada]. A imagem que estamos mostrando é a entrada do ciclo. Após a execução, a classe retornada foi [resultado real]. [Explicar se corresponde ou diverge da condição da amostra.]”

### 08:00–09:20 — Amostra com defeito

**Ação:** trocar pela amostra B, apontar o defeito e repetir todo o ciclo. Distinguir a nova saída da anterior.

> “Agora a entrada muda: esta amostra apresenta [defeito]. Mantemos as condições da bancada e executamos novamente. A saída foi [resultado real]. Isso nos permite observar o comportamento do modelo para outra condição do recipiente.”

### 09:20–10:20 — Integração e leitura do resultado

**Ação:** explicar a classe e os campos realmente disponíveis. Se sensor, SQLite ou MQTT já estiverem integrados, mostrar o gatilho ou o evento vinculado ao mesmo ciclo por identificador ou horário. Se não estiverem, usar este minuto para repetir uma inferência e explicar a integração câmera/modelo que funciona.

> “O resultado deste ciclo é [resultado]. [Mostrar a evidência da integração disponível.] Os componentes funcionando juntos nesta demonstração são [lista verificada]. Os demais blocos do diagrama permanecem como [estado real].”

### 10:20–11:00 — Síntese e transição

**Ação:** manter a evidência visível e resumir o que acabou de ocorrer.

> “Acompanhamos a entrada, a execução e o resultado de [quantidade real] ciclos. O teste mostrou [observação sustentada pela gravação]. Agora vamos relacionar essa evidência ao objetivo do projeto e explicar os limites e próximos passos.”

**Contingência:** se for necessário usar um trecho gravado anteriormente, identificá-lo e informar a montagem. Se só houver inferência em arquivo, mostrar arquivo → execução → resultado e explicitar a ausência de captura integrada. Não simular uma integração ausente. Uma falha deve ser relatada; encerrar a tentativa dentro do bloco reservado para preservar a conclusão.

## 6. Conclusão — 11:00–15:00

### 11:00–12:00 — Resultado observado e evidência

**Mostrar:** síntese dos ciclos e, se disponíveis, métricas verificadas da issue #11 com conjunto avaliado e ambiente.

> “Partimos do problema de recipientes defeituosos seguindo para o empacotamento. A solução proposta transforma a imagem em uma classificação e prevê o registro dessa informação. Na demonstração, observamos [resultados reais]. Isso sustenta [alcance efetivamente validado], nas condições apresentadas.”

**Desenvolver:** separar exemplos demonstrativos de avaliação do modelo. Se citar acurácia, informar o conjunto não usado no treinamento e sua dimensão. Se citar tempo, informar se é de inferência ou do ciclo completo. Sem medições, apresentar as metas como metas.

### 12:00–13:00 — Limitações e próxima etapa

**Mostrar:** quadro “demonstrado / pendente”, preenchido antes da gravação.

> “Ainda precisamos [pendências verificadas]. A próxima etapa técnica é [ação concreta], seguida de [teste que verificará o resultado]. Também precisamos avaliar o comportamento em mais amostras e condições de iluminação, além do tempo do ciclo completo.”

**Exemplos para selecionar conforme o estado final:** integrar gatilho do sensor à captura; persistir eventos; distribuir eventos e apresentar no dashboard; testar baixa confiança; medir inspeções ponta a ponta. Não anunciar essas funções como ausentes se já tiverem sido concluídas.

### 13:00–14:20 — Resultado esperado e impacto no OEE

**Mostrar:** relação qualitativa entre defeitos identificados, ação do operador e redução esperada de desperdícios/paradas.

> “O resultado esperado é disponibilizar informação de inspeção para apoiar a identificação de não conformidades e a investigação de causas recorrentes. A expectativa é contribuir para a qualidade e para a redução de interrupções associadas a esses defeitos. Essas dimensões se relacionam à eficiência global do equipamento, o OEE. O projeto ainda precisa de avaliação em operação para demonstrar qualquer ganho nesse indicador.”

**Desenvolver:** a classificação sozinha não corrige o processo nem remove fisicamente a peça. O benefício depende da resposta operacional e da integração prevista. Não mostrar percentual de melhoria, retorno financeiro ou ganho industrial sem medição.

### 14:20–15:00 — Fechamento

**Mostrar:** nome do projeto, equipe e endereço do repositório.

> “O Vigi propõe uma inspeção visual embarcada para tornar identificáveis os defeitos de recipientes antes do empacotamento. Apresentamos a arquitetura, demonstramos [escopo real] e indicamos o que falta validar. O resultado esperado é apoiar decisões com informação de inspeção e rastreabilidade. O código e a documentação estão no repositório do projeto. Obrigado.”

## 7. Preparação e verificação da Entrega 3

- [ ] Distribuir as falas entre os integrantes, incluindo as trocas no tempo de cada bloco.
- [ ] Preencher modelo, equipamento, comandos, resultados e pendências com evidências atuais.
- [ ] Selecionar os apoios visuais e preparar a bancada e a captura de tela.
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

**Estado da entrega:** esboço textual preparado; ensaio, validação da equipe e gravação pendentes. Este roteiro não constitui evidência de funcionamento do hardware nem de conclusão da issue #13.
