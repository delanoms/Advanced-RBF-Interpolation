# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-01-XX

### Adicionado

- Interpolação RBF avançada com 7 funções de base radial
  - Thin Plate (placa fina)
  - Multiquadric (multiquadrática)
  - Inverse Multiquadric (multiquadrática inversa)
  - Gaussian (gaussiana)
  - Linear
  - Cubic (cúbica)
  - Quintic (quíntica)
- Controle de vizinhança para interpolação local
- Métodos de extrapolação:
  - Nenhum (mantém NaN)
  - Valor constante
  - Vizinho mais próximo
  - Interpolação linear
- Otimização para grandes volumes de dados
- Parâmetro de suavização configurável
- Saída raster georreferenciada compatível com QGIS
- Integração completa com o framework de Processing do QGIS

### Funcionalidades Técnicas

- Algoritmo de interpolação RBF otimizado
- Busca eficiente de vizinhos usando KD-Tree
- Tratamento de valores NaN e extrapolação
- Clipping automático para evitar valores extremos
- Suporte a diferentes sistemas de coordenadas

### Documentação

- README completo em português
- Documentação de parâmetros detalhada
- Exemplos de uso e configuração
- Licença GPL v3

### Estrutura do Projeto

- Código modular e bem organizado
- Testes unitários incluídos
- Configuração para controle de versão
- Arquivos de build e distribuição

---

## [0.1.0] - 2025-06-16

### Adicionado

- Versão inicial do plugin
- Estrutura básica do QGIS Plugin Builder
- Algoritmo de interpolação RBF básico
