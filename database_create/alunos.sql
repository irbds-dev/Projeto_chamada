CREATE TABLE aluno (
    id_aluno SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(255) NOT NULL,
    id_turma INT REFERENCES turma(id_turma) ON DELETE SET null,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO aluno (nome, cpf, id_turma)
WITH nomes_base AS (
    SELECT unnest(ARRAY[
        'Miguel', 'Arthur', 'Gael', 'Théo', 'Heitor', 'Ravi', 'Davi', 'Bernardo', 'Noah', 'Gabriel',
        'Samuel', 'Pedro', 'Anthony', 'Isaac', 'Benício', 'Lucas', 'Lorenzo', 'Matheus', 'Bento', 'Rafael',
        'Nicolas', 'Guilherme', 'Joaquim', 'Emanuel', 'Felipe', 'Helena', 'Alice', 'Laura', 'Maria Alice', 'Sophia',
        'Manuela', 'Maitê', 'Liz', 'Cecília', 'Isabella', 'Luísa', 'Eloá', 'Ayla', 'Chloe', 'Maya',
        'Lívia', 'Lorena', 'Giovanna', 'Maria Clara', 'Beatriz', 'Mariana', 'Lara', 'Júlia', 'Antonella', 'Emanuelly'
    ]) AS n
),
sobrenomes_base AS (
    SELECT unnest(ARRAY[
        'Silva', 'Santos', 'Oliveira', 'Souza', 'Pereira', 'Ferreira', 'Alves', 'Lima', 'Costa', 'Ribeiro',
        'Martins', 'Carvalho', 'Rodrigues', 'Almeida', 'Lopes', 'Soares', 'Fernandes', 'Vieira', 'Barbosa', 'Rocha',
        'Dias', 'Nascimento', 'Andrade', 'Moreira', 'Nunes', 'Marques', 'Machado', 'Mendes', 'Freitas', 'Cardoso',
        'Ramos', 'Santana', 'Teixeira', 'Guimarães', 'Cunha', 'Castro', 'Moura', 'Cavalcanti', 'Pinto', 'Borges',
        'Melo', 'Araújo', 'Pires', 'Siqueira', 'Duarte', 'Freire', 'Viana', 'Rocha', 'Assis', 'Campelo'
    ]) AS s
),
lista_combinada AS (
    SELECT 
        n.n || ' ' || s.s AS nome_completo,
        row_number() OVER (ORDER BY random()) as rn
    FROM nomes_base n
    CROSS JOIN sobrenomes_base s
)
SELECT 
    lc.nome_completo,
    LPAD(floor(random() * 999)::text, 3, '0') || '.' || 
    LPAD(floor(random() * 999)::text, 3, '0') || '.' || 
    LPAD(floor(random() * 999)::text, 3, '0') || '-' || 
    LPAD(floor(random() * 99)::text, 2, '0') AS cpf,
    t.id_turma
FROM turma t
CROSS JOIN generate_series(1, 5) AS g(num)
JOIN lista_combinada lc ON lc.rn = ((t.id_turma - 1) * 5 + g.num);
