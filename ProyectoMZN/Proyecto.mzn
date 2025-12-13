% ============================================================
% Proyecto.mzn - Minimización de Polarización
% Versión compatible con Gurobi (MIP)
% ============================================================

% ---------- PARÁMETROS DE ENTRADA ----------
int: n;                          % Número total de personas
int: m;                          % Número de opiniones posibles
array[1..m] of int: p;           % Distribución inicial por opinión
array[1..m] of float: v;         % Valores de cada opinión (0-1)
array[1..m, 1..3] of int: s;     % Personas por (opinión, resistencia)
float: ct;                       % Costo total máximo
int: maxMovs;                    % Movimientos máximos

% ---------- ESCALADO ----------
int: ESCALA = 1000;
array[1..m] of int: v_scaled =
    [round(v[i] * int2float(ESCALA)) | i in 1..m];
int: ct_scaled = round(ct * int2float(ESCALA));

% ---------- VARIABLES DE DECISIÓN ----------
% x[i,j,k] = personas con resistencia k que pasan de opinión i a j
array[1..m, 1..m, 1..3] of var 0..n: x;

% ---------- RESTRICCIONES BÁSICAS ----------

% 1. No mover más personas de las disponibles
constraint forall(i in 1..m, k in 1..3)(
    sum(j in 1..m)(x[i,j,k]) <= s[i,k]
);

% 2. No mover a la misma opinión
constraint forall(i in 1..m, k in 1..3)(
    x[i,i,k] = 0
);

% 3. Límite de movimientos totales
constraint sum(i in 1..m, j in 1..m, k in 1..3)(
    abs(i - j) * x[i,j,k]
) <= maxMovs;

% ---------- COSTO TOTAL (ESCALADO) ----------
var 0..ct_scaled: costoTotal_scaled =
    sum(i in 1..m, j in 1..m, k in 1..3)(
        abs(i - j) * x[i,j,k] *
        (if k == 1 then ESCALA
         elseif k == 2 then (3 * ESCALA) div 2
         else 2 * ESCALA endif)
    );

constraint costoTotal_scaled <= ct_scaled;

% ---------- DISTRIBUCIÓN FINAL ----------
array[1..m] of var 0..n: p_final;

constraint forall(j in 1..m)(
    p_final[j] =
        sum(i in 1..m, k in 1..3)(x[i,j,k]) +
        sum(k in 1..3)(s[j,k]) -
        sum(t in 1..m, k in 1..3)(x[j,t,k])
);

constraint sum(j in 1..m)(p_final[j]) = n;

% ---------- ARRAY DE PERSONAS ----------
array[1..n] of var 1..m: persona_opinion;

constraint forall(persona in 1..n)(
    exists(opinion in 1..m)(
        persona > sum(op in 1..opinion-1)(p_final[op]) /\
        persona <= sum(op in 1..opinion)(p_final[op]) /\
        persona_opinion[persona] = opinion
    )
);

array[1..n] of var min(v_scaled)..max(v_scaled): valor_persona_scaled;

constraint forall(i in 1..n)(
    valor_persona_scaled[i] = v_scaled[persona_opinion[i]]
);

% ---------- MEDIANA (ESCALADA, ACOTADA) ----------
var min(v_scaled)..max(v_scaled): mediana_scaled;

int: pos_baja = n div 2;
int: pos_alta = (n div 2) + 1;

constraint
if n mod 2 == 1 then
    exists(idx in 1..n)(
        sum(j in 1..n)(valor_persona_scaled[j] < valor_persona_scaled[idx]) <= pos_baja /\
        sum(j in 1..n)(valor_persona_scaled[j] > valor_persona_scaled[idx]) <= (n - pos_alta) /\
        mediana_scaled = valor_persona_scaled[idx]
    )
else
    exists(idx1 in 1..n, idx2 in 1..n)(
        sum(j in 1..n)(valor_persona_scaled[j] < valor_persona_scaled[idx1]) <= pos_baja - 1 /\
        sum(j in 1..n)(valor_persona_scaled[j] > valor_persona_scaled[idx1]) <= (n - pos_baja) /\
        sum(j in 1..n)(valor_persona_scaled[j] < valor_persona_scaled[idx2]) <= pos_alta - 1 /\
        sum(j in 1..n)(valor_persona_scaled[j] > valor_persona_scaled[idx2]) <= (n - pos_alta) /\
        mediana_scaled =
            (valor_persona_scaled[idx1] + valor_persona_scaled[idx2]) div 2
    )
endif;

% ---------- POLARIZACIÓN (ESCALADA, ACOTADA) ----------
var 0..(n * (max(v_scaled) - min(v_scaled))): polarizacion_scaled =
    sum(j in 1..m)(
        p_final[j] * abs(v_scaled[j] - mediana_scaled)
    );

% ---------- FUNCIÓN OBJETIVO ----------
solve minimize polarizacion_scaled;

% ---------- MOVIMIENTOS TOTALES ----------
var int: movimientos_totales =
    sum(i in 1..m, j in 1..m, k in 1..3)(
        abs(i - j) * x[i,j,k]
    );

% ---------- SALIDA ----------
output [
    "{\n",
    "  \"polarizacion\": ", show(polarizacion_scaled / int2float(ESCALA)), ",\n",
    "  \"costo_usado\": ", show(costoTotal_scaled / int2float(ESCALA)), ",\n",
    "  \"movimientos_usados\": ", show(movimientos_totales), ",\n",
    "  \"p_final\": [", join(", ", [show(p_final[j]) | j in 1..m]), "],\n",
    "  \"mediana\": ", show(mediana_scaled / int2float(ESCALA)), "\n",
    "}\n"
];
