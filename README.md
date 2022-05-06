<table align="center"><tr><td align="center" width="9999">

<img src="https://i.ibb.co/hgpn23m/Captura-de-Tela-2020-06-27-a-s-00-03-54.png" align="center" width="150" alt="Project icon">

# JION

*Gratidão e piedade*

</td></tr>

</table>    

<div align="center">

> [![Version badge](https://img.shields.io/badge/version-0.0.8-silver.svg)]()

>[![GraphQl Badge](https://badgen.net/badge/icon/graphql/pink?icon=graphql&label)]()
[![Docs Link](https://badgen.net/badge/docs/github_wiki?icon=github)](https://github.com/brunolcarli/Jion/wiki)
![docker badge](https://badgen.net/badge/icon/docker?icon=docker&label)

</div>

<hr />

[Jion](https://pt.wikipedia.org/wiki/Jion) é uma API Graphql responsável pelo backend do chatbot de Inteligência Artificial [Luci](https://github.com/brunolcarli/Luci), contendo dados de armazenamento permanente, ou ainda, em outras palávras, sua memória de longo prazo.

## Rodando localmente

Há um arquivo *template* para definição das variáveis de ambiente em: `jion/environment/template`, crie um novo arquivo contendo suas variáveis e exporte-as:

```
$ source jion/environment/seu_arquivo
```

Você deve estar em um ambiente virtual python, onde poderá instalar as dependências:

```
$ make install
```

A API então poderá ser executada e estará disponível por padrão na porta `6500`

```
$ make run
```

## Docker

A partir do template disponibilizado em `jion/environment/template` você deverá criar um novo arquivo no mesmo diretório chamado `jion_env` contendo seus valores para as variáveis, resultando no arquivo `jion/environment/jion_env`.


Instale o docker-compose. Isso pdoe ser feito através do pip ou do makefile

pip
```
$ pip3 install docker-compose
```

make
```
$ make install
```


Execute o *build* e suba o container com os comandos:

```
$ docker-compose build
$ docker-compose up
```

