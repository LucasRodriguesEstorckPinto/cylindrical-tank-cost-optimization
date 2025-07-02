PORTUGUESE

# Otimização do Custo de um Tanque Cilíndrico

Aplicação gráfica com o intuito de Otimizar o custo de um Tanque cilíndrico , respeitando as restrições impostas no enunciado do trabalho. A aplicação foi desenvolvida utilizando a versão 3.13.5 da linguagem Python, diferente do indicado em aula, preferi implementar a interface gráfica usando a biblioteca CustomTkinter, na qual além de ser simples e leve, supre todas as necessidades do problema apresentado. 

## Descrição do Problema

O objetivo é **minimizar o custo total** de construção de um tanque cilíndrico, considerando:
- Custo do material (massa)
- Custo da soldagem (comprimento dos cordões)

### Função Objetivo:

![Função Objetivo](https://latex.codecogs.com/png.latex?%5Ccolor%7Bwhite%7D%20C(D%2C%20L)%20%3D%204.5%20%5Ccdot%20m(D%2C%20L)%20%2B%2020%20%5Ccdot%20%5Cell_w(D))


### Restrições:

![Restrições](https://latex.codecogs.com/png.latex?%5Ccolor%7Bwhite%7D%200.9V_0%20%5Cleq%20%5Cfrac%7B%5Cpi%20D%5E2%7D%7B4%7D%20L%20%5Cleq%201.1V_0%2C%20%5Cquad%20D%20%5Cleq%201%2C%20%5Cquad%20L%20%5Cleq%202)


## Funcionalidades
    
A aplicação foi desenvolvida com uma interface moderna e intuitiva usando `CustomTkinter` e segue o padrão de arquitetura **MVC**.

### Funcionalidades obrigatórias:

- [x] Interface gráfica interativa com múltiplos métodos de otimização ;
- [x] Controle total dos parâmetros (passo, critério de parada, ponto inicial) ;
- [x] Exibição dos resultados numéricos (iterações, avaliações, solução) ;
- [x] Curvas de nível da função objetivo com trajetória ;
- [x] Gráfico de evolução do erro.

### Funcionalidades adicionais:

- [x] Renderização gráfica moderna com suporte a temas escuro/claro
- [x] Validação em tempo real das entradas
- [x] Arquitetura modular (MVC) que facilita manutenção e extensões futuras



ENGLISH

#  Cylindrical Tank Cost Optimization

Graphical application with the purpose of protecting or reducing the cost of a cylindrical tank, respecting the unannounced restrictions imposed by the work. The application was developed using Python 3.13.5, different from the one indicated in class, preferring to implement a graphical interface using the CustomTkinter library, which version, in addition to being simple and lightweight, meets all the needs of the problem presented.

##  Problem Description

The objective is to **minimize the total cost** of building a cylindrical tank, considering:
- Material cost (mass)
- Welding cost (length of welds)

### Objective Function:

![Objective Function](https://latex.codecogs.com/png.latex?%5Ccolor%7Bwhite%7D%20C(D%2C%20L)%20%3D%204.5%20%5Ccdot%20m(D%2C%20L)%20%2B%2020%20%5Ccdot%20%5Cell_w(D))

### Constraints:

![Constraints](https://latex.codecogs.com/png.latex?%5Ccolor%7Bwhite%7D%200.9V_0%20%5Cleq%20%5Cfrac%7B%5Cpi%20D%5E2%7D%7B4%7D%20L%20%5Cleq%201.1V_0%2C%20%5Cquad%20D%20%5Cleq%201%2C%20%5Cquad%20L%20%5Cleq%202)

##  Features

The application is built with a modern and intuitive interface using `CustomTkinter` and follows the **MVC architecture pattern**.

###  Required Features:

- [x] Interactive GUI with multiple optimization methods
- [x] Full control over parameters (step size, stopping criteria, initial guess)
- [x] Numerical output (iterations, evaluations, solution)
- [x] Contour plot of the objective function with iteration trajectory
- [x] Error evolution graph

###  Extra Features:

- [x] Modern graphical rendering with support for dark/light themes
- [x] Real-time validation of inputs
- [x] Modular architecture (MVC) that facilitates maintenance and future extensions
