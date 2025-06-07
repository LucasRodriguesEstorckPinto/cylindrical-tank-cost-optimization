PORTUGUESE

# Otimização do Custo de um Tanque Cilíndrico

Aplicativo gráfico interativo para resolver um problema real de otimização com restrições, baseado no projeto de um tanque cilíndrico para transporte de resíduos tóxicos. Este projeto foi desenvolvido como parte da disciplina de Métodos Numéricos de Otimização.

## 📐 Descrição do Problema

O objetivo é **minimizar o custo total** de construção de um tanque cilíndrico, considerando:
- Custo do material (massa)
- Custo da soldagem (comprimento dos cordões)

### Função Objetivo:

\[
C(D, L) = 4.5 \cdot m(D, L) + 20 \cdot \\ell_w(D)
\]

### Restrições:

\[
0.9V_0 \\leq \\frac{\\pi D^2}{4} L \\leq 1.1V_0, \quad D \\leq 1, \quad L \\leq 2
\]

## 🚀 Funcionalidades

A aplicação foi desenvolvida com uma interface moderna e intuitiva usando `CustomTkinter` e segue o padrão de arquitetura **MVC**.

### ✅ Funcionalidades obrigatórias (do enunciado):

- [x] Interface gráfica interativa com múltiplos métodos de otimização
- [x] Controle total dos parâmetros (passo, critério de parada, ponto inicial)
- [x] Exibição dos resultados numéricos (iterações, avaliações, solução)
- [x] Curvas de nível da função objetivo com trajetória
- [x] Gráfico de evolução do erro

### 🌟 Funcionalidades adicionais (entrega extra):

- [x] Página inicial com explicação visual do problema e fórmulas em LaTeX
- [x] Layout com múltiplas abas e navegação organizada
- [x] Renderização gráfica moderna com suporte a temas escuro/claro
- [x] Explicações teóricas embutidas sobre os métodos (Steepest, Newton, DFP)
- [x] Validação em tempo real das entradas
- [x] Imagem ilustrativa do tanque embutida na interface
- [x] Tabela com evolução iterativa completa (scrollable)
- [x] Arquitetura modular (MVC) que facilita manutenção e extensões futuras
- [x] Código 100% autoral, sem uso de bibliotecas prontas de otimização

## 🧱 Estrutura do Projeto

ENGLISH

# 🛢️ Cylindrical Tank Cost Optimization

Interactive graphical application to solve a real-world constrained optimization problem, based on the design of a cylindrical tank for transporting toxic waste. This project was developed as part of the *Numerical Optimization Methods* course.

## 📐 Problem Description

The objective is to **minimize the total cost** of building a cylindrical tank, considering:
- Material cost (mass)
- Welding cost (length of welds)

### Objective Function:

\[
C(D, L) = 4.5 \cdot m(D, L) + 20 \cdot \ell_w(D)
\]

### Constraints:

\[
0.9V_0 \leq \frac{\pi D^2}{4} L \leq 1.1V_0, \quad D \leq 1, \quad L \leq 2
\]

## 🚀 Features

The application is built with a modern and intuitive interface using `CustomTkinter` and follows the **MVC architecture pattern**.

### ✅ Required Features (as per assignment):

- [x] Interactive GUI with multiple optimization methods
- [x] Full control over parameters (step size, stopping criteria, initial guess)
- [x] Numerical output (iterations, evaluations, solution)
- [x] Contour plot of the objective function with iteration trajectory
- [x] Error evolution graph

### 🌟 Extra Features (above and beyond):

- [x] Introductory page with a visual explanation of the problem and LaTeX-rendered formulas
- [x] Clean layout with multiple tabs and organized navigation
- [x] Modern plotting and appearance mode (dark/light theme)
- [x] Embedded theoretical explanations of each method (Steepest Descent, Newton, DFP)
- [x] Real-time input validation
- [x] Embedded illustration of the tank geometry
- [x] Scrollable table showing complete iteration history
- [x] Modular MVC architecture for easier maintenance and extension
- [x] 100% original code, without using any ready-made optimization libraries

## 🧱 Project Structure

