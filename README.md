# jmbelem Gestão — versão Python Kivy

Esta pasta contém uma versão Android independente do aplicativo. Ela abre o
sistema de faturação dentro de um WebView nativo Android e guarda o link
configurado localmente no telefone.

## O que já está incluído

- Link inicial configurado para o sistema jmbelem Gestão.
- Tela para alterar e guardar outro link `https://`.
- WebView Android com JavaScript, armazenamento local e cookies ativados.
- Botões nativos de menu, voltar, avançar, atualizar e configurações.
- Rotação vertical e horizontal (`orientation = all`).
- Ícone do aplicativo.

## Como gerar o APK

Use Linux, WSL ou macOS com Python, Java, Android SDK e Buildozer instalados.
Dentro desta pasta, execute:

```bash
pip install buildozer cython
buildozer -v android debug
```

O APK será criado na pasta `bin/`.

Para gerar uma versão de distribuição, use o modo de release do Buildozer e
assine o APK conforme o processo de publicação Android que você utiliza.

## Observação

O aplicativo usa `pyjnius` para criar o WebView Android nativo. Por isso, o
APK deve ser compilado para Android; executar `main.py` no computador serve
apenas para visualizar a tela de configuração, não para reproduzir o WebView
nativo.