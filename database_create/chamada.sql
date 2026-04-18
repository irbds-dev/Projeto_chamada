CREATE TABLE chamada (
    id_chamada SERIAL PRIMARY KEY,
    id_turma INT REFERENCES turma(id_turma) ON DELETE CASCADE,
    id_aluno INT REFERENCES aluno(id_aluno) ON DELETE CASCADE,
    presente BOOLEAN NOT NULL DEFAULT FALSE,
    justificativa TEXT,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW() -- Campo que será auto-atualizado
);
