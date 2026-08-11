<div align="center">
  <img src="static/logo.png" width="128" alt="Logo do Studyn">
  <h1>Studyn Anki Sync</h1>
  <p>Transforme seus estudos no Anki em progresso no ranking global do Studyn.</p>

  <p>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/releases"><img src="https://img.shields.io/github/v/release/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="Versão mais recente"></a>
    <a href="https://github.com/Studyn-Apps/StudynAnkiPlugin/actions/workflows/release.yml"><img src="https://img.shields.io/github/actions/workflow/status/Studyn-Apps/StudynAnkiPlugin/release.yml?style=flat-square&label=release" alt="Automação de release"></a>
    <a href="LICENSE"><img src="https://img.shields.io/github/license/Studyn-Apps/StudynAnkiPlugin?style=flat-square" alt="Licença MIT"></a>
  </p>

  <p>
    <a href="README.md">English</a> ·
    <strong>Português (Brasil)</strong> ·
    <a href="README.es-419.md">Español (Latinoamérica)</a>
  </p>
</div>

O Studyn Anki Sync é o add-on oficial e de código aberto que conecta o Anki
Desktop ao [Studyn](https://studyn.org/anki). Ele envia estatísticas agregadas
das suas revisões com segurança, permitindo acompanhar sua consistência,
comparar o progresso e participar do ranking global sem expor o conteúdo dos
seus cartões.

## Destaques

- **Ranking global:** sua atividade no Anki contribui para o seu perfil no Studyn.
- **Sincronização automática:** as revisões são enviadas em segundo plano após
  seus estudos.
- **Totais confiáveis:** snapshots autoritativos evitam estatísticas duplicadas
  e refletem corretamente revisões desfeitas.
- **Métricas úteis:** revisões, tempo de estudo, respostas Novamente/Difícil/Bom/Fácil,
  totais históricos e sequência atual.
- **Compatível com perfis:** cada perfil do Anki pode ser conectado à sua própria
  conta Studyn.
- **Traduzido:** suporte automático a `pt-BR`, `en-US` e `es-419`.
- **Suporte simplificado:** copie um diagnóstico sanitizado diretamente do Anki.
- **Avisos de atualização:** seja notificado quando houver uma nova versão oficial.
- **Leve:** nenhuma dependência Python externa durante a execução do add-on.

## Privacidade desde a concepção

Somente estatísticas agregadas de estudo são enviadas ao Studyn. O add-on
**nunca envia**:

- textos, perguntas ou respostas dos cartões;
- nomes de baralhos, etiquetas, IDs de cartões ou IDs de notas;
- seu usuário ou sua senha do AnkiWeb;
- o banco de dados da sua coleção ou arquivos de mídia.

O token de autorização fica armazenado localmente em
`user_files/credentials.json` e é separado por perfil do Anki. Você pode
revogá-lo a qualquer momento em **Ferramentas > Studyn > Desconectar**.

Reporte questões de segurança de forma privada conforme o [SECURITY.md](SECURITY.md).

## Requisitos

- Anki Desktop 2.1.50 ou mais recente;
- uma conta no Studyn;
- conexão com a internet para vincular a conta e sincronizar.

O add-on funciona no Anki Desktop. Revisões feitas no AnkiMobile, AnkiDroid ou
em outro cliente serão incluídas depois que esse histórico chegar ao Anki Desktop
e o add-on fizer uma sincronização.

## Instalação

1. Baixe o `.ankiaddon` mais recente em
   [GitHub Releases](https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest)
   ou na [página do Anki no Studyn](https://studyn.org/anki).
2. Abra o arquivo baixado com o Anki Desktop e confirme a instalação.
3. Reinicie o Anki.
4. Abra **Ferramentas > Studyn > Conectar conta**.
5. Autorize a conexão na janela do navegador que será aberta.

O Studyn faz a primeira sincronização assim que a conta é conectada. Para
atualizar o add-on depois, instale o novo `.ankiaddon` sobre a versão existente;
sua autorização local será preservada.

## Uso

O menu **Ferramentas > Studyn** reúne todas as ações do add-on:

| Ação | Finalidade |
| --- | --- |
| **Conectar conta** | Vincula o perfil atual do Anki ao Studyn. |
| **Sincronizar agora** | Envia imediatamente as estatísticas agregadas mais recentes. |
| **Ver status** | Exibe conta, servidor, última sincronização e último erro. |
| **Copiar diagnóstico** | Copia informações técnicas sanitizadas para solicitações de suporte. |
| **Configurar servidor** | Altera o endereço da API, principalmente para desenvolvimento local. |
| **Idioma** | Seleciona a detecção automática ou um idioma compatível. |
| **Desconectar** | Revoga o dispositivo e remove sua autorização local. |

### Idiomas

Por padrão, a interface acompanha o idioma do computador:

- localidades em português do Brasil usam `pt-BR`;
- localidades em espanhol usam `es-419`;
- inglês e idiomas sem tradução usam `en-US`.

Para escolher manualmente, abra **Ferramentas > Studyn > Idioma**, informe
`auto`, `pt-BR`, `en-US` ou `es-419` e reinicie o Anki para atualizar todos os
itens do menu.

## Como a sincronização funciona

A primeira conexão envia os 365 dias de estudo anteriores. As sincronizações
regulares reenviam os 31 dias mais recentes e ampliam automaticamente o período
de recuperação depois de muito tempo offline. Cada requisição contém totais
absolutos de um intervalo de datas; assim, repeti-la não soma as mesmas revisões
duas vezes.

Esses intervalos e limites podem ser ajustados em `config.json`. Consulte
[config.md](config.md) para conhecer todas as opções e
[docs/API_CONTRACT.md](docs/API_CONTRACT.md) para ver o protocolo do backend.

Por padrão, o add-on consulta a API oficial do GitHub Releases no máximo uma
vez a cada 24 horas. Nenhuma credencial do Studyn é enviada nessa requisição e
cada nova versão é avisada apenas uma vez. Defina `check_for_updates` como
`false` para desativar ou altere `update_check_interval_hours` para mudar o
intervalo.

## Solução de problemas

**O navegador mostra `Not Found` ao conectar.**

Abra **Ferramentas > Studyn > Configurar servidor** e confirme que o endereço
aponta para a base da API, incluindo `/api/v1/anki`. No desenvolvimento local,
use `http://127.0.0.1:3000/api/v1/anki` quando o site estiver na porta 3000.

**O ranking ainda não foi atualizado.**

Abra **Ferramentas > Studyn > Ver status** para conferir a última sincronização e
selecione **Sincronizar agora**. Se as revisões vieram de outro cliente Anki,
sincronize esse cliente com o Anki Desktop primeiro.

**A interface está no idioma errado.**

Escolha o idioma em **Ferramentas > Studyn > Idioma** e reinicie o Anki.

Para solicitar suporte, use **Ferramentas > Studyn > Copiar diagnóstico** e
revise o texto antes de compartilhá-lo. Tokens, IDs de dispositivos, identidade
do perfil, conteúdo dos cartões e credenciais presentes em URLs são excluídos ou
ocultados.

## Desenvolvimento

O projeto usa somente a biblioteca padrão do Python durante a execução. Com o
Python 3 instalado, execute os testes e gere o pacote com:

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

O arquivo instalável será criado em `dist/`. Para testar sem usar a API de
produção, inicie o servidor simulado incluído no projeto:

```powershell
python tools/mock_api.py
```

Depois, defina **Ferramentas > Studyn > Configurar servidor** como:

```text
http://127.0.0.1:8765/api/v1/anki
```

Contribuições são bem-vindas. Leia [CONTRIBUTING.md](CONTRIBUTING.md) antes de
abrir um pull request, consulte [CHANGELOG.md](CHANGELOG.md) para ver o histórico
e siga [SECURITY.md](SECURITY.md) para reportar vulnerabilidades em privado.

## Releases

Tags iguais à versão do add-on acionam a automação de release. Por exemplo, ao
enviar `v0.3.1`, o GitHub executa os testes, gera o `.ankiaddon` e seu checksum
SHA-256 e publica os dois arquivos em Releases. O checklist completo para mantenedores está em
[CONTRIBUTING.md](CONTRIBUTING.md#releases).

## Licença

Distribuído sob a [Licença MIT](LICENSE).
