# Entrega 2 — Roteiro de demonstração da PoC do Vigi

**Duração prevista:** 5 minutos.  
**Versão:** rascunho inicial para ensaio, 11/09/2026.  
**Vínculo:** [issue #13](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13), entregável de roteiro da demonstração prática.  
**Dependência de execução:** [issue #11](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11), modelo e pipeline de inferência na Raspberry Pi 5.

## 1. Objetivo e recorte

Demonstrar a viabilidade inicial da classificação visual de recipientes: apresentar uma entrada identificável, executar a inferência e mostrar o resultado correspondente em uma sequência acompanhável.

Este vídeo é a PoC da Entrega 2, com publicação prevista como **não listado no YouTube**. O [pitch final de até 15 minutos — Entrega 3](../pitch/01-roteiro-pitch.md) é outro vídeo, com roteiro próprio. O [README — Entrega 4](../../README.md) organiza o esboço da documentação. Esses materiais também fazem parte da issue #13.

**Sequência principal proposta:** recipiente na bancada → imagem da câmera → modelo na Raspberry Pi 5 → classe prevista na tela ou no terminal. A câmera é o outro elemento da arquitetura que deve funcionar junto da tecnologia central, a inferência. Não é necessário antecipar a integração completa para demonstrar esse recorte.

O roteiro pode ser preparado enquanto a issue #11 é finalizada. A gravação depende de verificar o modelo e a execução real. Na revisão local usada para este documento, o repositório disponibiliza o coletor de dataset, que **não executa inferência**; portanto, seu comando não deve ser apresentado como execução do classificador.

## 2. Preparação da bancada e da tela

- Separar um recipiente conforme e outro com um defeito visível pertencente às classes efetivamente disponíveis no modelo. Preferir `sem_tampa` pela facilidade de identificação visual, se essa classe estiver operacional.
- Manter iluminação, fundo e enquadramento consistentes. Identificar as amostras como A e B para relacionar cada entrada à respectiva saída.
- Exibir a Raspberry Pi e a câmera e explicar onde o processamento acontece. Se houver notebook conectado por acesso remoto, identificá-lo como tela de acesso, quando esse for seu papel real.
- Organizar a gravação para mostrar a bancada e a saída legível, por enquadramento conjunto ou captura de tela com imagem da bancada sobreposta. Mostrar o quadro realmente usado pelo modelo, quando disponível.
- Usar a interface existente da inferência: terminal ou janela já são suficientes. Não é necessário criar dashboard para este vídeo.
- Ensaiar o acionamento real, manual ou contínuo, e declará-lo na fala. Só atribuir a captura ao sensor E18-D80NK se essa integração estiver funcionando.

### Dados a preencher após a entrega da issue #11

| Item | Registro para o ensaio |
| --- | --- |
| Responsável pela apresentação e pela operação | A definir com a equipe |
| Modelo, versão e caminho dos pesos usados | A confirmar |
| Classes presentes no modelo exportado | A confirmar |
| Equipamento que executa a inferência | Confirmar Raspberry Pi 5; registrar se for outro |
| Câmera e forma de captura/acionamento | A confirmar |
| Comando real de execução e diretório de trabalho | A preencher após teste na bancada |
| Saída disponível | Confirmar classe, score e eventual tempo medido |
| Evidência do ensaio | Registrar amostras, saídas reais e limitações observadas |

## 3. Roteiro de gravação — 00:00 a 05:00

As falas são sugestões; substituir os campos entre colchetes por informações verificadas. Os intervalos incluem operação da bancada, troca de amostras e tempo para leitura da tela, além da narração.

### 00:00–00:30 — Apresentação e objetivo (30 s)

**Imagem/ação:** apresentador e bancada, com o nome Vigi e a identificação “Entrega 2 — Prova de Conceito”.

**Fala sugerida:**

> “Este é o Vigi, um projeto de inspeção visual de recipientes em linhas de envase. A proposta é identificar recipientes conformes e defeitos visíveis, como ausência de tampa. Nesta prova de conceito, vamos mostrar a tecnologia central: uma imagem entra no modelo, a inferência é executada e a classificação aparece na tela. O foco desta entrega é verificar esse funcionamento inicial.”

### 00:30–01:10 — Elementos e caminho da informação (40 s)

**Imagem/ação:** apontar o recipiente, a câmera, a Raspberry Pi e a tela. Exibir brevemente o fluxo `Câmera → Inferência na Raspberry Pi → Resultado`.

**Fala sugerida, após confirmar a montagem:**

> “O recipiente é o objeto inspecionado. A câmera fornece a imagem de entrada. A Raspberry Pi 5 executa o modelo [nome e versão], treinado para distinguir [classes disponíveis]. A tela permite acompanhar a imagem e a saída do processamento. Nesta montagem, a captura é [manual/contínua/acionada pelo sensor]. Assim, mostramos a inferência trabalhando com a câmera, que já é um componente previsto na arquitetura do Vigi.”

**Atenção:** usar apenas a modalidade real de captura e as informações efetivamente exibidas.

### 01:10–02:20 — Primeiro ciclo: recipiente conforme (70 s)

**Imagem/ação, em sequência contínua:**

1. Mostrar a amostra A e explicar por que ela é visualmente conforme.
2. Posicioná-la diante da câmera e mostrar sua imagem de entrada.
3. Iniciar a execução pelo comando validado ou evidenciar o próximo ciclo, caso o processo já esteja rodando.
4. Acompanhar o processamento e manter o resultado legível por alguns segundos, sem corte entre entrada e saída.

**Fala sugerida:**

> “Esta é a amostra A, com a tampa posicionada e sem o defeito que vamos mostrar depois. Esta imagem é a entrada desta execução. Agora [ação real que inicia o ciclo]. O programa fornece a imagem ao modelo e obtém a classificação. A saída para esta amostra foi [classe observada]. [Se disponível: o score exibido foi valor observado.] Esse resultado corresponde ao recipiente que acabamos de apresentar.”

**Interpretação:** comparar a previsão com a condição da amostra. Se houver divergência, relatá-la; não ler uma fala de acerto pré-escrita. Score de uma previsão não é acurácia do modelo.

### 02:20–03:30 — Segundo ciclo: defeito visível (70 s)

**Imagem/ação, em sequência contínua:**

1. Retirar A, mostrar a amostra B e apontar o defeito visível.
2. Apresentar B à câmera, preservando as condições da bancada.
3. Repetir o ciclo e mostrar a nova saída, distinguindo-a do resultado anterior.
4. Comparar a classe retornada com o defeito apresentado.

**Fala sugerida:**

> “Agora usamos a amostra B, que apresenta [defeito visível]. Mantemos a câmera e o enquadramento para acompanhar a mudança da entrada. Executamos novamente o mesmo processo. O modelo retornou [classe observada]. [Se houver acerto: a classificação corresponde ao defeito mostrado.] A troca da amostra permite observar uma nova inferência e o resultado associado à nova imagem.”

**Se houver erro ou instabilidade:** descrever o que ocorreu e a limitação observada. Qualquer repetição deve mostrar novamente a entrada e a execução; não substituir o resultado por texto inserido na edição.

### 03:30–04:15 — Leitura do resultado e alcance da prova (45 s)

**Imagem/ação:** manter a saída real visível e apontar seus campos. Se houver tempo disponível, repetir A para mostrar mais um ciclo, sem tratar a repetição como avaliação estatística.

**Fala sugerida:**

> “A classe indica a previsão do modelo para a imagem apresentada. [Se disponível: este score acompanha a previsão; ele não representa a acurácia global.] Nestes ciclos, observamos [resumo fiel dos resultados]. A demonstração fornece evidência inicial do funcionamento da captura com a inferência nesta bancada. Para avaliar a qualidade do modelo de forma ampla, ainda precisamos considerar os testes com imagens separadas do treinamento.”

**Se houver tempo medido na saída:** explicar o intervalo medido. Tempo de inferência isolado não comprova o RNF01, que considera a inspeção desde a detecção até a disponibilização do resultado. Não afirmar o atendimento à meta de acurácia do RNF06 com base nos dois exemplos do vídeo.

### 04:15–05:00 — Limites e próxima etapa técnica (45 s)

**Imagem/ação:** voltar à bancada ou ao fluxo simplificado. Identificar visualmente o trecho demonstrado e as integrações futuras.

**Fala sugerida, ajustada ao estado real:**

> “Nesta PoC, demonstramos [componentes realmente usados] e os resultados obtidos para as amostras. A próxima etapa técnica é [integração ainda pendente, por exemplo: ligar o gatilho do sensor à captura e à inferência]. Depois, o fluxo previsto inclui registrar os eventos no SQLite e distribuí-los por MQTT para o backend e o dashboard. [Citar somente o que de fato falta integrar.] Também será necessário ampliar os testes de classificação e de tempo do ciclo. Esta entrega apresenta a viabilidade inicial do núcleo de visão computacional do Vigi.”

**Limite de escopo:** não apresentar rejeição mecânica de recipientes como próxima entrega; atuadores estão fora do escopo atual do projeto.

## 4. Alternativa se a captura integrada ainda não estiver disponível

Usar uma imagem previamente capturada é uma alternativa para mostrar a inferência inicial: exibir o arquivo identificado, iniciar o processamento real e mostrar a saída correspondente, sem cortes nesse ciclo. Explicar que a entrada é um arquivo e informar o equipamento real de execução.

Essa alternativa demonstra a inferência sobre imagem, mas não evidencia por si só a câmera funcionando junto do modelo. Para buscar o nível Avançado, priorizar o ciclo com câmera integrada ou mostrar outro elemento arquitetural realmente conectado à inferência. Se a execução ocorrer somente em notebook ou ambiente remoto, não afirmar que a inferência embarcada na Raspberry Pi foi validada.

## 5. Conferência com os critérios da atividade

| Critério informado pela plataforma | Evidência planejada no vídeo |
| --- | --- |
| Entrada ou início da execução identificável | Amostras A e B, imagem de entrada e acionamento visível |
| Tecnologia principal funcionando | Execução real do modelo durante os dois ciclos |
| Resultado produzido | Classe prevista legível e vinculada à amostra correspondente |
| Entrada, execução e resultado em uma sequência acompanhável | Ciclos contínuos de 01:10 a 03:30, sem cortes internos |
| Tecnologia central com outro elemento da arquitetura | Câmera fornecendo a imagem ao pipeline de inferência |
| Explicação da entrada, funcionamento, resultado e função dos elementos | Apresentação da montagem e narração dos ciclos |
| Próxima etapa ou função ainda não integrada/implementada | Encerramento com pendências concretas verificadas no ensaio |
| Artefato solicitado | Link do vídeo não listado no YouTube, com cerca de 5 minutos |

O roteiro foi estruturado para contemplar o nível Avançado descrito na atividade. O atendimento depende da execução e das evidências efetivamente presentes na gravação.

## 6. Checklist do ensaio e da entrega

- [ ] Confirmar com o responsável pela issue #11 os pesos, classes, comando e ambiente de execução.
- [ ] Executar os dois ciclos na bancada e preencher os dados pendentes deste roteiro.
- [ ] Validar o roteiro e dividir apresentação/operação com a equipe.
- [ ] Conferir se a imagem mostrada corresponde à entrada real da inferência.
- [ ] Confirmar a câmera integrada, ou declarar explicitamente a alternativa utilizada.
- [ ] Ajustar as falas de resultado, limitações e próxima etapa ao estado observado.
- [ ] Ensaiar com cronômetro para aproximadamente 5 minutos, preservando o tempo de leitura das saídas.
- [ ] Conferir áudio e legibilidade; manter cada ciclo sem cortes entre entrada e resultado.
- [ ] Revisar a gravação completa e confirmar que não há métricas ou integrações apresentadas sem evidência.
- [ ] Publicar o vídeo como **não listado** no YouTube e testar o acesso pelo link sem a conta do autor.
- [ ] Registrar o link final e enviá-lo à plataforma da atividade.

**Link do vídeo:** pendente de gravação e publicação.

## 7. Referências e alinhamento da issue

- [Issue #13 — documentação e roteiros](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/13).
- [Issue #11 — treinamento e inferência](https://github.com/eldrayan/Vigi-TCCPNAAT/issues/11).
- [Arquitetura do Vigi](../arquitetura/diagrama-arquitetural.md).
- [Requisitos funcionais — US01](../requisitos/02-requisitos-funcionais.md).
- [Requisitos não funcionais — RNF01 e RNF06](../requisitos/03-requisitos-nao-funcionais.md).
- Critérios da Entrega 2 fornecidos na solicitação desta atividade.

A issue #13 menciona sensor, SQLite/MQTT/Node-RED na demonstração. Este roteiro adota o recorte inicial de inferência solicitado para a Entrega 2; não declara concluído o fluxo mais amplo da issue. A arquitetura documentada atualmente prevê FastAPI e React para supervisão, portanto Node-RED não foi incluído como componente da apresentação. A conclusão da issue #13 também depende dos demais entregáveis e da validação com a equipe.
