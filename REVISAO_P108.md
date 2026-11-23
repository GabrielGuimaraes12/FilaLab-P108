# Revisão das listas P108

Foram conferidos os 34 exercícios dos quatro PDFs de exercícios da pasta da disciplina. O exercício 7 de prioridades também usa o Exemplo 1 do PDF teórico de M/G/1 e prioridades. Os tempos abaixo estão na unidade indicada. Arredonde no final do cálculo.

## M/M/s · 15 exercícios

| Nº | Recalculo e leitura do enunciado |
|---|---|
| 1 | A média ponderada normalizada é λ=12/mês. O gabarito equivale a M/M/1 com μ=16/mês e ρ=0,75. Nesse cenário, W=0,25 mês, ociosidade=25%, P(fila≤4)=1−0,75⁶=0,8220, Lq=2,25, Wq=0,1875 mês e L=3 equipamentos. Em mês de 30 dias, P(W>20 dias)=0,0695 e P(Wq>15 dias)=0,1015. O valor 0,7627 corresponde a P(sistema≤4). O texto chama 0,75 de tempo e omite a unidade e o número de servidores. Se 0,75 for Wq em meses com s=1, Lq=9 e ρ≈0,9083, então o conjunto de respostas muda. |
| 2 | Com ρ=0,8 e Wq=15 min, W=Wq/ρ=18,75 min, λ=12,8/h e μ=16/h. Em dias corridos, W≈0,01302 dia. Lq=3,2, L=4, P₀=0,20, P(W>30 min)=0,2019, P(Wq>15 min)=0,3595, P(10 chegadas/h)=0,0898 e P(X=10)=0,0215. Poisson com média 16 fornece P(12)=0,0661 para capacidade potencial com servidor continuamente ocupado. Para saídas efetivas estacionárias em M/M/1, a taxa é 12,8/h e P(12)=0,1115. |
| 3 | Lq=ρ²/(1−ρ)=3,2 implica ρ=0,8. W=0,5 h implica μ−λ=2/h e λ=8/h. P(X<6)=1−0,8⁶=0,737856. |
| 4 | Sob M/M/1, λ=1/min e μ=3/min. Restam 0,5 min para fila mais compra. W médio=0,5 min e P(W≤0,5)=1−exp(−1)=63,21%. Chegar a tempo é possível, sem garantia. |
| 5 | λ=3/h, μ=4/h. Lq=2,25, L=3, Wq=0,75 h, W=1 h, P₆=0,04449, ρ=75%, P(W>2 h)=0,13534 e P(Wq>1,5 h)=0,16735. |
| 6 | Com μ=5/h, Wq=0,8 h dá λ=4/h. Lq=3,2, L=4, W=1 h, P(W>1 h)=0,36788 e P(Wq>0,8 h)=0,35946. |
| 7 | λ=2/h, μ=3/h. Para s=1 e 2, respectivamente, ρ=(2/3;1/3), L=(2;0,75), Lq=(4/3;1/12), P₀=(1/3;1/2), P(X>2)=(0,29630;0,05556), Wq=(2/3;1/24) h, W=(1;3/8) h, P(Wq>0,5 h)=(0,40435;0,02256) e P(W>1 h)=(0,36788;0,06552). |
| 8 | λ=40/h, μ=30/h e s=2. Com Wq observado de 1 min, Little dá Lq=0,6667 e L=2, com W=3 min. Esses valores também coincidem com o modelo estacionário M/M/2. |
| 9 | λ=5/h e μ=7/h. Wq com um atendente é 21,43 min. Com dois, Wq=1,253 min. O mínimo é dois. |
| 10 | De ρ=0,75 e Wq=2,5 min, λ=0,9/min e μ=1,2/min. (a) L=3 e W=10/3 min. (b) Para W=2 min, μ=1,4/min. (c) P(X<4)=1−(0,9/1,4)⁴=82,92%; 17,08% é o complemento. (d) μ=0,9/0,15^(1/4)=1,44617/min. (e) Com K=3 e as taxas originais, P(X>2)=P₃=15,43%. |
| 11 | λ=2/dia, μ=4/dia. Cabem três tarefas em espera, portanto P(fila≤3)=P(X≤4)=1−0,5⁵=0,96875. O depósito remoto mantém a fila ilimitada. |
| 12 | λ=10/h, μ=15/h. Ninguém esperando admite um cliente em atendimento. P(fila=0)=P₀+P₁=5/9≈55,56%. 33,33% é P₀. |
| 13 | Com μ=30/h, L=2, W=6 min, Wq=4 min, Lq=4/3, P₀=1/3, P₁=2/9, P₂=4/27, P(X>2)=29,63%, P(Wq>5 min)=28,97% e P(W>7 min)=31,14%. Com ajuda, μ=40/h, L=1, W=3 min, Wq=1,5 min, Lq=0,5, P₀=0,5, P₁=0,25, P₂=0,125, P(X>2)=12,5% e as caudas de tempo são 9,44% e 9,70%. Só a meta de ocupação é atendida com ajuda. |
| 14 | Use μ=20/h por pista de pouso. Com (λ,s)=(10,1), (15,1) e (25,2), os trios (Lq; P(fila≤4); P(Wq≤30 min)) são (0,5000;98,44%;99,66%), (2,2500;82,20%;93,84%) e (0,8013;95,42%;99,97%). O gabarito usa 92,7% no último caso. A condição fila≤4 equivale a X≤6 com duas pistas. (a) e (c) cumprem os três critérios. |
| 15 | Hoje com quatro caixas, o trio (Lq; P(fila≤5); P(Wq≤5 min)) é (0,1739;99,73%;99,9992%). Com λ=3/min e quatro caixas, (1,5283;90,93%;99,6567%). Cinco caixas produzem (0,3542;98,90%;99,9989%) e atendem às três metas. |

## M/M/s/K · 6 exercícios

| Nº | Recalculo e leitura do enunciado |
|---|---|
| 1 | λ=2/min, μ=4/min, s=1, K=5. P₀=0,50794, L=0,90476, Lq=0,41270, P₄=0,03175, W=0,45968 min e Wq=0,20968 min. |
| 2 | λ=1/h, μ=4/3 h⁻¹, s=1, K=4. L=1,44430, Wq=0,86143 h. Ocupado na chegada significa X≥1, com probabilidade 67,22%; lotado significa X=4, com probabilidade 10,37%. Entre admitidos, 63,43% esperam. |
| 3 | λ=15/h, μ=20/h, s=1, K=4. Lq=0,77209, Wq=3,44571 min e P(fila>2)=P₄=10,3713%. |
| 4 | Para duas pistas e três vagas de espera, K=5. Lq=0,10454, Wq=0,42102 min e P(fila>2)=P₅=0,6769%. O trio do gabarito (0,0848;0,3455;0,0182) corresponde ao cálculo com K=4 e P₄, caso em que a fila tem no máximo dois lugares. |
| 5 | λ=1/h, μ=4/3 h⁻¹, s=2 e K=5. L=0,84947, Wq=0,10526 h, P(ambos ocupados)=20,13%, P(lotado)=0,6769% e P(ao menos um ocupado)=54,36%. O trio impresso é consistente com K=4 e probabilidade de lotação, e não com a capacidade 5 do enunciado. |
| 6 | Com três lugares no pátio para espera e um terminal, K=4. Lq=0,77209, L=1,44430, W=0,53714 h e Wq=0,28714 h. Com dois terminais e o mesmo pátio, K=5 e Wq=0,035085 h. O 0,0288 h supõe K=4, ou seja, dois lugares de espera com dois terminais. |

## M/M/s/N · 6 exercícios

| Nº | Recalculo e leitura do enunciado |
|---|---|
| 1 | Use N=10 conforme o parêntese, λ=1/200 por hora e μ=1/10 por hora. P₀=0,53796, Lq=0,29723, L=0,75926, Wq=6,43296 h e W=16,43296 h. Custo em 8 h com mão de obra alocada só enquanto ocupada: 8×[30L+10(1−P₀)]≈R$ 219,19. No turno inteiro, R$ 262,22. |
| 2 | N=6, λ=1/30 por hora por trem e um posto com μ=0,15/h. O gabarito troca unidades e medidas: L=2,19375, Lq=1,34792, P₄=0,13535, W=17,29063 h e Wq=10,62396 h. Se o prazo for da chegada à conclusão, P(W>24 h)≈25,93%, misturando caudas Erlang(n+1, μ) pelos estados vistos na chegada. O tempo médio menor que 24 h permite atrasos individuais. |
| 3 | N=2, λ=0,1/h, μ=0,125/h, s=1. P₀=0,25773, L=1,07216, Lq=0,32990, W=11,55556 h e Wq=3,55556 h. Ocupação=74,23% e disponibilidade por máquina=46,39%. |
| 4 | N=3, λ=1/9 e μ=1/2 por hora. Com um técnico, distribuição de X≈(0,49290;0,32860;0,14604;0,03245), L=0,71805, W=2,832 h e ocupação=50,71%. Com dois técnicos, distribuição≈(0,54607;0,36404;0,08090;0,00899) e L=0,55281. O valor 0,667 é a carga nominal 3λ/μ. |
| 5 | Um mecânico e N=4 dão 3,00829 máquinas operando. Custo de paralisação=R$ 158,67/dia e custo total=R$ 208,67/dia. Dois grupos independentes de N=2 dão custo total≈R$ 221,08/dia. Com os valores informados, um mecânico custa cerca de R$ 12,41/dia a menos. |
| 6 | N=4, λ=0,01/h, μ=0,1/h e s=2. P₀=0,68199, L=0,36773, Lq=0,00450, W=10,12392 h, Wq=0,12392 h. Probabilidade de ao menos um técnico ocupado=31,80%. Ocupação média por técnico=18,16% e disponibilidade de cada máquina=90,81%. O complemento da ocupação por técnico descreve ociosidade do técnico. |

## M/G/1 e prioridades · 7 exercícios

| Nº | Recalculo e leitura do enunciado |
|---|---|
| 1 | Para σ=4,3,2,1,0, com λ=0,2 e μ=0,25, as listas são Lq=(3,2;2,5;2;1,7;1,6), L=(4;3,3;2,8;2,5;2,4), Wq=(16;12,5;10;8,5;8), W=(20;16,5;14;12,5;12). A razão pedida Lq(4)/Lq(0)=2; o gabarito mostra a inversa. Reduções de Lq=(0,7;0,5;0,3;0,1). Com σ=4, μ≈0,301777 para Lq=1,6, um aumento de 0,051777. |
| 2 | Com λ=3/h e μ=4/h, ρ=75% para qualquer σ admissível. Lq=1,125, L=1,875, Wq=0,375 h e W=0,625 h se σ=0. A média de 15 min sozinha deixa as quatro medidas de fila e permanência indeterminadas. |
| 3 | Com Lq=2, λ=3/h, Wq=2/3 h. L e W dependem de μ. Assumindo σ=0, ρ=0,828427 e μ=3,62132/h, então L=2,828427 e W=0,942809 h. |
| 4 | Sem interrupção, λ=(2;10)/h, μ=20/h. Classe 1: (Lq; L; Wq; W)=(0,06667;0,16667;0,03333;0,08333). Classe 2: (0,83333;1,33333;0,08333;0,13333). A relação de esperas é 0,4 e a ocupação em 12 h é 7,2 h. A impressão de Lq₂ como 0,083 viola Little. |
| 5 | Com s=1 e μ=6, as medidas (Lq;L;Wq;W) são (0,41667;0,75000;0,20833;0,37500) e (3,75000;4,25000;1,25000;1,41667). Com s=2 e μ=3, são (0,37879;1,04545;0,18939;0,52273) e (3,40909;4,40909;1,13636;1,46970). Para classe 1, um rápido minimiza W e dois lentos minimizam Wq. |
| 6 | λ=(2;4;2)/dia, μ=10/dia. W em dias é 0,5 para todas sob FCFS, (0,2;0,35;1,1) sem interrupção e (0,125;0,3125;1,25) com retomada. |
| 7 | Do Exemplo 1, λ total=2/h e μ=3/h. Taxas por classe (0,1;0,4;1,5)/h. Wq com retomada para s=1: (0,011494;0,080460;0,866667) h, para s=2: (0,0000926;0,0028906;0,0547786) h. O último valor impresso é 0,05493 h. Sem interrupção, s=1: (0,229885;0,275862;0,800000) h e s=2: (0,028249;0,030817;0,045455) h. Para cada Wq da linha, some 1/3 h para W e multiplique os tempos pela taxa da classe para Lq e L. |

