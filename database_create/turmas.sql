CREATE TABLE turma (
    id_turma SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    periodo VARCHAR(100) NOT NULL,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO turma (nome, periodo)
SELECT 
    n.ano || 'º ano ' || x.letra AS nome,
    p.periodo_nome AS periodo
FROM 
    generate_series(1, 3) AS n(ano)
CROSS JOIN 
    (VALUES ('A'), ('B'), ('C')) AS x(letra)
CROSS JOIN 
    (VALUES ('Diurno'), ('Noturno')) AS p(periodo_nome)
ORDER BY 
    n.ano, x.letra, p.periodo_nome;
