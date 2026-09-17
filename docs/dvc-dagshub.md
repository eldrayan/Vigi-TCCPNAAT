# Recuperar modelo e dataset pelo DVC/DagsHub

Execute os comandos na raiz do clone após preparar o ambiente Python pelo
[README](../README.md). O Git guarda ponteiros, código e configuração; o DVC
materializa os pesos e dados. Treinar novamente não é requisito para operar.

## Autenticação e modelo de operação

O remoto `dagshub` em `.dvc/config` usa `s3://dvc`, com endpoint do repositório
`alan-mendes-ufca/Vigi-TCCPNAAT` no DagsHub. A conta autenticada precisa ter acesso
aos objetos desse armazenamento, que é distinto do repositório GitHub.

```bash
make dvc-login
uv run --no-sync python scripts/dvc_dagshub.py pull models.dvc
```

Conclua a autorização interativa apresentada pelo DagsHub. O script obtém o token
armazenado pelo login e fornece `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY`
apenas ao subprocesso DVC. Não cole tokens no Git, no `.env.example` ou no manual.

`make model-pull` chama DVC diretamente e **não executa essa ponte de
credenciais**. Para o fluxo de login acima, use o comando explícito com o script.
Não é necessário baixar o dataset para iniciar o Edge com modelo promovido.

Confirme o contrato do manifesto e a existência do peso que ele referencia:

```bash
uv run --no-sync python - <<'PY'
from pathlib import Path
from model_lifecycle.manifest import ModelManifest
path = Path('models/active/manifest.json')
manifest = ModelManifest.load(path)
weight = manifest.resolve_model_path(path)
assert weight.stat().st_size > 0, 'Peso vazio'
print('Manifesto válido:', path)
print('Peso presente:', weight)
print('Formato:', manifest.format)
print('Classes:', ', '.join(manifest.classes))
print('Limiar de confiança:', manifest.confidence_threshold)
PY
```

Espera-se formato `pytorch`, peso `.pt` e classes `01_conforme`, `02_sem_tampa`,
`03_tampa_torta`, `04_amassado`. Essa checagem não carrega a rede nem comprova
acurácia; conclua a inferência por imagem descrita no README. A mensagem
`Everything is up to date` sozinha não comprova que esses arquivos existem.

## Dataset para avaliação ou treinamento

Escolha um ponteiro realmente versionado antes do download:

```bash
git ls-files 'dataset/*.dvc'
uv run --no-sync python scripts/dvc_dagshub.py pull dataset/vigi-cls.dvc
uv run --no-sync python scripts/validar_dataset.py --dataset dataset/vigi-cls
```

Se escolher outro ponteiro listado, substitua **ambos** os caminhos. O validador
exige `train`, `val`, `test` e as quatro classes oficiais. `make dvc-pull
DATASET=dataset/vigi-cls` recupera explicitamente esse dataset e `models.dvc`;
não use outro nome sem conferir a existência do respectivo `.dvc`.

## Diagnóstico

| Resultado | Próxima verificação |
| --- | --- |
| Token ausente ou expirado | Execute `make dvc-login` no mesmo usuário e ambiente que executará o script. |
| `AccessDenied`, `403` ou erro de credencial | Confirme acesso da conta ao remoto DagsHub e uso de `scripts/dvc_dagshub.py`; não publique o token nos logs. |
| Objeto/cache ausente no remoto | Registre o ponteiro e o hash solicitado; o mantenedor precisa disponibilizar os objetos associados. Um clone Git não recupera pesos ausentes. |
| Manifesto ou peso ausente após pull | Confira o conteúdo de `models.dvc` e o erro da checagem acima. Não invente manifesto nem promova outro modelo apenas para contornar o problema. |
| Cache sem permissão | Use cache de propriedade do usuário. Para diagnóstico temporário: `XDG_CACHE_HOME=/tmp DVC_SITE_CACHE_DIR=/tmp/vigi-dvc-site-cache UV_CACHE_DIR=/tmp/vigi-uv-cache uv run --no-sync python scripts/dvc_dagshub.py pull models.dvc`. |
| Dataset sem `val` ou classe obrigatória | Confira se escolheu o artefato correto; não renomeie ou redivida silenciosamente o conjunto publicado. |

Este procedimento descreve recuperação de artefatos existentes. Publicar pesos,
alterar ponteiros e promover modelos são operações separadas de manutenção.
