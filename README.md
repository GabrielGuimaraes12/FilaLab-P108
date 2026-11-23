# FilaLab P108

Calculadora Streamlit para Otimização II. Inclui M/M/s, M/M/s/K, M/M/s/N, M/G/1 e prioridades M/M/s com serviço idêntico. O [guia de revisão](REVISAO_P108.md) reúne os recálculos das quatro listas.

## Rodar localmente

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest -q
```

Execute os comandos dentro da pasta do projeto. A navegação preserva os campos por modelo durante a sessão. Confira a unidade antes de digitar as taxas. Para guardar comparações, exporte o CSV antes de fechar a aba.

## Abrir em um computador da faculdade

Em um aplicativo público do Streamlit Community Cloud, abra o endereço publicado no navegador. O visitante precisa de acesso à internet e ao domínio do aplicativo. Teste em janela anônima na rede da faculdade antes da prova. Confirme com o professor se é permitido usar a ferramenta e se o navegador da prova pode abrir o endereço.

## Implantação

Use um repositório GitHub com o conteúdo desta pasta na raiz, inclua o arquivo de dependências e aponte o [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) para a branch principal e o arquivo `app.py`. Valide a URL publicada abrindo o aplicativo em janela anônima e calculando um cenário. Para um teste simples, use M/M/1, λ=3 por hora e μ=4 por hora. A calculadora deve retornar Lq=2,25 e Wq=0,75 h.
