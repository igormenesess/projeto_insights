# Projeto de Insights

O objetivo desse projeto é fornecer uma relatório recomendação de imóveis, dadas as melhores condições, para que a empresa possa realizar suas operações de compra e venda. Os insights fornecidos neste projeto visam maximizar os lucros através da seleção de imóveis que representem oportunidades dentro da base de dados.

A ferramenta de visualização utilizada nesse projeto - Streamlit, permitirá que a empresa possa visualizar esse resultado de forma gráfica, tabular e através de mapas de localização.

O resultado geral obtido foi uma seleção de __14 imóveis__ . Assumindo que o time de negócios definiu a premissa de encontrar imóveis que tenham ótimas condições e vendê-los pelo preço de um desvio padrão acima da média, o lucro que poderá ser obtido com as operações é de __$ 3.028.587,95__

| __Número de imóveis__ | __Lucro__ |
| ----------------- | ----------------- |
| 14 | $ 3.028.587,95 | 

Link para visualização:  [<img alt="Heroku" src="https://img.shields.io/badge/heroku-%23430098.svg?style=for-the-badge&logo=heroku&logoColor=white"/>](https://analytics-projeto-insights.herokuapp.com)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


## Dados

O conjunto de dados que representam o contexto está disponível na plataforma do Kaggle. O link para acesso aos dados :

[https://www.kaggle.com/datasets/harlfoxem/housesalesprediction](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)


## 1. A House Rocket

### 1.1 Contexto do negócio:

A House Rocket é uma plataforma digital que tem como modelo de negócio, a compra e a venda de imóveis usando a tecnologia para analisar suas melhores oportunidades.

O objetivo do case é fornecer insights para a empresa encontrar as melhores oportunidades de negócio no mercado de imóveis. O CEO da House Rocket gostaria de ***maximizar*** a receita da empresa encontrando ***boas oportunidades*** de negócio.

Sua principal estratégia é ***comprar boas casas*** em ótimas localizações com preços baixos e depois revendê-las posteriormente a preços mais altos. Quanto maior a diferença entre a compra e a venda, maior o lucro da empresa.

Entretanto, as casas possuem muitos atributos que as tornam mais ou menos atrativas aos compradores e vendedores, e a localização e o período do ano também podem influenciar os preços.

### 1.2 Questão do negócio:

Considerando que:

a) O time do negócio não consegue tomar boas decisões de compra sem analisar os dados,e;

b) O portfólio é muito grande, o que levaria muito tempo para fazer o trabalho manualmente.

O objetivo desse projeto é fornecer uma seleção de imóveis, dadas as melhores condições, para que a empresa possa realizar suas operações de compra e venda. 
O planejamento é demonstrar através de visualizações, quais as melhores oportunidades e qual resultado (lucro) máximo que pode ser alcançado.

Em suma, o projeto visa responder às seguintes perguntas de negócio:

- Quais são os imóveis que a House Rocket deveria comprar e por qual preço ?
 - Uma vez a casa comprada, qual o melhor momento para vendê-las e por qual preço ?

### 1.3 Sobre os dados:

Os dados foram extraídos do link abaixo, onde constam todos os imóveis em portfólio e disponíveis para a empresa.

https://www.kaggle.com/harlfoxem/housesalesprediction

Os atributos dos imóveis dentro do portfólio e seus respectivos significados, são os seguintes:

|***Atributo*** | ***Descrição*** |
| -------- | --------- |
|**id** | Numeração única de identificação de cada imóvel |
|**date** | Data da venda da casa |
|**price** | Preço que a casa está sendo vendida pelo proprietário |
|**bedrooms** | Número de quartos |
|**bathrooms** | Número de banheiros (0.5 = banheiro em um quarto, mas sem chuveiro) |
|**sqft_living** | Medida (em pés quadrado) do espaço interior dos apartamentos |
|**sqft_lot** | Medida (em pés quadrado)quadrada do espaço terrestre |
|**floors** | Número de andares do imóvel | 
|**waterfront** | Variável que indica a presença ou não de vista para água (0 = não e 1 = sim) | 
|**view** | Um índice de 0 a 4 que indica a qualidade da vista da propriedade. Varia de 0 a 4, onde: 0 = baixa 4 = alta | 
|**condition** | Um índice de 1 a 5 que indica a condição da casa. Varia de 1 a 5, onde:1 = baixo 5 = alta | 
|**grade** | Um índice de 1 a 13 que indica a construção e o design do edifício. Varia de 1 a 13, onde: 13 = baixo, 7 = médio e 1113 = alta | 
|**sqft_basement** | A metragem quadrada do espaço habitacional interior acima do nível do solo | 
|**yr_built** | Ano de construção de cada imóvel | 
|**yr_renovated** | Ano de reforma de cada imóvel | 
|**zipcode** | CEP da casa | 
|**lat** | Latitude | 
|**long** | Longitude | 
|**sqft_livining15** | Medida (em pés quadrado) do espaço interno de habitação para os 15 vizinhos mais próximo | 
|**sqft_lot15**| Medida (em pés quadrado) dos lotes de terra dos 15 vizinhos mais próximo | 

### 1.5 Premissas do negócio:

Dentro do processo de entendimento de negócio, exploração dos dados e decisão para fornecer os insights finais, foram adotadas as seguintes premissas:

- Os valores iguais a zero em *yr_renovated* são casas que nunca foram reformadas;
- O valor igual a 33 na coluna *bathroom* foi considerada um erro e por isso foi delatada das análises. Possivelmente poderia ser um erro de digitação, mas por falta dessa clareza, a exclusão foi optada;
- A coluna *price* significa o preço que a casa foi ou será comprada pela empresa House Rocket;
- Valores duplicados em *id* foram removidos e considerados somente a compra mais recente
- Dado que a __localidade__ e a __condição__ são os principais fatores que influenciam na valorização ou desvalorização dos imóveis, essas foram características decisivas na seleção ou não dos imóveis
- Para as condições dos imóveis, foi determinada a seguinte classificação: __1 = péssimo, 2 = ruim, 3 = regular, 4 = bom e 5 = excelente__

__A premissa de negócio foi baseada em  encontrar imóveis que tenham ótimas condições e vendê-los pelo preço de um desvio padrão acima da média, se baseando no preço por área para tomar uma decisão mais assertiva.__

## 2. Planejamento da solução:

### 2.1  Exploração de dados:

A primeira etapa do projeto foi realizar a coleta, tratamento e exploração dos dados. Nessa etapa foi possível realizar identificar necessidades de limpeza e transformação de dados, realizar uma análise das estatísticas descritivas dos conjuntos de dados, e ainda realizar a criação de novas *features* para facilitar e proporcionar as visualizações e criações dos insights que serão apresentados. 

### 2.2  Seleção dos imóveis:

Todo planejamento dessa solução foi pensando na criação de um aplicativo de visualização, onde a empresa poderá consultar a seleção dos imóveis, seus insights e outras informações inerentes às perguntas de negócio.

### 2.3  Planejamento da análise dos Insights:

Dentre os imóveis selecionados como sugestão de compra e venda, foram feitas algumas análises para se encontrar insights, com o objetivo de maximizar o resultado esperado, oferecendo estratégias para a tomada de decisão.

Ou seja, foram planejados dois grupos de insights dentro do projeto. Os diretamente ligados aos imóveis selecionados, e outro considerando todas as informações do portfólio, com o objetivo de gerar informações possivelmente desconhecidas e que possam vir a ser objetos de novas questões de negócio.

## 3. Principais insights:
Tendo todo entendimento do negócio, e respondida as perguntas de negócio, foram levantadas algumas hipóteses para serem validadas, com o objetivo de gerar insights para próximas questões de negócio ou mesmo gerar novas estratégias para a House Rocket:

| __Hipótese__ | __Resultado__ | __Tradução para negócio__ |
| ------------ | ------------ | ------------ |
| __H1__ - Os imóveis com mais quartos tem o preço maior. | Falsa | O preço por área dos imóveis não aumenta ou diminui com o aumento do número de quartos. |
| __H2__ - Os imóveis com vista para água são mais caros. | Verdadeira | Os imoveis com vista para agua são em média 93.3% mais caros. |
| __H3__ - O verão é a melhor época do ano para se vender imóveis. | Falsa | Não se observou uma variação significativa de preços em relação a época do ano nessa base de dados. |
| __H4__ - Os imoveis mais atuais ou reformados recentemente são mais caros. | Falsa | Não se observou uma variação significativa de preços em relação ao ano de construção ou reforma do imóvel nessa base de dados. |
| __H5__ - Imóveis com melhores condições tem preços maiores. | Verdadeira | Conforme as condições dos imóveis melhoram os preços aumentam.|

## 4. Resultados financeiros:

O objetivo desse projeto era fornecer uma lista de imóveis com opções de compra e venda, e consequentemente o lucro que poderá ser obtido se todas as transações ocorrerem. Ou seja, o resultado financeiro apresentado abaixo representa o lucro máximo que pode ser obtido utilizando as recomendações informadas.

| __Número de imóveis__ | __Lucro__ |
| ----------------- | ----------------- |
| 14 | $ 3.028.587,95 | 

## 5. Conclusão:

O projeto tem como princípio a geração de insights para o negócio, assim como responder algumas perguntas feitas pela empresa. O objetivo foi concluído, e foi possível extrair informações relevantes e com potencial forma de gerar direcionamento para as próximas operações da House Rocket.

As visualizações fornecidas irão permitir com que a empresa possa avaliar as regiões mais lucrativas, os atributos que levam o imóvel a se tornar mais viável para as operações de compra e venda, e ainda visualizar o lucro máximo que poderá ser alcançado de acordo com as opções de negócio.
