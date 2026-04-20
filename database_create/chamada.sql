CREATE TABLE chamada (
    id_chamada SERIAL PRIMARY KEY,
    id_turma INT REFERENCES turma(id_turma) ON DELETE CASCADE,
    id_aluno INT REFERENCES aluno(id_aluno) ON DELETE CASCADE,
    presente BOOLEAN NOT NULL DEFAULT FALSE,
    justificativa TEXT,
    data TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER tr_chamada_update_timestamp
BEFORE UPDATE ON chamada
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
