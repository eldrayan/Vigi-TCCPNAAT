# TODO — Configuração manual do MLOps

Este checklist reúne as etapas que precisam ser executadas fora do código para
que os jobs `ML Artifact Check` e `Model Quality Gate` consigam acessar o remote
DVC da Raspberry Pi. Não registre chaves, tokens ou segredos neste arquivo.

## 1. Preparar o acesso SSH à Raspberry Pi

- [ ] Confirmar que a Raspberry Pi está ligada e conectada ao Tailscale com o
  endereço `100.67.236.30`.
- [ ] Confirmar que o servidor SSH está ativo no Pi:

  ```bash
  systemctl status ssh
  ```

- [ ] Criar uma chave SSH Ed25519 exclusiva para o GitHub Actions em uma
  máquina confiável. Não sobrescrever chaves pessoais existentes:

  ```bash
  ssh-keygen -t ed25519 -C "github-actions-vigi" -f ./vigi_ci_ed25519
  ```

- [ ] Adicionar apenas a chave pública `vigi_ci_ed25519.pub` ao arquivo
  `/home/alan/.ssh/authorized_keys` da Raspberry Pi.
- [ ] Conferir no Pi as permissões do diretório e do arquivo:

  ```bash
  chmod 700 /home/alan/.ssh
  chmod 600 /home/alan/.ssh/authorized_keys
  ```

- [ ] Testar a chave antes de cadastrá-la no GitHub:

  ```bash
  ssh -i ./vigi_ci_ed25519 -o IdentitiesOnly=yes alan@100.67.236.30
  ```

- [ ] Guardar a chave privada `vigi_ci_ed25519` em um gerenciador de senhas até
  concluir a configuração. Nunca adicioná-la ao Git.

## 2. Verificar o storage DVC no Pi

- [ ] Confirmar que o diretório compartilhado com o `yolo-edge-api` existe e é
  gravável pelo usuário `alan`:

  ```bash
  mkdir -p /home/alan/dvc-storage
  test -w /home/alan/dvc-storage
  ```

- [ ] Na máquina de desenvolvimento, configurar o caminho da chave somente na
  configuração local do DVC:

  ```bash
  dvc remote modify --local local_remote keyfile /caminho/vigi_ci_ed25519
  ```

- [ ] Confirmar que o remote padrão é o storage já existente:

  ```bash
  dvc remote list
  ```

  Saída esperada:

  ```text
  local_remote  ssh://alan@100.67.236.30/home/alan/dvc-storage (default)
  ```

- [ ] Depois que dataset e modelos existirem, validar leitura e escrita com
  `dvc push` e `dvc pull`.

## 3. Criar a identidade do CI no Tailscale

- [ ] Abrir o console administrativo do Tailscale e acessar **Access controls**.
- [ ] Criar ou confirmar a existência da tag `tag:ci` em `tagOwners`, preservando
  todas as regras já existentes da tailnet.
- [ ] Autorizar `tag:ci` a acessar somente a Raspberry Pi na porta TCP 22. Evitar
  uma regra ampla para todos os dispositivos e portas.
- [ ] Salvar a política e usar a validação do console para confirmar que a regra
  permite:
  - origem: `tag:ci`;
  - destino: Raspberry Pi `100.67.236.30`;
  - serviço: SSH/TCP 22.
- [ ] Abrir **Trust credentials** e criar um OAuth client com uma descrição como
  `GitHub Actions — Vigi`.
- [ ] Conceder ao cliente o escopo gravável `auth_keys` exigido pela GitHub
  Action e associar exatamente a tag `tag:ci`.
- [ ] Copiar imediatamente o Client ID e o Client Secret. O secret não poderá
  ser consultado novamente depois que a tela for fechada.

Referências oficiais:

- [Tailscale GitHub Action](https://github.com/tailscale/github-action#readme)
- [Conectar runners do GitHub à infraestrutura privada](https://tailscale.com/kb/1586/secure-github-runners)

## 4. Cadastrar os secrets no GitHub

- [ ] Abrir o repositório `eldrayan/Vigi-TCCPNAAT` no GitHub.
- [ ] Acessar **Settings → Secrets and variables → Actions**.
- [ ] Criar os seguintes **Repository secrets**, mantendo exatamente estes
  nomes:

  | Secret | Conteúdo |
  |---|---|
  | `TS_OAUTH_CLIENT_ID` | Client ID do OAuth client do Tailscale |
  | `TS_OAUTH_SECRET` | Client Secret do OAuth client do Tailscale |
  | `RPI_SSH_KEY` | Conteúdo completo da chave privada `vigi_ci_ed25519` |

- [ ] Confirmar que `RPI_SSH_KEY` inclui as linhas `BEGIN OPENSSH PRIVATE KEY` e
  `END OPENSSH PRIVATE KEY`.
- [ ] Não criar secrets para host, usuário ou caminho do storage: esses valores
  não são credenciais e já estão definidos na configuração DVC do projeto.

## 5. Publicar os primeiros artefatos DVC

Esta etapa deve ser feita somente quando o dataset externo e os modelos
existirem. Enquanto os dois ponteiros abaixo estiverem ausentes, o workflow
opera em modo de bootstrap e informa que aguarda os artefatos.

- [ ] Copiar o dataset externo já particionado para `dataset/vigi-cls/`.
- [ ] Validar o dataset sem modificá-lo:

  ```bash
  uv run python scripts/validar_dataset.py --dataset dataset/vigi-cls
  ```

- [ ] Rastrear e enviar o dataset ao remote:

  ```bash
  dvc add dataset/vigi-cls
  dvc push dataset/vigi-cls.dvc
  ```

- [ ] Depois do treinamento, promoção e benchmark, rastrear e enviar os modelos:

  ```bash
  dvc add models
  dvc push models.dvc
  ```

- [ ] Adicionar ao Git apenas os ponteiros e arquivos de configuração:

  ```bash
  git add dataset/vigi-cls.dvc models.dvc .gitignore
  ```

- [ ] Conferir antes do commit que nenhum `.pt`, `.tflite`, imagem do dataset ou
  chave privada aparece em `git status`.

## 6. Validar o workflow no GitHub

- [ ] Fazer push da branch contendo `.github/workflows/mlops-ci.yml`.
- [ ] Abrir **Actions → Vigi MLOps — CI e Model Gate**.
- [ ] Executar `Run workflow` manualmente na branch da implementação.
- [ ] Confirmar que os três jobs concluem com sucesso:
  - `Lint & Tests`;
  - `ML Artifact Check`;
  - `Model Quality Gate`.
- [ ] Confirmar nos logs que o runner Tailscale consegue alcançar o Pi e que o
  DVC recupera `dataset/vigi-cls.dvc` e `models.dvc`.
- [ ] Baixar o artifact `model-quality-gate` e conferir `metrics.json`,
  `predictions.csv` e `confusion-matrix.png`.

## 7. Tornar os checks obrigatórios

Esta etapa só pode ser concluída depois que o workflow executar ao menos uma
vez e os nomes dos checks aparecerem no GitHub.

- [ ] Abrir **Settings → Rules → Rulesets** ou a regra de proteção da branch
  `main`.
- [ ] Exigir pull request antes de merge.
- [ ] Exigir que estes status checks estejam aprovados:
  - `Lint & Tests`;
  - `ML Artifact Check`;
  - `Model Quality Gate`.
- [ ] Manter o deploy automático desativado até que a aplicação e o container
  finais sejam definidos.

## Diagnóstico rápido

- `requested tags ... are invalid or not permitted`: conferir se o OAuth client
  possui `auth_keys` gravável e exatamente `tag:ci`.
- `Permission denied (publickey)`: conferir a chave pública em
  `authorized_keys`, o usuário `alan`, as permissões SSH e o conteúdo de
  `RPI_SSH_KEY`.
- `Connection timed out`: confirmar que o Pi está online no Tailscale e que a
  política permite `tag:ci` → Pi na porta 22.
- Falha no `dvc pull`: testar primeiro a mesma chave e o mesmo remote na máquina
  local com `dvc pull -v`.
- Em caso de exposição de qualquer chave ou OAuth secret, revogar imediatamente
  a credencial no Tailscale/GitHub e gerar outra.
